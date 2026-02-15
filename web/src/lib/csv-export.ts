/**
 * CSV and JSON export utilities with proper encoding and metadata support
 */

/**
 * Downloads data as a JSON file with pretty formatting
 * @param data Array of data to export
 * @param filename Name of the file (without extension)
 */
export function downloadAsJson(data: unknown[], filename: string): void {
  const datePrefix = new Date().toISOString().split('T')[0];
  const fullFilename = filename.startsWith(datePrefix) ? filename : `${datePrefix}-${filename}`;
  
  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${fullFilename}.json`;
  
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  
  URL.revokeObjectURL(url);
}

/**
 * Escapes a CSV field value by:
 * - Wrapping in quotes if it contains comma, quote, or newline
 * - Doubling internal quotes
 * @param value The value to escape
 */
function escapeCsvValue(value: unknown): string {
  if (value === null || value === undefined) {
    return '';
  }
  
  const str = String(value);
  
  // Check if value needs escaping
  if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
    // Double any internal quotes and wrap in quotes
    return `"${str.replace(/"/g, '""')}"`;
  }
  
  return str;
}

/**
 * Downloads data as a CSV file with UTF-8 BOM for Excel compatibility
 * @param data Array of objects to export
 * @param filename Name of the file (without extension)
 */
export function downloadAsCsv(data: Record<string, unknown>[], filename: string): void {
  if (!data || data.length === 0) {
    console.warn('No data to export');
    return;
  }
  
  const datePrefix = new Date().toISOString().split('T')[0];
  const fullFilename = filename.startsWith(datePrefix) ? filename : `${datePrefix}-${filename}`;
  
  // Extract headers from first object
  const headers = Object.keys(data[0]);
  
  // Build CSV content
  const headerRow = headers.map(escapeCsvValue).join(',');
  const dataRows = data.map(row => 
    headers.map(header => escapeCsvValue(row[header])).join(',')
  );
  
  const csvContent = [headerRow, ...dataRows].join('\n');
  
  // Add UTF-8 BOM for Excel compatibility
  const csvWithBom = '\uFEFF' + csvContent;
  
  const blob = new Blob([csvWithBom], { type: 'text/csv;charset=utf-8' });
  
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${fullFilename}.csv`;
  
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  
  URL.revokeObjectURL(url);
}
