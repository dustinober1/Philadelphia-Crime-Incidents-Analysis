```chatagent
---
description: 'Refresh interactive Plotly visualizations, produce static fallbacks, and run visual-diff tests to detect visual regressions.'
tools:
  - plotly
  - kaleido
  - pillow
  - imagehash
  - pytest
---
Purpose
- Keep the dashboard and report visuals up-to-date by re-rendering interactive Plotly figures, writing static PNG/SVG fallbacks, and running visual-diff checks against approved baselines.

When to use
- Run on push to `dashboard/` or `analysis/` files that change visual output.
- Run nightly to detect drift caused by upstream data changes.

Behavior
- Load a target plotting function (module:function) that returns a Plotly `Figure` and save both interactive JSON/HTML and static PNG via `kaleido`.
- If a baseline image exists, compute perceptual hash (via `imagehash`) and report difference; fail CI if difference > threshold.
- Save outputs to `reports/visuals/{figure_name}/{YYYY-MM-DD}/` and record metadata including renderer versions.

CI integration
- Provide a GitHub Actions job that runs `python infra/visualize.py --target dashboard.components.plot:make_choropleth --out reports/visuals` and fails when visual diff exceeds allowed tolerance.

Developer notes
- Keep baseline images under `tests/baselines/visuals/` and update them intentionally when approved.
- Use `kaleido` for headless static exports; ensure it's in `requirements.txt`.

Example command
```
python infra/visualize.py --target dashboard.pages.spatial:build_choropleth --out-dir reports/visuals --baseline tests/baselines/visuals/spatial_choropleth.png
```

End of agent spec.
```
