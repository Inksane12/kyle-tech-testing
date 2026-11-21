#!/usr/bin/env python3
"""No-dependency local checks for the Kyle Tech Testing static showcase."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PAGES = ("index.html", "evaluation.html", "methods.html", "sample-reports.html", "collaborate.html", "lab.html", "reports.html", "demo-mini-pc.html", "demo-peripheral.html", "demo-networking.html", "research-hub.html", "gpu-research.html", "mini-pc-guide.html", "processor-guide.html", "windows-compatibility.html")
EXPECTED = {
    "idle.csv": {"temperature_c": ("30.66", "32.00"), "utilization_pct": ("1.03", "35.00"), "memory_used_mib": ("1687.46", "1815.00"), "power_w": ("9.51", "23.64")},
    "mixed-comfyui.csv": {"temperature_c": ("42.44", "64.00"), "utilization_pct": ("33.22", "100.00"), "memory_used_mib": ("7540.88", "11571.00"), "power_w": ("54.84", "184.81")},
}


class PageAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.images_missing_alt = 0
        self.h1_count = 0
        self.scripts: list[str | None] = []
        self.viewport = False
        self.external_assets: list[str] = []
        self.inline_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if "id" in data:
            if data["id"] in self.ids:
                raise ValueError(f"duplicate id: {data['id']}")
            self.ids.add(data["id"] or "")
        if tag in ("a", "link") and data.get("href"):
            self.links.append(data["href"] or "")
        if tag in ("img", "script"):
            if data.get("alt") is None:
                if tag == "img":
                    self.images_missing_alt += 1
            if data.get("src"):
                self.links.append(data["src"] or "")
        if tag == "script":
            self.scripts.append(data.get("src"))
            if not data.get("src"):
                self.inline_script = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and (data.get("name") or "").lower() == "viewport":
            self.viewport = True
        for key in ("src", "href"):
            value = data.get(key)
            if tag in ("script", "link") and value and urlparse(value).scheme in ("http", "https"):
                self.external_assets.append(value)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def verify_links() -> int:
    total = 0
    for name in PAGES:
        path = ROOT / name
        if not path.is_file():
            fail(f"missing page {name}")
        text = path.read_text(encoding="utf-8")
        parser = PageAudit()
        parser.feed(text)
        required_navigation = ('href="lab.html"', 'href="reports.html"', 'href="research-hub.html"', 'href="sample-reports.html"', 'href="collaborate.html"')
        if any(link not in text for link in required_navigation):
            fail(f"{name}: expected Test Lab, Reports, Research, Examples, and manufacturer navigation links")
        if parser.h1_count != 1:
            fail(f"{name}: expected one h1, got {parser.h1_count}")
        if parser.images_missing_alt:
            fail(f"{name}: image without alt text")
        if not parser.viewport:
            fail(f"{name}: viewport metadata missing")
        if parser.external_assets or parser.inline_script:
            fail(f"{name}: remote asset or inline JavaScript found: {parser.external_assets}")
        for ref in parser.links:
            url = urlparse(ref)
            if url.scheme or ref.startswith("//"):
                continue
            destination = (path.parent / url.path).resolve() if url.path else path
            if not destination.is_relative_to(ROOT):
                fail(f"{name}: link escapes site directory: {ref}")
            if not destination.exists():
                fail(f"{name}: missing local link/asset {ref}")
            if url.fragment and destination.suffix in (".html", ""):
                target_page = PageAudit()
                target_page.feed(destination.read_text(encoding="utf-8"))
                if url.fragment not in target_page.ids:
                    fail(f"{name}: missing fragment target {ref}")
            total += 1
    return total


def verify_csv_and_hashes() -> None:
    manifest = (ROOT / "evidence" / "SHA256SUMS.txt").read_text(encoding="utf-8")
    for filename, wanted in EXPECTED.items():
        path = ROOT / "data" / filename
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest not in manifest or filename not in manifest:
            fail(f"{filename}: SHA-256 does not match manifest")
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
            expected_header = ["timestamp_utc", "gpu_index", "gpu_name", "driver_version", "temperature_c", "utilization_pct", "memory_used_mib", "memory_total_mib", "power_w"]
            if reader.fieldnames != expected_header or len(rows) != 59:
                fail(f"{filename}: CSV schema or sample count mismatch")
            timestamps = [row["timestamp_utc"] for row in rows]
            if timestamps != sorted(timestamps):
                fail(f"{filename}: timestamps are not ordered")
            if any(row["gpu_name"] != "NVIDIA GeForce RTX 4070" for row in rows):
                fail(f"{filename}: GPU identity changed")
            for metric, (mean_expected, peak_expected) in wanted.items():
                values = [Decimal(row[metric]) for row in rows]
                mean = sum(values) / Decimal(len(values))
                if f"{mean:.2f}" != mean_expected or f"{max(values):.2f}" != peak_expected:
                    fail(f"{filename}: {metric} statistics mismatch")
    if "f6a39dfcb3febf9c61e88a1944f91f20171846f07309a833cf40b4d63f3d8a00  data/idle.csv" not in manifest:
        fail("idle capture differs from the verified source hash")
    if "41881d8562b4bdad2d31a9aba1decef8a33eeb939b2332600dfefe45b27fd3a7  data/mixed-comfyui.csv" not in manifest:
        fail("mixed capture differs from the verified source hash")

    fallback_source = (ROOT / "data" / "telemetry-fallback.js").read_text(encoding="utf-8")
    prefix = "window.KTT_TELEMETRY_DATA = "
    if not fallback_source.startswith(prefix) or not fallback_source.rstrip().endswith(";"):
        fail("local-file chart fallback is missing or malformed")
    fallback = json.loads(fallback_source[len(prefix):].rstrip()[:-1])
    for key, filename in (("idle", "idle.csv"), ("mixed", "mixed-comfyui.csv")):
        with (ROOT / "data" / filename).open(encoding="utf-8-sig", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        if len(fallback.get(key, [])) != len(source_rows):
            fail(f"{key}: fallback sample count differs from CSV")
        for source_row, fallback_row in zip(source_rows, fallback[key]):
            if source_row["timestamp_utc"] != fallback_row["timestamp_utc"]:
                fail(f"{key}: fallback timestamp differs from CSV")
            for metric in ("temperature_c", "utilization_pct", "memory_used_mib", "power_w"):
                if Decimal(source_row[metric]) != Decimal(str(fallback_row[metric])):
                    fail(f"{key}: fallback {metric} value differs from CSV")


def verify_privacy_and_presentation() -> None:
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "site.js").read_text(encoding="utf-8")
    if "prefers-reduced-motion" not in css or not re.search(r"@media\s*\(max-width:\s*540px\)", css):
        fail("mobile or reduced-motion CSS missing")
    if "fetch(path)" not in js or "KTT_TELEMETRY_DATA" not in js or "addEventListener('pointermove'" not in js or "addEventListener('keydown'" not in js or "ArrowRight" not in js or "addEventListener('click'" not in js:
        fail("interactive CSV chart implementation missing")
    if re.search(r"(?i)([A-Z]:\\Users\\|[A-Z]:\\AI\\|sk-[a-zA-Z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)", "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() not in {".png"})):
        fail("local path or credential-shaped string found in public site files")
    pages = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in PAGES)
    if "contact@kyletechtesting.com" not in pages:
        fail("current public contact address is missing")
    public_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and p.suffix.lower() in {".html", ".md"})
    if "kyle.techtesting@gmail.com" in public_text:
        fail("outdated public contact address remains in site files")
    collaboration = (ROOT / "collaborate.html").read_text(encoding="utf-8")
    if "Propose a Hardware Evaluation" not in collaboration or "mailto:contact@kyletechtesting.com?subject=Hardware%20evaluation%20proposal" not in collaboration or "Your%20name%2C%20role%2C%20and%20contact%20information" not in collaboration:
        fail("manufacturer CTA or prefilled contact fields are missing")
    if "Your specifications tell customers what your hardware is designed to do." not in collaboration:
        fail("manufacturer value proposition is missing")
    for disclosure in ("not independently verified", "not tested", "endurance", "no established"):
        if disclosure not in pages.lower():
            fail(f"required evidence/marketing disclosure missing: {disclosure}")
    for name in ("demo-mini-pc.html", "demo-peripheral.html", "demo-networking.html"):
        demo = (ROOT / name).read_text(encoding="utf-8").lower()
        if "demonstration report" not in demo or "not a completed product evaluation" not in demo:
            fail(f"{name}: demonstration disclosure missing")
    archive = (ROOT / "reports.html").read_text(encoding="utf-8").lower()
    if "planned evaluations" not in archive or "not yet tested" not in archive:
        fail("reports archive: planned work status missing")
    if not (ROOT / ".nojekyll").exists():
        fail("GitHub Pages .nojekyll marker missing")


def verify_research_snapshot() -> None:
    path = ROOT / "data" / "blender-4.4.0-optix-gpu.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        required = ["device_name", "median_score_samples_per_min", "benchmark_count", "blender_version", "compute_type", "source_name", "collected_utc"]
        if reader.fieldnames != required or len(rows) != 7:
            fail("Blender snapshot schema or record count mismatch")
        if len({row["device_name"] for row in rows}) != len(rows):
            fail("duplicate GPU in Blender snapshot")
        expected_rows = {
            "NVIDIA GeForce RTX 5080": ("9163.59", 1151),
            "NVIDIA GeForce RTX 4080 SUPER": ("8440.77", 168),
            "NVIDIA GeForce RTX 4080": ("8429.57", 139),
            "NVIDIA GeForce RTX 4070 Ti SUPER": ("7123.36", 240),
            "NVIDIA GeForce RTX 4070 Ti": ("6307.34", 151),
            "NVIDIA GeForce RTX 5070": ("6190.96", 436),
            "NVIDIA GeForce RTX 4070 SUPER": ("6155.93", 256),
        }
        actual_rows = {row["device_name"]: (row["median_score_samples_per_min"], int(row["benchmark_count"])) for row in rows}
        if actual_rows != expected_rows:
            fail("headline Blender scores or sample counts differ from the verified query snapshot")
        for row in rows:
            if row["blender_version"] != "4.4.0" or row["compute_type"] != "OPTIX" or row["source_name"] != "Blender Open Data" or row["collected_utc"] != "2026-11-21":
                fail("Blender snapshot contains inconsistent source metadata")
            if Decimal(row["median_score_samples_per_min"]) <= 0 or int(row["benchmark_count"]) <= 0:
                fail("Blender snapshot contains invalid measurement")
    hub = (ROOT / "research-hub.html").read_text(encoding="utf-8")
    gpu_article = (ROOT / "gpu-research.html").read_text(encoding="utf-8")
    if "THIRD-PARTY DATA" not in hub or "NOT TESTED BY KYLE TECH TESTING" not in hub or "CC0 (Creative Commons Zero)" not in hub or "different processors" not in gpu_article.lower():
        fail("external benchmark attribution or conditions disclosure missing")
    for article, marker in (("mini-pc-guide.html", "not a review of a specific mini pc"), ("processor-guide.html", "not kyle tech test results"), ("windows-compatibility.html", "not a claim that the listed devices were tested")):
        if marker not in (ROOT / article).read_text(encoding="utf-8").lower():
            fail(f"{article}: research-vs-testing distinction missing")
    sources = (ROOT / "research-sources.md").read_text(encoding="utf-8")
    for expected in ("CC0", "Open GPU Benchmarks", "synthetic scaffold data", "2026-11-21", "Intel ARK", "Microsoft"):
        if expected.lower() not in sources.lower():
            fail(f"research source register missing {expected}")
    for device, (score, count) in expected_rows.items():
        model_label = device.replace("NVIDIA GeForce ", "")
        expected_table_row = f"<th scope=\"row\">{model_label}</th><td>{Decimal(score):,.2f}</td><td>{count:,}</td>"
        if model_label not in (ROOT / "data" / "blender-4.4.0-optix-gpu.csv").read_text(encoding="utf-8") or expected_table_row not in gpu_article:
            fail(f"research chart/table is missing source data for {device}")


def main() -> None:
    links = verify_links()
    verify_csv_and_hashes()
    verify_privacy_and_presentation()
    verify_research_snapshot()
    print(f"PASS: {len(PAGES)} pages; {links} local links/assets; two byte-verified 59-sample evidence CSVs; seven-row third-party benchmark snapshot; responsive/accessibility/privacy/source-attribution checks.")


if __name__ == "__main__":
    main()
