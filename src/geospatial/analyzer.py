import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from folium.plugins import HeatMap, MarkerCluster
from sklearn.neighbors import KernelDensity
import pyarrow

from src.analysis.profiler import DataProfiler


class GeoAnalyzer(DataProfiler):
    """
    Extends DataProfiler with geographic analysis capabilities for crime incident data.
    Provides methods for geospatial analysis including mapping, hotspot identification,
    and spatial distribution analysis.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the GeoAnalyzer with a pandas DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing crime incident data with coordinate columns.
        """
        super().__init__(df)
        self.gdf = None  # Will hold GeoDataFrame after initialization

    def initialize_geodataframe(
        self, lat_col: str = "latitude", lon_col: str = "longitude"
    ) -> gpd.GeoDataFrame:
        """
        Convert DataFrame with coordinate columns to a GeoDataFrame.

        Args:
            lat_col (str): Name of latitude column. Defaults to 'latitude'.
            lon_col (str): Name of longitude column. Defaults to 'longitude'.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame with geometry column.

        Raises:
            ValueError: If coordinate columns not found or invalid.
        """
        if lat_col not in self.df.columns or lon_col not in self.df.columns:
            raise ValueError(f"Columns '{lat_col}' and/or '{lon_col}' not found.")

        # Validate coordinates
        self.validate_coordinates(self.df, lat_col, lon_col)

        # Create geometry column from coordinates
        geometry = gpd.points_from_xy(self.df[lon_col], self.df[lat_col])

        # Create GeoDataFrame
        self.gdf = gpd.GeoDataFrame(self.df, geometry=geometry, crs="EPSG:4326")

        return self.gdf

    def validate_coordinates(
        self, df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude"
    ) -> bool:
        """
        Validate that coordinate values are within reasonable ranges.

        Args:
            df (pd.DataFrame): DataFrame to validate.
            lat_col (str): Name of latitude column. Defaults to 'latitude'.
            lon_col (str): Name of longitude column. Defaults to 'longitude'.

        Returns:
            bool: True if all coordinates are valid.

        Raises:
            ValueError: If coordinates are out of valid ranges.
        """
        # Check latitude range (-90 to 90)
        invalid_lat = (df[lat_col] < -90) | (df[lat_col] > 90)
        if invalid_lat.any():
            raise ValueError(
                f"Invalid latitude values found. Valid range: -90 to 90. "
                f"Found: {df[invalid_lat][lat_col].min()} to {df[invalid_lat][lat_col].max()}"
            )

        # Check longitude range (-180 to 180)
        invalid_lon = (df[lon_col] < -180) | (df[lon_col] > 180)
        if invalid_lon.any():
            raise ValueError(
                f"Invalid longitude values found. Valid range: -180 to 180. "
                f"Found: {df[invalid_lon][lon_col].min()} to {df[invalid_lon][lon_col].max()}"
            )

        return True

    def create_interactive_map(
        self,
        lat_col: str = "latitude",
        lon_col: str = "longitude",
        crime_type_col: str = None,
        output_file: str = "crime_map.html",
    ) -> folium.Map:
        """
        Generate an interactive HTML map with crime markers.

        Args:
            lat_col (str): Latitude column name. Defaults to 'latitude'.
            lon_col (str): Longitude column name. Defaults to 'longitude'.
            crime_type_col (str): Column to use for marker colors. Defaults to None.
            output_file (str): Output HTML file path. Defaults to 'crime_map.html'.

        Returns:
            folium.Map: Folium map object.
        """
        if self.gdf is None:
            self.initialize_geodataframe(lat_col, lon_col)

        # Get Philadelphia center coordinates
        phl_center = [39.9526, -75.1652]
        map_obj = folium.Map(location=phl_center, zoom_start=11)

        # Add marker cluster
        marker_cluster = MarkerCluster().add_to(map_obj)

        # Add markers for each incident
        for idx, row in self.gdf.iterrows():
            popup_text = f"Crime: {row.get('ucr_general', 'Unknown')}"
            if crime_type_col and crime_type_col in row:
                popup_text = f"{row[crime_type_col]}"

            color = "blue"
            if crime_type_col and crime_type_col in row:
                from src.geospatial.utils import get_marker_color

                color = get_marker_color(row[crime_type_col])

            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=5,
                popup=popup_text,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
            ).add_to(marker_cluster)

        # Save map
        map_obj.save(output_file)
        return map_obj

    def identify_hotspots(
        self,
        lat_col: str = "latitude",
        lon_col: str = "longitude",
        bandwidth: float = 0.01,
        grid_size: int = 50,
    ) -> dict:
        """
        Use kernel density estimation to identify crime hotspots.

        Args:
            lat_col (str): Latitude column name. Defaults to 'latitude'.
            lon_col (str): Longitude column name. Defaults to 'longitude'.
            bandwidth (float): Bandwidth for KDE. Defaults to 0.01.
            grid_size (int): Grid size for heatmap. Defaults to 50.

        Returns:
            dict: Dictionary with hotspot information including grid coordinates and density values.
        """
        if self.gdf is None:
            self.initialize_geodataframe(lat_col, lon_col)

        # Extract coordinates
        coords = self.gdf[[lon_col, lat_col]].values

        # Fit KDE model
        kde = KernelDensity(bandwidth=bandwidth)
        kde.fit(coords)

        # Create grid for prediction
        lon_min, lon_max = coords[:, 0].min(), coords[:, 0].max()
        lat_min, lat_max = coords[:, 1].min(), coords[:, 1].max()

        lon_grid = np.linspace(lon_min, lon_max, grid_size)
        lat_grid = np.linspace(lat_min, lat_max, grid_size)
        lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)

        # Evaluate density on grid
        grid_coords = np.column_stack([lon_mesh.ravel(), lat_mesh.ravel()])
        density = np.exp(kde.score_samples(grid_coords))
        density = density.reshape(lon_mesh.shape)

        # Identify top hotspots (cells with highest density)
        hotspot_indices = np.argsort(density.ravel())[-10:]  # Top 10
        hotspots = []
        for idx in hotspot_indices:
            lat_idx, lon_idx = np.unravel_index(idx, density.shape)
            hotspots.append(
                {
                    "latitude": lat_grid[lat_idx],
                    "longitude": lon_grid[lon_idx],
                    "density": float(density[lat_idx, lon_idx]),
                }
            )

        return {
            "hotspots": hotspots,
            "grid": {
                "lat_grid": lat_grid.tolist(),
                "lon_grid": lon_grid.tolist(),
                "density": density.tolist(),
            },
        }

    def analyze_spatial_distribution(
        self, lat_col: str = "latitude", lon_col: str = "longitude"
    ) -> dict:
        """
        Analyze geographic patterns of crime incidents.

        Args:
            lat_col (str): Latitude column name. Defaults to 'latitude'.
            lon_col (str): Longitude column name. Defaults to 'longitude'.

        Returns:
            dict: Dictionary with spatial distribution statistics.
        """
        if self.gdf is None:
            self.initialize_geodataframe(lat_col, lon_col)

        coords = self.gdf[[lon_col, lat_col]].values

        return {
            "total_incidents": len(self.gdf),
            "latitude_range": {
                "min": float(coords[:, 1].min()),
                "max": float(coords[:, 1].max()),
                "mean": float(coords[:, 1].mean()),
                "std": float(coords[:, 1].std()),
            },
            "longitude_range": {
                "min": float(coords[:, 0].min()),
                "max": float(coords[:, 0].max()),
                "mean": float(coords[:, 0].mean()),
                "std": float(coords[:, 0].std()),
            },
            "geographic_spread": {
                "lat_span": float(coords[:, 1].max() - coords[:, 1].min()),
                "lon_span": float(coords[:, 0].max() - coords[:, 0].min()),
            },
        }

    def compare_area_density(
        self,
        area_col: str,
        lat_col: str = "latitude",
        lon_col: str = "longitude",
    ) -> pd.DataFrame:
        """
        Compare crime density across different geographic areas.

        Args:
            area_col (str): Column name for geographic areas (e.g., 'district', 'zone').
            lat_col (str): Latitude column name. Defaults to 'latitude'.
            lon_col (str): Longitude column name. Defaults to 'longitude'.

        Returns:
            pd.DataFrame: DataFrame with area density statistics.

        Raises:
            ValueError: If area_col not found.
        """
        if area_col not in self.df.columns:
            raise ValueError(f"Column '{area_col}' not found.")

        if self.gdf is None:
            self.initialize_geodataframe(lat_col, lon_col)

        # Calculate density metrics per area
        area_stats = []
        for area in self.gdf[area_col].unique():
            area_data = self.gdf[self.gdf[area_col] == area]
            coords = area_data[[lon_col, lat_col]].values

            # Calculate bounding box area in degrees (rough approximation)
            lat_span = coords[:, 1].max() - coords[:, 1].min()
            lon_span = coords[:, 0].max() - coords[:, 0].min()
            bounding_box_area = lat_span * lon_span

            density = len(area_data) / bounding_box_area if bounding_box_area > 0 else 0

            area_stats.append(
                {
                    "area": area,
                    "incident_count": len(area_data),
                    "density_per_sq_degree": float(density),
                    "lat_span": float(lat_span),
                    "lon_span": float(lon_span),
                }
            )

        return pd.DataFrame(area_stats).sort_values(
            "density_per_sq_degree", ascending=False
        )
