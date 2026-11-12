# Australian Resources and Energy Explorer — constrained build plan

> **Planning record:** This document preserves the original time-boxed concept.
> The delivered MVP differs in two intentional ways: it uses a native Power BI
> Shape Map instead of OKViz Synoptic Panel so the public embed works, and it
> omits the historical export trend after the REQ workbook exceeded the MVP's
> data-preparation budget. See the root README for the implemented scope.

## Scope

Build one polished 16:9 Power BI page around two OKViz Synoptic Panel visuals:

- an Australian state/territory selector;
- a seven-shape commodity selector: iron ore, coal, gold and silver, lithium,
  copper and base metals, bauxite, and nickel;
- mine count, selected-region count, and leading-commodity cards;
- a ranked bar chart and mine detail table;
- one annual export trend sourced from the REQ workbook.

The spatial fact is a mine site, not production tonnage. Labels must say
"operating mines" and must not imply that mine count measures output or value.

Leave out mining regions, individual mine polygons, live refresh, Fabric,
incremental refresh, forecasting, drill-through pages, tooltips pages, and more
than seven commodity shapes. LNG and oil do not belong on the mine-site panel.

## Timebox and done checks

| Block | Time | Done check | Main time risk |
|---|---:|---|---|
| Validate and clean data | 60 min | Re-runnable script writes clean mine CSV; REQ table selected | Fighting the 47-sheet workbook |
| Model | 35 min | Small star schema filters correctly in both directions | Many-to-many over-engineering |
| Synoptic SVGs | 75 min | Both panels select and cross-filter | SVG IDs not matching data values |
| Report page | 75 min | Cards, rank, trend and table respond correctly | Formatting too early |
| QA and polish | 35 min | Labels, empty states, attribution and interactions checked | Custom visual behaviour |
| Package | 60 min | README, diagram, dictionary, case study and demo script committed | Video retakes |

Total: 5 hours 40 minutes. If the REQ extraction exceeds 25 minutes, replace the
trend with a state-by-commodity ranked view and list historical export trends as
future work.

## Data sources

### Geoscience Australia — Australian Operating Mines Map 2025

- Contents: operating-mine name, state, coordinates, status and publisher
  commodity group; the downloaded layer currently contains 347 records.
- Format: ArcGIS feature service supporting JSON and GeoJSON; downloadable map
  data is also available.
- Update frequency: annual.
- Licence: Creative Commons Attribution 4.0 International.
- Ingestion: HTTP GET from the official ArcGIS layer, retain the response in
  `data/raw`, validate and flatten it to `data/clean` with Python.
- Quality: structurally clean, but commodity groups are broad and polymetallic.

This is the easiest and primary source.

### Office of the Chief Economist — REQ September 2026 historical data

- Contents: Australian and global annual, quarterly and monthly production,
  trade, prices and economic indicators across 47 workbook sheets.
- Format: XLSX; no API identified on the publication page.
- Update frequency: quarterly publication cycle.
- Licence: CC BY 4.0 except specified logos, third-party content, trademarks and
  the Commonwealth Coat of Arms. Attribution wording is included in `About`.
- Ingestion: import only the selected annual export-value table and unpivot year
  columns in Power Query. Do not build a general workbook parser in this MVP.
- Quality: authoritative but messy for automation because it is presentation-
  formatted and extremely wide.

## Lightweight architecture

`official source -> data/raw -> Python validation/standardisation -> data/clean
-> Power Query -> star schema -> Power BI report`

Tools: Python standard library, Power Query, Power BI Desktop/PBIP, Git and
GitHub. The data-quality gate checks required fields, unique mine IDs, recognised
state codes and coordinate ranges.

## Model

- `FactMine`: one row per operating mine (`MineKey`).
- `DimRegion`: one row per state/territory (`RegionKey`, exact `RegionName`).
- `DimCommodity`: one row per reporting commodity (`CommodityKey`, exact
  `CommodityName`, display order and colour).
- `FactExportAnnual`: one row per commodity and financial/calendar year for the
  single chosen REQ measure.
- `DimDate`: one row per reporting year used by the export trend.

Use single-direction one-to-many relationships from dimensions to facts. The
mine fact itself is the region-to-commodity bridge, so no bidirectional or
many-to-many relationship is required. The state SVG region names must match
`DimRegion[RegionName]` exactly; commodity SVG shape names must match
`DimCommodity[CommodityName]` exactly.

## Synoptic panels

Use an openly licensed Australian states/territories SVG from an authoritative
government source or create the simplified outlines from an open boundary file.
Preserve attribution and verify the asset licence before committing it. Remove
tiny offshore shapes and excessive vertices in Inkscape, then assign human-
readable SVG IDs/names that exactly match the dimension.

Build the commodity panel directly in Inkscape from seven simple geometric
tiles with text/icon cues. Original geometry avoids icon-licensing ambiguity.
Common failures are duplicate IDs, nested groups receiving the ID instead of
the selectable path, unsupported SVG effects, and spelling/case mismatches.

## Page design and measures

Layout: title/filter strip; state panel left; commodity panel centre; KPI cards
top-right; ranking and annual trend across the lower middle; compact mine table
at the bottom/right. Use edit interactions so selecting either Synoptic Panel
filters the other panel plus all supporting visuals.

Measures: `[Operating Mines]`, `[Regions Selected]`, `[Commodity Rank]`,
`[Top Commodity]`, `[Export Value]`, and `[Export YoY %]`.

## Highest-value advanced features

1. PBIP with PBIR/TMDL and Git history (15–20 minutes of setup): directly useful
   evidence for BI engineering and controlled deployment discussions.
2. Executable data-quality checks (15 minutes): demonstrates fail-fast pipeline
   thinking and gives a concrete interview example.

Future work: Fabric pipeline/lakehouse, CI validation, incremental refresh,
deployment pipelines, detailed mining regions, historical mine status and APIs.

## Last-hour packaging

README: problem, screenshot/GIF, insights, architecture, data sources/licences,
reproduction steps, model, quality checks, limitations and future work.

Architecture diagram: source -> raw -> validation/clean -> Power Query -> model
-> report -> Publish to web. Data dictionary: field, type, grain, definition and
source. Case study: context, constraints, decisions, result and lessons.

Two-minute demo: 0:00 problem; 0:15 architecture; 0:35 select WA; 0:55 select
lithium; 1:15 show trend/ranking/table; 1:35 show PBIP, validation and licence;
1:55 close with limitations and next step.

## Interview questions and evidence

1. How did you control scope? Point to the timebox and cuts.
2. How did you make the pipeline reproducible? Run `scripts/prepare_mines.py`.
3. Why this model? Show dimension-to-fact filtering and avoidance of ambiguous
   bidirectional relationships.
4. How did you assure quality? Show assertions and a deliberate failing example.
5. What would productionisation require? Discuss orchestration, monitoring,
   secrets, CI/CD, refresh ownership and Fabric without claiming the MVP has it.

## First 30 minutes

1. Run the mine preparation script and inspect counts.
2. Create a blank Power BI file and save it as PBIP with PBIR and TMDL.
3. Import `data/clean/operating_mines.csv`.
4. Create region and commodity dimensions by reference in Power Query.
5. Confirm exact display names before editing either SVG.

## Risks and cut order

1. Synoptic SVG setup consumes the build: use states only and simple commodity
   tiles; do not attempt mining regions.
2. REQ workbook extraction consumes the build: cut the time trend first.
3. Custom-visual behaviour differs after publishing: test Publish to web early;
   if necessary keep one Synoptic Panel and replace the other with native tiles.

