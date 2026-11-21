# Kyle Tech Testing — Showcase Website

A build-free, responsive marketing showcase for an emerging independent hardware reviewer. It uses only local HTML, CSS, JavaScript, SVG, and PNG assets. No analytics, tracking, runtime package, external font request, backend, or third-party JavaScript is used.

## Preview on Windows

Open PowerShell in this directory and run:

```powershell
python -m http.server 8080 --bind 127.0.0.1
```

Open <http://127.0.0.1:8080> in a browser. Keep that PowerShell window open while previewing. Press **Ctrl+C** in the same window to stop the local server. The site does not run a hardware test or contact the GPU.

The interactive chart reads the two included CSV evidence files over HTTP. A source-checked bundled fallback also supports browsers that block CSV fetches on `file://` previews, which explains why the earlier direct-file screenshot could show an empty chart. HTTP remains the recommended way to preview the complete site.

The static dark-theme PNG charts are generated from the same preserved CSVs. To regenerate them locally, run `python .\generate_static_charts.py` (Matplotlib is needed only for regeneration, not to preview or host the site).

## Pages

- `index.html` — overview, verified system specifications, measured findings, interactive data visualization, report library, and collaboration call to action.
- `evaluation.html` — RTX 4070 evaluation summary, interactive CSV chart, static source charts, sample statistics, evidence downloads, and limitations.
- `lab.html` — documented primary test system separated from owner-reported, unverified additional equipment.
- `reports.html` — published evaluation, report-format demonstrations, and explicitly planned test tracks.
- `methods.html` — evaluation principles and clear status of present capabilities versus planned work.
- `sample-reports.html` and `demo-*.html` — report layouts and three separate demonstrations; these are **not completed product evaluations** and contain no test findings.
- `collaborate.html` — manufacturer-specific collaboration process, possible deliverables, sample terms, editorial boundaries, and direct contact.
- `research-hub.html` — searchable source-linked research index and an interactive chart of a fixed Blender Open Data GPU comparison snapshot.
- `gpu-research.html`, `mini-pc-guide.html`, `processor-guide.html`, and `windows-compatibility.html` — source-labeled GPU data interpretation, mini PC evaluation guide, Intel N100 specification guide, and Windows peripheral/network compatibility methodology.
- `research-sources.md` — source-by-source reuse basis, collection date, caveats, and excluded candidate data sources.

The supplied portfolio contained charts and a vector illustration, but no photograph of the tested RTX 4070 card. The hero therefore uses an original generated, generic GPU concept rendering; it is visibly labeled as illustrative and never presented as test evidence or as the specific card tested. The charts remain the actual evidence visuals.

## What the evidence says

The actual source is the two included 59-row GPU telemetry captures from the existing [hardware-testing portfolio](https://github.com/Inksane12/hardware-testing-portfolio). A five-minute idle-labeled baseline and a separate five-minute mixed ComfyUI capture show sampled peaks of 64 °C, 100% GPU utilization, 11,571 MiB VRAM, and 184.81 W GPU-reported power in the mixed capture. The complete capture includes idle periods. These values do not establish generation speed, output quality, sustained-load behavior, or an endurance result.

Two ERNIE Image Turbo generations were reported by the operator; no screenshot, output, or application history was supplied to independently verify completion. This is disclosed on the evaluation page. The included CSVs preserve timestamps and numeric GPU telemetry. See `evidence/SHA256SUMS.txt` for their hashes.

The only completed review displayed is the short RTX 4070 telemetry evaluation. Windows peripheral, gaming, networking, and mini-PC sections describe areas or procedures that have not yet been tested. The reported non-GPU equipment is not independently verified.

## Hardware Research Hub

The research section is separate from hands-on evaluations. Its chart uses seven Blender Open Data GPU median rows collected 2026-11-21 from the Blender 4.4.0 + OptiX query. Blender's dataset download page states CC0 licensing. The score unit is an estimate of Cycles samples per minute; the chart includes community record counts and prominently labels the values as third-party data. The base RTX 4070 is omitted from that chart because its row was not verified in this exact filtered snapshot. No Open GPU Benchmarks scores are used: the inspected page identified displayed values as synthetic scaffold data.

The mini PC, processor, and Windows guides use official Intel and Microsoft references for narrow factual specifications and troubleshooting context. They summarize in original wording, link to the source, and do not republish vendor imagery or bulk proprietary data. The guides are not product test reports.

## Free GitHub Pages deployment

This folder is a standalone static-site source directory. Nothing is published by previewing or validating it.

1. Create a **new** public GitHub repository (for example, `kyle-tech-testing-showcase`). Do not overwrite the existing hardware-testing evidence repository.
2. In PowerShell opened in this folder, run the commands below after replacing the URL with the new repository's HTTPS URL:

   ```powershell
   git init -b main
   git add .
   git status --short
   git commit -m "Build Kyle Tech Testing showcase website"
   git remote add origin https://github.com/OWNER/kyle-tech-testing-showcase.git
   git push -u origin main
   ```

   Review `git status --short` and the staged file list before committing. `.gitignore` excludes local configuration, credentials, machine-local files, temporary data, logs, and private evidence.
3. On GitHub, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/(root)`, then save.
4. Wait for the Pages deployment to complete. Confirm the published homepage, all site pages, CSV downloads, charts, mobile layout, and contact link. The expected address is `https://OWNER.github.io/kyle-tech-testing-showcase/`; use the exact address shown by GitHub.
5. Only after owner review and approval, share that verified link in manufacturer correspondence. Do not claim social reach, audience analytics, sponsorships, endorsements, or completed product tests that are not documented.

GitHub Pages makes the repository contents public. Review the complete file list before the first push. The separate site contains the already-published GPU CSV telemetry, derived charts, public-facing technical copy, and this deployment guide; it contains no private machine logs, Gmail data, tracker, credentials, or user account directories.

## Validation

Run the included no-dependency structural and evidence checks:

```powershell
python .\validate_site.py
node .\test_chart_runtime.cjs
node .\test_research_runtime.cjs
```

The Node runtime smoke tests use only built-in Node modules and verify the measured telemetry chart, capture/metric switches, UTC sample tooltip, and research chart/filter behavior. The Python checks verify local page links and assets, CSV shape/sample counts and source hashes, report statistics, the third-party snapshot schema and disclosures, page structure, responsive/accessibility declarations, no remote code/assets, and public-content privacy patterns. They do not replace a visual review in current desktop and mobile browsers before publication.

If either source CSV is intentionally updated, regenerate the `file://` fallback with `python .\generate_chart_fallback.py`, then run both validation commands. The Python validator checks every fallback timestamp and plotted value against the preserved CSVs.

## Contact

[kyle.techtesting@gmail.com](mailto:kyle.techtesting@gmail.com)
