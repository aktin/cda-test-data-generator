# CDA Synthetic Data Generator

Standalone generator for synthetic HL7 CDA emergency-department documents
compliant with the **AKTIN Notaufnahmeregister** data model (template
`1.2.276.0.76.10.1019`).

---

## Requirements

- Python 3.9+
- `lxml >= 4.9`
- `pandas >= 1.3` (required for `--mode empirical` and `--mode anonymize` only)
- `pytest >= 7.0` (tests only)

```bash
pip install -r requirements.txt
```

`pandas` is imported lazily — synthetic mode works without it.

---

## Quick Start

```bash
# Generate 10 synthetic CDA documents (written to ./output)
python generate.py --count 10

# Send 50 synthetic documents directly to a local AKTIN DWH (no files written)
python generate.py --count 50 --generate-cda false \
    --dwh-url http://localhost:18080/aktin/cda/fhir/Binary

# Generate files AND send to DWH
python generate.py --count 50 --output-dir ./cda_out \
    --dwh-url http://localhost:18080/aktin/cda/fhir/Binary

# Reproducible output with fixed seed
python generate.py --count 50 --seed 42 --output-dir ./cda_out

# Preview summary table only — no files, no sending
python generate.py --count 20 --generate-cda false
```

---

## Generation Modes

### `synthetic` (default)

Generates clinically plausible random values with no external data required.
All distributions are hard-coded (see *Generated Data Points* below).

```bash
python generate.py --count 100 --seed 42
```

### `empirical` — `--mode empirical --data-dir DIR`

Reads AKTIN raw exports (`case_data.txt` + `diag_data.txt`) from `DIR`,
learns empirical distributions (admission-hour weights, LOS, vitals,
categorical frequencies, procedure absence rates, ICD codes), and generates
`N` statistically representative synthetic rows.
Requires `pandas >= 1.3`.

```bash
python generate.py --mode empirical --count 200 \
    --data-dir ./sampling_data --output-dir ./cda_empirical
```

### `anonymize` — `--mode anonymize --data-dir DIR`

Reads the same exports and produces one anonymised row per real case (or a
random sample of N). Rules:

- Timestamps are reassigned to a random day in the **same calendar month**
  and jittered by `±time-jitter` minutes (default ±30 min).
- LOS and intra-encounter offsets (triage, doctor contact) are preserved.
- Vitals are Gaussian-jittered by `±1–5` units; GCS components are left intact.
- All PII (name, address, contact) is replaced with synthetic values.
- Diagnoses are taken from the real `diag_data.txt` lookup for that case.

Requires `pandas >= 1.3`.

```bash
python generate.py --mode anonymize --count 50 \
    --data-dir ./sampling_data --output-dir ./cda_anon \
    --time-jitter 30 --age-jitter 2
```

Place the AKTIN raw export files in the data directory before running empirical
or anonymize mode:

```
sampling_data/
├── case_data.txt
└── diag_data.txt
```

---

## Sending to an AKTIN DWH

Pass `--dwh-url` with the FHIR Binary endpoint. If the flag is omitted, nothing
is sent. Sending works independently of `--generate-cda` and is available in all
three generation modes — no real export data is required for `synthetic`.

```bash
# Synthetic — send 100 cases, no files written
python generate.py --count 100 --generate-cda false \
    --dwh-url http://localhost:18080/aktin/cda/fhir/Binary

# Synthetic — write files AND send
python generate.py --count 100 --output-dir ./cda_out \
    --dwh-url http://localhost:18080/aktin/cda/fhir/Binary

# Empirical — send 1000 statistically representative cases
python generate.py --mode empirical --count 1000 \
    --data-dir ./sampling_data \
    --start-date 2025-01-01 --end-date 2026-02-28 \
    --generate-cda false \
    --dwh-url http://localhost:18080/aktin/cda/fhir/Binary

# Anonymize — send all cases from sampling_data
python generate.py --mode anonymize --data-dir ./sampling_data \
    --generate-cda false \
    --dwh-url http://localhost:18080/aktin/cda/fhir/Binary
```

Each HTTP response is inspected: `200 OK` (updated) and `201 Created` count as
success; any other status is a failure and the FHIR `OperationOutcome` issues
(if present) are printed to the console. The process exits with code 1 if any
case fails.

Cases are sent in chronological order by admission date. The summary line shows
separate counters for file writes and DWH sends:

```
[done]  total=50  files_ok=50  files_fail=0  dwh_ok=50  dwh_fail=0
```

---

## CLI Reference

| Flag | Default | Description |
|---|---|---|
| `--mode MODE` | `synthetic` | Generation mode: `synthetic` \| `empirical` \| `anonymize` |
| `--count N` | `10` | Number of CDA documents to generate |
| `--data-dir DIR` | `./sampling_data` | Directory with `case_data.txt` + `diag_data.txt` (required for empirical/anonymize) |
| `--output-dir DIR` | `./output` | Directory for CDA XML files (created if absent) |
| `--generate-cda true\|false` | `true` | Write CDA files to disk; set to `false` to skip |
| `--dwh-url URL` | *(none)* | AKTIN DWH FHIR Binary endpoint. If omitted, nothing is sent. |
| `--org-id OID` | `1.2.276.0.76.4.17.9999` | Hospital OID written into every document |
| `--org-name NAME` | `AKTIN Testklinikum` | Hospital display name |
| `--author-prefix PREFIX` | `Dr.` | Author name prefix |
| `--author-first NAME` | `Mara` | Author given name |
| `--author-last NAME` | `Mustermensch` | Author family name |
| `--start-date YYYY-MM-DD` | `2000-01-01` | Admission date range start (synthetic/empirical) |
| `--end-date YYYY-MM-DD` | Today | Admission date range end (synthetic/empirical) |
| `--time-jitter MIN` | `30` | Anonymize: max admission time jitter in minutes |
| `--age-jitter YRS` | `2` | Anonymize: max age jitter in years |
| `--seed INT` | *(random)* | RNG seed for reproducible output |
| `--csv-out FILE` | *(none)* | Write intermediate staging rows to FILE as TSV |

### Examples

```bash
# Synthetic — reproducible, custom hospital identity, write files
python generate.py \
    --count 100 \
    --org-id 1.2.276.0.76.4.17.1234 \
    --org-name "Klinikum Musterstadt" \
    --start-date 2025-01-01 \
    --end-date 2025-12-31 \
    --seed 7 \
    --output-dir ./cda_2025

# Empirical — 200 cases based on real data, write files
python generate.py --mode empirical --count 200 \
    --data-dir ./sampling_data --output-dir ./cda_empirical

# Anonymize — 50 cases from real data, jittered, write files
python generate.py --mode anonymize --count 50 \
    --data-dir ./sampling_data --output-dir ./cda_anon \
    --time-jitter 30 --age-jitter 2

# Inspect staging rows without generating any CDA files
python generate.py --count 20 --generate-cda false \
    --csv-out ./staging_preview.tsv
```

### Summary table

Every run prints a tab-aligned summary before writing files:

```
Encounter-ID                    Aufnahme             G  T  Sys  CEDIS  ICD-10    Verbleib
------------------------------  -------------------  -  -  ---  -----  --------  -------
SYN-ENC-2026-00001              2026-03-22 23:57:00  W  3  MTS  007    T14.0     S
SYN-ENC-2026-00002              2026-03-11 12:17:00  F  4  MTS  657    S06.0     5
```

Columns: encounter ID · admission datetime · gender · triage level ·
triage system · CEDIS code · primary ICD-10-GM · discharge disposition.

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output: **49 passed** in < 2 seconds.

| Suite | Tests | What is verified |
|---|---|---|
| `TestDataGenerator` | 12 | Row count, required columns, timestamp ordering, GCS consistency, valid codes, isolation logic, reproducibility, quarter-end calculation, secondary diagnose keys |
| `TestColumnMapper` | 18 | Gender mapping, timestamp formats, discharge codes, allergy/tetanus flags, UUID generation, triage OIDs, vital-signs fallback, diagnosis parsing |
| `TestTransformer` | 5 | ClinicalDocument root element, well-formed XML, encounter ID, patient ID, realmCode DE |
| `TestFullPipeline` | 3 | 100 rows build without error, unique encounter IDs, unique CDA document IDs |
| `TestEmpiricalStubs` | 6 | Distribution analysis keys, LOS positivity, 24-entry hour weights, ICD codes present, valid CDA built, GCS consistency |
| `TestAnonymizeStubs` | 5 | Valid CDA from anonymised row, same calendar month, diagnoses from lookup, PII cleared, `_build_diag_lookup` correctness |

All tests use in-memory pandas DataFrames; no real AKTIN export files required.

---

## Pipeline Architecture

```
data_generator.generate_rows*(count, ...)
        |
        |  list[dict]   (German CSV column names)
        v
column_mapper.map_row(row, ...)
        |
        |  dict         (XSLT field names)
        v
transformer.transform(fields)
        |
        |  lxml ElementTree
        v
   CDA XML / AKTIN DWH   (HL7 CDA R2, template 1.2.276.0.76.10.1019)
```

### `src/data_generator.py`

Three public entry points:

| Function | Mode | pandas |
|---|---|---|
| `generate_rows(count, ...)` | synthetic | not needed |
| `generate_rows_empirical(case_data_path, diag_data_path, count, ...)` | empirical | required |
| `generate_rows_anonymize(case_data_path, diag_data_path, count, ...)` | anonymize | required |

Key behaviours (all modes):

- CEDIS codes loaded from `resources/cedis.csv` at import; falls back to a
  12-entry hard-coded list if the file is absent.
- Timestamp chain enforced: every row satisfies
  `admission ≤ triage ≤ doctor_contact`, `discharge > admission`.
- GCS components always sum to `gcs_gesamt`.
- Accepts `seed` parameter for fully reproducible output.

Empirical-specific:

- Learns admission-hour weights, LOS bootstrap samples, vitals histograms,
  categorical frequency dicts, procedure absence rates, and ICD code pools
  from `case_data.txt` and `diag_data.txt`.
- Falls back to synthetic defaults for any column absent from the data.

Anonymize-specific:

- Parses original timestamps; preserves LOS and intra-encounter offsets.
- Reassigns to a random day in the same calendar month + time jitter.
- Jitters vitals with Gaussian noise (std = 1–5 units per field).
- Replaces all PII with fresh synthetic values.

### `src/column_mapper.py`

Translates the German staging-CSV column names to the flat XSLT field dict
consumed by `EmergencyNote.xslt`. Handles:

- Timestamp normalisation (multiple input formats → `YYYYMMDDHHmmSS`)
- Gender synonym `W` → `F`
- Discharge codes `S`/`V` → `verlegung_type` (voc-53)
- Triage system abbreviation → OID (`MTS` → `1.2.276.0.76.5.438`, etc.)
- Pupil size numeric mm → voc-49 codes (C/M/D)
- Allergy/tetanus 0/1 flags → XML `negationInd` booleans
- Diagnostic 0/1 → PB/OPB
- CEDIS code validated against schematron vocabulary if available
- Auto-generates UUID for `document_id` when `cda_dokument_id` is empty

### `src/transformer.py`

Wraps `lxml.etree.XSLT`. Builds an `<aktin_raw>` XML element from the field
dict, applies `resources/EmergencyNote.xslt`, and returns the resulting
`lxml._ElementTree`. The compiled XSLT is cached after first use.

### `resources/EmergencyNote.xslt`

XSLT 1.0 template that transforms `<aktin_raw>` into a complete
HL7 CDA R2 `<ClinicalDocument>`. This file is kept in sync with the copy in
`csv2cda/resources/EmergencyNote.xslt` — both are identical and only need to be
maintained once. Handles all AKTIN templates including:

- Document header (id, code, effectiveTime, confidentialityCode)
- recordTarget / patientRole (demographics, address, telecom)
- author (1 or 2 authors)
- custodian, legalAuthenticator
- componentOf / encompassingEncounter (admission/discharge times, referral)
- serviceEvent / documentationOf (therapy times, performer)
- Sections: transport, CEDIS chief complaint, triage, vital signs, GCS,
  pupils, Rankin scale, isolation, MRO, diagnostics, discharge disposition,
  diagnoses, emergency history, allergies, tetanus immunisation

---

## Generated Data Points

All fields are derived from the staging CSV format defined in the
[AKTIN DATA_DICTIONARY](resources/DATA_DICTIONARY.md).
The table below documents every simulated data point.

### Document identification

| CSV column | Generated value |
|---|---|
| `patientennummer` | `SYN-P-<N>` (zero-padded 5-digit index) |
| `dokument_id` | `SYN-ENC-<YEAR>-<N>` |
| `Krankenhausinternes Fallkennzeichen` | `KH-<50000+N>` |
| `cda_dokument_id` | Random UUID v4 (unique per row) |
| `dokument_erstellungszeitpunkt` | Admission time + 0–5 min |
| `dokument_versionsnummer` | `1` |

### Patient demographics

| CSV column | Generated value |
|---|---|
| `geschlecht` | `M` / `F` / `W` (uniform random) |
| `patient_vorname` | Random from 20 German given names per gender |
| `patient_nachname` | Random from 30 common German family names |
| `patient_geburtsdatum` | Derived from random age 18–92 years |
| `patient_strasse` | Random from 12 street names |
| `patient_hausnummer` | Random integer 1–120 |
| `patient_ort` / `postleitzahl` / `patient_bundesland` | 15 German cities with matching PLZ and Bundesland |
| `patient_telefon` / `patient_mobiltelefon` / `patient_email` | Empty (optional fields) |

### Author

| CSV column | Generated value |
|---|---|
| `autor_1_zeitpunkt` | Same as `dokument_erstellungszeitpunkt` |
| `autor_1_id` / `autor_1_praefix` / `autor_1_vorname` / `autor_1_nachname` | From CLI args (`--author-*`); defaults: `A-4711`, `Dr.`, `Mara`, `Mustermensch` |
| `autor_2_*` | Empty (second author omitted) |

### Organisation

All organisation fields come from CLI args (`--org-*`).
Defaults represent a generic AKTIN test hospital in Berlin.

### Insurance

| CSV column | Generated value |
|---|---|
| `krankenkasse_name` | Random from 6 real Krankenkassen + `Unbekannt` (higher weight) |
| `ik_nummer` | IK number matching the chosen Krankenkasse |
| `egk_nummer` | Random 9-digit `E…` number (empty when Kasse = Unbekannt) |
| `versicherungsnummer` | Random 9-digit `V…` number (empty when Kasse = Unbekannt) |
| `versicherungs_quartalsende` | Last day of current quarter (`YYYYMMDD`) |
| `versicherter_vorname` / `versicherter_nachname` / `vk_nummer` | Empty |

### Encounter timing

All timestamps are logically ordered and consistent:

```
admission
  + 1–10 min  → triage_zeitpunkt
  + 5–25 min  → arztkontakt_beginn_zeitpunkt
  ± 2–5 min   → therapiebeginn_zeitpunkt
  + 30 min–8 h (from admission) → entlassung_zeitpunkt
                                → therapieende_zeitpunkt (≤ discharge)
                                → arztkontakt_ende_zeitpunkt (≤ discharge)
```

| CSV column | Notes |
|---|---|
| `aufnahme_zeitpunkt` | Random time on a random day in the configured date range |
| `entlassung_zeitpunkt` | Admission + 30 min to 8 h |
| `triage_zeitpunkt` | Admission + 1–10 min |
| `arztkontakt_beginn_zeitpunkt` | Triage + 5–25 min |
| `arztkontakt_ende_zeitpunkt` | Discharge − 5–20 min |
| `therapiebeginn_zeitpunkt` | Doctor contact ± 2–5 min |
| `therapieende_zeitpunkt` | Discharge − 0–20 min |

### Referral and transport

| CSV column | Values | Weights |
|---|---|---|
| `zuweisungsart` | VAP · KVNDAK · KVNPIK · RD · NA · KLINV · NPHYS · OTH | 15:12:8:30:10:8:10:7 |
| `transportmittel` | NA · 1(KTW) · 2(RTW) · 3(NAW) · 4(RTH) · OTH | 25:15:30:20:5:5 |

### Chief complaint (CEDIS)

| CSV column | Generated value |
|---|---|
| `vorstellungsgrund_cedis` | Random CEDIS 3-digit code from `resources/cedis.csv` |
| `vorstellungsgrund_text` | Display name of the selected CEDIS code |
| `symptomdauer` | Random from {5, 10, 15, 30, 60, 120, 240, 480, 1440, 2880, 10080} minutes |

### Triage

| CSV column | Generated value |
|---|---|
| `triage_system` | `MTS` (70 %) / `ESI` (30 %) |
| `triage_stufe` | 1–5 weighted towards levels 3–4 (3:15:40:35:7) |
| `triage_zeitpunkt` | See encounter timing above |

### Vital signs

Ranges are correlated to triage level — level 1 (most severe) allows wider
and more extreme ranges; level 5 (least severe) stays close to normal.

| CSV column | Unit | Level 1 range | Level 3 range | Level 5 range |
|---|---|---|---|---|
| `atemfrequenz` | /min | 0–40 | 10–30 | 12–20 |
| `sauerstoffsaettigung` | % | 70–95 | 88–100 | 95–100 |
| `blutdruck_systolisch` | mmHg | 60–130 | 90–190 | 110–160 |
| `herzfrequenz` | /min | 40–160 | 55–130 | 60–100 |
| `koerperkerntemperatur` | °C | 34.5–40.5 | 35.5–39.5 | 36.2–37.8 |
| `schmerzskala` | 0–10 NRS | 0–10 | 3–9 | 0–5 |

Vitals may be omitted for triage levels 4–5 (30 % probability).

### Glasgow Coma Scale

| CSV column | Range | Notes |
|---|---|---|
| `gcs_gesamt` | 3–15 (level-dependent) | Always equals eyes + verbal + motor |
| `gcs_augen` | 1–4 | Proportionally distributed from total |
| `gcs_verbal` | 1–5 | Proportionally distributed from total |
| `gcs_motorik` | 1–6 | Remainder: total − eyes − verbal |

GCS is omitted for triage levels 4–5 (50 % probability).

### Pupils

| CSV column | Codes | Notes |
|---|---|---|
| `pupillenweite_rechts` / `pupillenweite_links` | C · M · D · UNK | Weights 10:60:5:25 |
| `pupillenreaktion_rechts` / `pupillenreaktion_links` | B · D · A · UNK | Weights 65:10:5:20 |

Pupils only generated when GCS is present (60 % probability).

### Modified Rankin Scale

`rankin_skala` 0–6, weighted towards 0–2 (30:20:15:15:10:8:2).

### Isolation

| CSV column | Notes |
|---|---|
| `isolationsstatus` | `1` (5 % probability), otherwise `0` |
| `isolationsgrund` | One of U80 · A09.9 · A16.9 · G03.9 · OTH — only when isolated |

### Multidrug-resistant organisms (MRO)

`multiresistente_erreger` = 1 with 3 % probability. When present, exactly
one of MRSA (30 %) · 3MRGN (20 %) · 4MRGN (10 %) · VRE (20 %) is set;
otherwise generic AMRO.

### Diagnostic modalities

Each modality is independently drawn. Timestamps are doctor_contact + offset.

| Modality | CSV column | Probability | Timestamp offset |
|---|---|---|---|
| Laboratory | `labor_durchgefuehrt` | 75 % | +10–60 min |
| Blood gas analysis | `bga_durchgefuehrt` | 30 % | +15–45 min |
| Urinalysis | `urinschnelltest_durchgefuehrt` | 25 % | +15–50 min |
| ECG | `ekg_durchgefuehrt` | 55 % | +5–30 min |
| Ultrasound | `sonographie_durchgefuehrt` | 20 % | +20–70 min |
| Echocardiography | `echokardiographie_durchgefuehrt` | 8 % | +30–90 min |
| CT head (cCT) | `cct_durchgefuehrt` | 15 % | +30–90 min |
| CT (axial) | `ct_durchgefuehrt` | 20 % | +30–90 min |
| Trauma scan | `traumascan_durchgefuehrt` | 5 % | +20–60 min |
| X-ray spine | `roentgen_wirbelsaeule_durchgefuehrt` | 8 % | +20–60 min |
| X-ray thorax | `roentgen_thorax_durchgefuehrt` | 30 % | +15–60 min |
| X-ray pelvis | `roentgen_becken_durchgefuehrt` | 5 % | +20–60 min |
| X-ray extremity | `roentgen_extremitaet_durchgefuehrt` | 12 % | +15–50 min |
| X-ray other | `roentgen_sonstiges_durchgefuehrt` | 5 % | +20–60 min |
| MRI | `mrt_durchgefuehrt` | 7 % | +40–120 min |

Each `*_durchgefuehrt` column is `PB` (performed) or `OPB` (not performed).
The matching `*_zeitpunkt` column is populated only when performed.

### Discharge disposition

| Code | Meaning | Weight |
|---|---|---|
| `1` | Tod | 1 |
| `2` | Entlassung gegen ärztlichen Rat | 2 |
| `3` | Behandlung abgebrochen | 3 |
| `4` | Entlassung nach Hause | 40 |
| `5` | Entlassung zu weiterbehandelndem Arzt | 10 |
| `6` | Kein Arztkontakt | 5 |
| `S` | Stationär aufgenommen | 30 |
| `V` | Verlegt | 9 |

### Diagnoses

| CSV column | Generated value |
|---|---|
| `icd10gm_code` | Random from pool of 27 common ED ICD-10-GM codes |
| `diagnose_fuehrend_zusatzkennzeichen` | G (70 %) · V (20 %) · A (5 %) · Z (5 %) |
| `diagnose_2` … `diagnose_3` | 0–3 secondary codes from 15-code pool (40:35:20:5 weights) |
| `diagnose_*_zusatzkennzeichen` | Same qualifier distribution as primary |

Primary ICD-10-GM pool includes: I21.9 · I20.0 · I10 · J18.9 · K35.80 ·
S06.0 · M54.5 · R55 · R07.4 · R51 · J06.9 · K29.7 · T14.0 · S52.5 · I63.9
· E11.9 · N23 · G40.9 · F10.0 · T39.1 · R60.0 · K80.20 · J44.1 · I48.0 ·
Z87.39 · I25.9 · G47.0.

### Emergency history (Notfallanamnese)

`notfallanamnese`: free-text sentence generated from 5 templates, using the
CEDIS display name as the chief complaint phrase.

### Allergies

| CSV column | Notes |
|---|---|
| `allergie_allgemein` | `1` (30 % probability) |
| `allergie_antibiotika` | `1` (15 % if allergy present) |
| `allergie_kontrastmittel` | `1` (10 % if allergy present) |
| `allergie_sonstige` | `1` (20 % if allergy present) |
| `allergie_freitext` | Free-text description (empty when no allergy) |

### Tetanus immunisation

`tetanusschutz`: `1` (protected, 60 %) · `0` (not protected, 20 %) ·
empty/unknown (20 %).

---

## Limitations

- Vitals and GCS use independent random draws per field; real clinical
  correlations (e.g. low GCS with low SpO2) are approximated only through
  triage-level ranges, not explicit joint distributions.
- Secondary diagnoses are drawn from a 15-code pool independent of the
  primary diagnosis.
- Patient names, addresses, and free-text fields are drawn from small
  predefined lists and do not reflect regional or demographic distributions.
- No schematron validation is performed by the generator. The XSLT output
  can be validated separately using the schematron rules in
  `resources/shematron/` of the main project.
