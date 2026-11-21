# Research source register

Research pages and data snapshot added 2026-11-21. Sources are checked for what is actually reused. Benchmark measurements are reproduced only from sources that explicitly permit reuse. Manufacturer specifications and Microsoft troubleshooting information are linked and summarized in original wording; source page text, images, and graphics are not republished.

| Source | Material used | License / reuse basis | Scope and caveats | Collected |
|---|---|---|---|---|
| [Blender Open Data query: Blender 4.4.0, OptiX, grouped by device](https://opendata.blender.org/benchmarks/query/?blender_version=4.4.0&compute_type=OPTIX&group_by=device_name) | Seven GPU median scores and benchmark counts in `data/blender-4.4.0-optix-gpu.csv`; displayed in the research hub | Blender's [daily dataset download page](https://opendata.blender.org/download/) states the dataset is CC0 (Creative Commons Zero). Reuse with source attribution is permitted; attribution is provided as good practice. | Community submissions; median Cycles samples/minute estimate, Blender 4.4.0 and OptiX. Different systems and submitters; benchmark counts are submissions, not labs or unique owners. Base RTX 4070 omitted because its row could not be verified in this exact filtered snapshot. | 2026-11-21 |
| [Blender Open Data methodology](https://opendata.blender.org/about/) | Original explanation of the score and dataset limits | Linked and summarized in original wording; no dataset rows from this page. Dataset license statement is on the download page above. | Score aggregates Cycles benchmark scenes; system context varies. | 2026-11-21 |
| [Intel ARK: Processor N100 specifications](https://www.intel.com/content/www/us/en/products/sku/231803/intel-processor-n100-6m-cache-up-to-3-40-ghz/specifications.html) | Four cores/four threads, up to 3.40 GHz, 6 MB cache, 6 W TDP | Manufacturer specification page. Only factual specification values are summarized with a direct source link; no table dump, images or graphics copied. No explicit open data license asserted. | CPU SKU-level specs do not describe a mini PC's sustained behavior or full system performance. | 2026-11-21 |
| [Microsoft Bluetooth connection troubleshooting](https://support.microsoft.com/en-us/windows/hardware/bluetooth/troubleshoot-bluetooth-not-connecting-in-windows) and [driver guidance](https://support.microsoft.com/en-us/windows/hardware/bluetooth/update-bluetooth-drivers-in-windows) | Original compatibility checklist summary with links | No content or image republished; original wording summarizes support guidance. No open reuse license asserted. | Version-specific guidance may change; readers should follow current Microsoft and device-maker instructions. | 2026-11-21 |
| [Open GPU Benchmarks](https://opengpubenchmarks.com/) | Evaluated as a candidate source; **no scores reused** | Site states CC BY 4.0 on its [license page](https://opengpubenchmarks.com/license/). | The inspected page itself said synthetic scaffold data was displayed and not published benchmark results; excluded from charts and analysis. | 2026-11-21 |

## Attribution shown with data

The hub marks the chart as **THIRD-PARTY DATA** and names Blender Open Data, exact application version, compute backend, score unit, source link, sample count and collection date. The GPU article explains that the rows are community medians and not a controlled Kyle Tech Testing test. The source CSV preserves the filtering metadata per row.

## Exclusions

- No copyrighted reviewer charts, product photographs or article text are reused.
- No benchmark results are taken from Open GPU Benchmarks because the inspected result page exposed synthetic scaffold data.
- No public result is merged with the site's first-party RTX 4070 telemetry.
- No benchmark claim is made for an individual mini PC, laptop, peripheral or router.
