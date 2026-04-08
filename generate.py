"""
generate.py — Synthetic CDA generator (shipping edition)
---------------------------------------------------------
Three generation modes:

  synthetic  (default)
      Clinically plausible random values.  No external data required.

  empirical  --data-dir DIR
      Reads AKTIN raw exports (case_data.txt + diag_data.txt) from DIR,
      learns empirical distributions (admission-hour weights, LOS, vitals,
      categorical frequencies, procedure absence rates, ICD codes), and
      generates N statistically representative synthetic rows.
      Requires pandas>=1.3.

  anonymize  --data-dir DIR
      Reads the same exports and produces one anonymised row per real case
      (or a random sample of N).  Timestamps are reassigned to a random day
      in the same calendar month and jittered by ±30 min.  LOS and offsets
      are preserved.  Vitals are gently jittered.  All PII is replaced.
      Requires pandas>=1.3.

Usage
-----
    python generate.py --count 10 --output-dir ./output

    python generate.py --mode empirical --count 200 \\
        --data-dir ./data/2024-Q1 --output-dir ./cda_out

    python generate.py --mode anonymize --count 50 \\
        --data-dir ./data/2024-Q1 --output-dir ./cda_anon \\
        --time-jitter 30 --age-jitter 2

    python generate.py --count 5 --seed 42 --generate-cda false

    # Generate and send to AKTIN DWH (no files written)
    python generate.py --count 10 --generate-cda false \\
        --dwh-url http://localhost:18080/aktin/cda/fhir/Binary

    # Write files AND send to AKTIN DWH
    python generate.py --count 10 --output-dir ./output \\
        --dwh-url http://localhost:18080/aktin/cda/fhir/Binary
"""

import argparse
import csv
import datetime
import os
import sys
import urllib.request
import urllib.error

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.join(_HERE, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from lxml import etree
from column_mapper import map_row
from data_generator import generate_rows, generate_rows_empirical, generate_rows_anonymize
from transformer import transform

# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

_TABLE_COLS = [
    ("dokument_id",                  "Encounter-ID",  30),
    ("aufnahme_zeitpunkt",           "Aufnahme",      19),
    ("geschlecht",                   "G",              1),
    ("triage_stufe",                 "T",              1),
    ("triage_system",                "Sys",            3),
    ("vorstellungsgrund_cedis",      "CEDIS",          5),
    ("icd10gm_code",                 "ICD-10",         8),
    ("verbleib_nach_notaufnahme",    "Verbleib",       7),
]


def _print_table(rows: list) -> None:
    header = "  ".join(label.ljust(w) for _, label, w in _TABLE_COLS)
    sep    = "  ".join("-" * w        for _, _,     w in _TABLE_COLS)
    print(header)
    print(sep)
    for row in rows:
        line = "  ".join(
            str(row.get(col, "")).ljust(w)[:w] for col, _, w in _TABLE_COLS
        )
        print(line)
    print()


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def _write_csv(rows: list, path: str) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t",
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[csv]   {len(rows)} rows written -> {path}")


# ---------------------------------------------------------------------------
# DWH sender
# ---------------------------------------------------------------------------

def _http_post(url: str, data: bytes, content_type: str = "text/xml") -> tuple:
    """POST *data* to *url*; return (status_code, body_text)."""
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": content_type},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body
    except OSError as e:
        return 503, str(e)


def _parse_operation_outcome(body: str) -> list:
    """Extract issue texts from a FHIR OperationOutcome XML response."""
    try:
        root = etree.fromstring(body.encode("utf-8"))
    except etree.XMLSyntaxError:
        return [body[:500]] if body.strip() else []
    issues = []
    for issue in root.findall(".//{http://hl7.org/fhir}issue"):
        diag     = issue.find("{http://hl7.org/fhir}diagnostics")
        details  = issue.find("{http://hl7.org/fhir}details/{http://hl7.org/fhir}text")
        severity = issue.find("{http://hl7.org/fhir}severity")
        sev = severity.get("value", "?") if severity is not None else "?"
        txt = ""
        if diag is not None:
            txt = diag.get("value", "")
        elif details is not None:
            txt = details.get("value", "")
        if txt:
            issues.append(f"[{sev}] {txt}")
    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic HL7 CDA emergency-department documents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Mode
    parser.add_argument("--mode", choices=["synthetic", "empirical", "anonymize"],
                        default="synthetic",
                        help="Generation mode (default: synthetic).")
    _default_data_dir = os.path.join(_HERE, "sampling_data")
    parser.add_argument("--data-dir", default=_default_data_dir, metavar="DIR",
                        help="Directory containing case_data.txt and diag_data.txt "
                             f"(default: ./sampling_data).")

    # Volume
    parser.add_argument("--count", type=int, default=None,
                        help="Number of CDA documents to generate. "
                             "Defaults to the number of unique a_encounter_num values in "
                             "case_data.txt for anonymize/empirical modes, or 10 for synthetic.")

    # Output
    parser.add_argument("--output-dir", default="./output",
                        help="Directory for CDA XML files (default: ./output).")
    parser.add_argument("--generate-cda",
                        type=lambda v: v.lower() == "true", default=True,
                        metavar="true|false",
                        help="Generate CDA files: true (default) or false to skip file generation.")
    parser.add_argument("--csv-out", default=None, metavar="FILE",
                        help="Write staging-CSV rows to FILE (tab-separated). "
                             "Use with --generate-cda false to skip CDA generation entirely.")

    # Hospital / author identity
    parser.add_argument("--org-id",       default="1.2.276.0.76.4.17.9999")
    parser.add_argument("--org-name",     default="AKTIN Testklinikum")
    parser.add_argument("--author-prefix",default="Dr.")
    parser.add_argument("--author-first", default="Mara")
    parser.add_argument("--author-last",  default="Mustermensch")

    # Date range (synthetic + empirical)
    parser.add_argument("--start-date", default=None, metavar="YYYY-MM-DD",
                        help="Admission date range start.")
    parser.add_argument("--end-date",   default=None, metavar="YYYY-MM-DD",
                        help="Admission date range end.")

    # Anonymize-specific
    parser.add_argument("--time-jitter", type=int, default=30, metavar="MIN",
                        help="Anonymize: max admission time jitter in minutes (default: 30).")
    parser.add_argument("--age-jitter",  type=int, default=2,  metavar="YRS",
                        help="Anonymize: max age jitter in years (default: 2).")

    # Reproducibility
    parser.add_argument("--seed", type=int, default=None,
                        help="RNG seed for reproducible output.")

    # DWH sending
    parser.add_argument("--dwh-url", default=None, metavar="URL",
                        help="FHIR Binary endpoint to POST each CDA to, "
                             "e.g. http://localhost:18080/aktin/cda/fhir/Binary")

    args = parser.parse_args()

    # Validate data-dir for real-data modes
    if args.mode in ("empirical", "anonymize"):
        case_path_check = os.path.join(args.data_dir, "case_data.txt")
        if not os.path.isfile(case_path_check):
            parser.error(
                f"case_data.txt not found in '{args.data_dir}'. "
                f"Place case_data.txt and diag_data.txt in that directory "
                f"or pass a different path with --data-dir."
            )
        if args.count is None:
            import csv as _csv
            with open(case_path_check, newline="", encoding="utf-8") as _f:
                _reader = _csv.DictReader(_f, delimiter="\t")
                _enc_nums = {row["a_encounter_num"] for row in _reader if row.get("a_encounter_num")}
            args.count = len(_enc_nums)
            print(f"[generate]  --count not set; using {args.count} unique encounter(s) from case_data.txt")

    if args.count is None:
        args.count = 10

    start_date = datetime.date.fromisoformat(args.start_date) if args.start_date else None
    end_date   = datetime.date.fromisoformat(args.end_date)   if args.end_date   else None

    print(f"[generate]  mode={args.mode}  count={args.count}  "
          f"org='{args.org_name}'  seed={args.seed}  generate_cda={args.generate_cda}")

    common_kw = dict(
        org_id=args.org_id,
        org_name=args.org_name,
        author_prefix=args.author_prefix,
        author_first=args.author_first,
        author_last=args.author_last,
        seed=args.seed,
    )

    if args.mode == "synthetic":
        rows = generate_rows(
            count=args.count,
            start_date=start_date,
            end_date=end_date,
            **common_kw,
        )
    elif args.mode == "empirical":
        case_path = os.path.join(args.data_dir, "case_data.txt")
        diag_path = os.path.join(args.data_dir, "diag_data.txt")
        rows = generate_rows_empirical(
            case_data_path=case_path,
            diag_data_path=diag_path,
            count=args.count,
            start_date=start_date,
            end_date=end_date,
            **common_kw,
        )
    else:  # anonymize
        case_path = os.path.join(args.data_dir, "case_data.txt")
        diag_path = os.path.join(args.data_dir, "diag_data.txt")
        rows = generate_rows_anonymize(
            case_data_path=case_path,
            diag_data_path=diag_path,
            count=args.count,
            time_jitter_minutes=args.time_jitter,
            age_jitter_years=args.age_jitter,
            **common_kw,
        )

    _print_table(rows)

    if args.csv_out:
        _write_csv(rows, args.csv_out)

    # Nothing to do when neither writing files nor sending to DWH
    if not args.generate_cda and not args.dwh_url:
        print(f"[done]  {len(rows)} rows generated (--generate-cda false, no --dwh-url set)")
        return

    if args.generate_cda:
        os.makedirs(args.output_dir, exist_ok=True)

    # Group rows by admission date so DWH receives cases in chronological order
    from collections import defaultdict
    days: dict = defaultdict(list)
    for row in rows:
        day_key = str(row.get("aufnahme_zeitpunkt", ""))[:10]
        days[day_key].append(row)

    file_ok = file_fail = 0
    dwh_ok  = dwh_fail  = 0

    for day in sorted(days):
        if args.dwh_url:
            print(f"\n[day]  {day}  ({len(days[day])} case(s))")
        for row in days[day]:
            enc_id = row.get("dokument_id", "unknown").replace("/", "_")
            try:
                fields = map_row(
                    row,
                    org_id=args.org_id,
                    org_name=args.org_name,
                    author_prefix=args.author_prefix,
                    author_first=args.author_first,
                    author_last=args.author_last,
                )
                tree = transform(fields)
                xml_bytes = etree.tostring(
                    tree.getroot(), xml_declaration=True, encoding="UTF-8", pretty_print=True
                )
            except Exception as exc:
                print(f"  BUILD-FAIL  {enc_id}  ->  {exc}")
                file_fail += 1
                dwh_fail  += 1
                continue

            # --- Write CDA file (optional) ------------------------------------
            if args.generate_cda:
                out_path = os.path.join(args.output_dir, f"cda_{enc_id}.xml")
                try:
                    with open(out_path, "wb") as fh:
                        fh.write(xml_bytes)
                    print(f"  FILE-OK  {enc_id}  ->  {out_path}")
                    file_ok += 1
                except OSError as exc:
                    print(f"  FILE-FAIL  {enc_id}  ->  {exc}")
                    file_fail += 1

            # --- POST to AKTIN DWH (optional) ---------------------------------
            if args.dwh_url:
                status, body = _http_post(args.dwh_url, xml_bytes)
                if status in (200, 201):
                    dwh_ok += 1
                    action = "updated" if status == 200 else "created"
                    print(f"  DWH-OK ({action:<7})  {enc_id}  ->  HTTP {status}")
                else:
                    dwh_fail += 1
                    issues = _parse_operation_outcome(body)
                    print(f"  DWH-FAIL          {enc_id}  ->  HTTP {status}")
                    for issue in issues:
                        print(f"    {issue}")
                    if not issues and body.strip():
                        print(f"    {body[:300]}")

    parts = [f"total={len(rows)}"]
    if args.generate_cda:
        parts.append(f"files_ok={file_ok}  files_fail={file_fail}")
    if args.dwh_url:
        parts.append(f"dwh_ok={dwh_ok}  dwh_fail={dwh_fail}")
    print(f"\n[done]  {'  '.join(parts)}")
    if file_fail or dwh_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
