"""
test_functional.py
------------------
Functional tests for the CDA generation pipeline.  No DWH or network required.

All tests run fully in-memory: rows are generated, mapped, and transformed to
CDA XML without touching disk or any external system.

Suites
~~~~~~
TestDataGenerator    — synthetic mode: structure, timing, GCS, codes
TestColumnMapper     — field translation, gender, discharge, allergy, triage OIDs
TestTransformer      — CDA root element, well-formed XML, key fields
TestFullPipeline     — 100 rows end-to-end, ID uniqueness
TestEmpiricalStubs   — empirical helpers work with minimal in-memory DataFrames
TestAnonymizeStubs   — anonymize helpers work with minimal in-memory DataFrames
"""

import datetime as dt
import os
import sys
import uuid

import pytest
from lxml import etree

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.join(_HERE, "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from column_mapper import map_row, _to_cda_ts
from data_generator import (
    generate_rows, _quarter_end,
    _analyze_case_data, _analyze_diag_data, _build_diag_lookup,
    _empirical_one, _anonymize_one,
)
from transformer import transform

HL7 = "urn:hl7-org:v3"


# ---------------------------------------------------------------------------
# data_generator — synthetic mode
# ---------------------------------------------------------------------------

class TestDataGenerator:

    def test_generates_correct_count(self):
        assert len(generate_rows(count=5, seed=1)) == 5

    def test_all_required_columns_present(self, sample_rows):
        required = [
            "patientennummer", "dokument_id", "geschlecht",
            "aufnahme_zeitpunkt", "entlassung_zeitpunkt",
            "triage_stufe", "triage_system", "triage_zeitpunkt",
            "arztkontakt_beginn_zeitpunkt", "therapiebeginn_zeitpunkt",
            "icd10gm_code", "verbleib_nach_notaufnahme",
            "isolationsstatus", "multiresistente_erreger",
            "labor_durchgefuehrt", "ekg_durchgefuehrt",
            "organisation_id", "organisation_name",
            "autor_1_vorname", "autor_1_nachname",
            "patient_vorname", "patient_nachname", "patient_geburtsdatum",
            "allergie_allgemein", "tetanusschutz",
        ]
        for row in sample_rows:
            for col in required:
                assert col in row, f"Missing column '{col}'"

    def test_timestamps_logical_order(self, sample_rows):
        for row in sample_rows:
            admission = dt.datetime.strptime(row["aufnahme_zeitpunkt"], "%Y-%m-%d %H:%M:%S")
            triage    = dt.datetime.strptime(row["triage_zeitpunkt"],   "%Y-%m-%d %H:%M:%S")
            doctor    = dt.datetime.strptime(row["arztkontakt_beginn_zeitpunkt"], "%Y-%m-%d %H:%M:%S")
            discharge = dt.datetime.strptime(row["entlassung_zeitpunkt"], "%Y-%m-%d %H:%M:%S")
            assert triage    >= admission, "Triage before admission"
            assert doctor    >= triage,   "Doctor contact before triage"
            assert discharge >  admission, "Discharge not after admission"

    def test_gcs_components_sum_to_total(self, sample_rows):
        for row in sample_rows:
            total  = row.get("gcs_gesamt", "")
            eyes   = row.get("gcs_augen", "")
            verbal = row.get("gcs_verbal", "")
            motor  = row.get("gcs_motorik", "")
            if total and eyes and verbal and motor:
                assert int(total) == int(eyes) + int(verbal) + int(motor), \
                    f"GCS mismatch: {total} != {eyes}+{verbal}+{motor}"

    def test_triage_level_in_valid_range(self, sample_rows):
        for row in sample_rows:
            assert row["triage_stufe"] in {"1", "2", "3", "4", "5"}

    def test_gender_valid_code(self, sample_rows):
        for row in sample_rows:
            assert row["geschlecht"] in {"M", "F", "W", "UN"}

    def test_discharge_code_valid(self, sample_rows):
        valid = {"1", "2", "3", "4", "5", "6", "S", "V"}
        for row in sample_rows:
            assert row["verbleib_nach_notaufnahme"] in valid

    def test_isolation_consistent(self, sample_rows):
        for row in sample_rows:
            if row["isolationsstatus"] == "0":
                assert row["isolationsgrund"] == ""

    def test_diagnostics_code_valid(self, sample_rows):
        for row in sample_rows:
            for col in ["labor_durchgefuehrt", "ekg_durchgefuehrt", "mrt_durchgefuehrt"]:
                assert row[col] in {"PB", "OPB"}, f"{col}={row[col]!r}"

    def test_reproducibility(self):
        a = generate_rows(count=3, seed=99)
        b = generate_rows(count=3, seed=99)
        assert [r["patientennummer"]     for r in a] == [r["patientennummer"]     for r in b]
        assert [r["aufnahme_zeitpunkt"]  for r in a] == [r["aufnahme_zeitpunkt"]  for r in b]

    def test_quarter_end(self):
        assert _quarter_end(dt.date(2025, 1, 15)) == "20250331"
        assert _quarter_end(dt.date(2025, 6, 30)) == "20250630"
        assert _quarter_end(dt.date(2025, 10, 1)) == "20251231"

    def test_secondary_diagnose_keys_present(self, sample_rows):
        for row in sample_rows:
            for n in range(2, 11):
                assert f"diagnose_{n}" in row
                assert f"diagnose_{n}_zusatzkennzeichen" in row


# ---------------------------------------------------------------------------
# column_mapper
# ---------------------------------------------------------------------------

class TestColumnMapper:

    def test_gender_w_maps_to_f(self, sample_row):
        row = dict(sample_row)
        row["geschlecht"] = "W"
        assert map_row(row)["gender"] == "F"

    def test_gender_m_stays_m(self, sample_row):
        row = dict(sample_row)
        row["geschlecht"] = "M"
        assert map_row(row)["gender"] == "M"

    def test_timestamp_format(self):
        assert _to_cda_ts("2025-05-01 10:23:00") == "20250501102300"

    def test_timestamp_empty(self):
        assert _to_cda_ts("") == ""

    def test_discharge_s_maps_to_verlegung(self, sample_row):
        row = dict(sample_row)
        row["verbleib_nach_notaufnahme"] = "S"
        fields = map_row(row)
        assert fields["verlegung_type"] == "5"
        assert fields["discharge"] == ""

    def test_discharge_v_maps_to_verlegung(self, sample_row):
        row = dict(sample_row)
        row["verbleib_nach_notaufnahme"] = "V"
        assert map_row(row)["verlegung_type"] == "6"

    def test_discharge_numeric_passthrough(self, sample_row):
        row = dict(sample_row)
        row["verbleib_nach_notaufnahme"] = "4"
        assert map_row(row)["discharge"] == "4"

    def test_allergy_present(self, sample_row):
        row = dict(sample_row)
        row["allergie_allgemein"] = "1"
        assert map_row(row)["allergy"] == "false"

    def test_allergy_absent(self, sample_row):
        row = dict(sample_row)
        row["allergie_allgemein"] = "0"
        assert map_row(row)["allergy"] == "true"

    def test_tetanus_present(self, sample_row):
        row = dict(sample_row)
        row["tetanusschutz"] = "1"
        assert map_row(row)["tetanus_vaccination"] == "false"

    def test_tetanus_absent(self, sample_row):
        row = dict(sample_row)
        row["tetanusschutz"] = "0"
        assert map_row(row)["tetanus_vaccination"] == "true"

    def test_tetanus_unknown(self, sample_row):
        row = dict(sample_row)
        row["tetanusschutz"] = ""
        assert map_row(row)["tetanus_vaccination"] == ""

    def test_auto_uuid_when_cda_id_missing(self, sample_row):
        row = dict(sample_row)
        row["cda_dokument_id"] = ""
        uuid.UUID(map_row(row)["document_id"])

    def test_triage_mts_oid(self, sample_row):
        row = dict(sample_row)
        row["triage_system"] = "MTS"
        assert map_row(row)["triage_system"] == "1.2.276.0.76.5.438"

    def test_triage_esi_oid(self, sample_row):
        row = dict(sample_row)
        row["triage_system"] = "ESI"
        assert map_row(row)["triage_system"] == "1.2.276.0.76.5.437"

    def test_vital_signs_ts_fallback(self, sample_row):
        row = dict(sample_row)
        row["triage_zeitpunkt"] = ""
        fields = map_row(row)
        assert fields["vital_signs_ts"] == fields["admission_ts"]

    def test_diagnosis_parsed(self, sample_row):
        row = dict(sample_row)
        row["icd10gm_code"] = "I21.9"
        row["diagnose_fuehrend_zusatzkennzeichen"] = "G"
        fields = map_row(row)
        assert fields["diagnosis_code_1"] == "I21.9"
        assert fields["diagnosis_qualifier_1"] == "G"

    def test_secondary_diagnosis_parsed(self, sample_row):
        row = dict(sample_row)
        row["diagnose_2"] = "E11.9"
        row["diagnose_2_zusatzkennzeichen"] = "A"
        fields = map_row(row)
        assert fields["diagnosis_code_2"] == "E11.9"
        assert fields["diagnosis_qualifier_2"] == "A"


# ---------------------------------------------------------------------------
# transformer
# ---------------------------------------------------------------------------

class TestTransformer:

    def test_produces_cda_root(self, cda_tree):
        assert etree.QName(cda_tree.getroot().tag).localname == "ClinicalDocument"

    def test_well_formed_xml(self, cda_tree):
        xml_bytes = etree.tostring(cda_tree.getroot(), xml_declaration=True, encoding="UTF-8")
        etree.fromstring(xml_bytes)

    def test_encounter_id_present(self, cda_tree, sample_row):
        enc = cda_tree.getroot().find(
            f".//{{{HL7}}}encompassingEncounter/{{{HL7}}}id"
        )
        assert enc is not None
        assert enc.get("extension") == sample_row["dokument_id"]

    def test_patient_id_present(self, cda_tree, sample_row):
        pat_id = cda_tree.getroot().find(f".//{{{HL7}}}patientRole/{{{HL7}}}id")
        assert pat_id is not None
        assert pat_id.get("extension") == sample_row["patientennummer"]

    def test_realm_code_de(self, cda_tree):
        rc = cda_tree.getroot().find(f"{{{HL7}}}realmCode")
        assert rc is not None
        assert rc.get("code") == "DE"


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

class TestFullPipeline:

    def test_100_rows_build_without_error(self):
        rows   = generate_rows(count=100, seed=7)
        failed = []
        for row in rows:
            enc_id = row.get("dokument_id", "?")
            try:
                fields    = map_row(row)
                tree      = transform(fields)
                xml_bytes = etree.tostring(tree.getroot(), encoding="UTF-8")
                etree.fromstring(xml_bytes)
            except Exception as exc:
                failed.append(f"{enc_id}: {exc}")
        assert not failed, "Build failures:\n" + "\n".join(failed)

    def test_unique_encounter_ids(self):
        rows = generate_rows(count=50, seed=3)
        ids  = [r["dokument_id"] for r in rows]
        assert len(ids) == len(set(ids))

    def test_unique_cda_document_ids(self):
        rows = generate_rows(count=50, seed=3)
        ids  = [r["cda_dokument_id"] for r in rows]
        assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Empirical helpers  (in-memory DataFrames — no real AKTIN data needed)
# ---------------------------------------------------------------------------

class TestEmpiricalStubs:

    @pytest.fixture
    def minimal_dist(self):
        """Minimal distribution dict produced by _analyze_case_data on tiny data."""
        import pandas as pd
        df = pd.DataFrame({
            "aufnahme_ts":        ["2024-06-01 08:00:00", "2024-06-02 14:30:00", "2024-06-03 20:15:00"],
            "entlassung_ts":      ["2024-06-01 10:30:00", "2024-06-02 18:00:00", "2024-06-04 02:00:00"],
            "triage_ts":          ["2024-06-01 08:05:00", "2024-06-02 14:35:00", "2024-06-03 20:20:00"],
            "start_arztkontakt_ts":["2024-06-01 08:20:00","2024-06-02 15:00:00","2024-06-03 20:45:00"],
            "geschlecht":         ["M", "F", "M"],
            "triage":             [3.0, 2.0, 4.0],
            "cedis":              ["201", "301", "401"],
            "triagesystem":       ["MTS", "ESI", "MTS"],
            "zuweisung":          ["Rettungsdienst", "Vertragsarzt/Praxis", "Notarzt"],
            "transport":          ["RTW", "Ohne", "KTW"],
            "verbleib":           ["Entlassung nach Hause", "Aufnahme auf Normalstation", "Entlassung nach Hause"],
            "atemfrequenz":       [18, 22, 16],
            "saettigung":         [97, 95, 98],
            "blutdruck_sys":      [130, 145, 120],
            "herzfrequenz":       [78, 88, 72],
            "kerntemperatur":     [36.8, 37.2, 36.5],
            "gcs_summe":          [15, 14, 15],
            "gcs_augen":          [4, 4, 4],
            "gcs_verbal":         [5, 4, 5],
            "gcs_motorisch":      [6, 6, 6],
        })
        return _analyze_case_data(df)

    @pytest.fixture
    def minimal_ddiag(self):
        import pandas as pd
        df = pd.DataFrame({
            "a_encounter_num": [1, 1, 2, 3],
            "icd_code":        ["I21.9", "I10", "R55", "J18.9"],
            "diagnose_zusatz": ["G", "G", "G", "G"],
        })
        return _analyze_diag_data(df)

    def test_analyze_case_returns_expected_keys(self, minimal_dist):
        for key in ("num", "cat", "missing", "hour_weights", "los_samples",
                    "triage_offsets", "ak_offsets", "proc_absence"):
            assert key in minimal_dist

    def test_analyze_case_los_samples_positive(self, minimal_dist):
        for v in minimal_dist["los_samples"]:
            assert v >= 0

    def test_analyze_case_hour_weights_24_entries(self, minimal_dist):
        assert len(minimal_dist["hour_weights"]) == 24

    def test_analyze_diag_icd_codes_present(self, minimal_ddiag):
        assert "I21.9" in minimal_ddiag["icd_codes"]
        assert "R55" in minimal_ddiag["icd_codes"]

    def test_empirical_row_builds_valid_cda(self, minimal_dist, minimal_ddiag):
        import random
        random.seed(0)
        start = dt.date(2024, 1, 1)
        end   = dt.date(2024, 12, 31)
        kw = dict(
            org_id="1.2.276.0.76.4.17.9999", org_name="Test",
            org_street="Str", org_house="1", org_city="Berlin",
            org_plz="10115", org_state="Berlin", org_phone="",
            org_email="", author_id="A-1", author_prefix="Dr.",
            author_first="Max", author_last="Muster",
        )
        row    = _empirical_one(1, minimal_dist, minimal_ddiag, start, end, **kw)
        fields = map_row(row)
        tree   = transform(fields)
        xml_bytes = etree.tostring(tree.getroot(), encoding="UTF-8")
        etree.fromstring(xml_bytes)  # must not raise

    def test_empirical_gcs_consistent(self, minimal_dist, minimal_ddiag):
        import random
        random.seed(42)
        start = dt.date(2024, 1, 1)
        end   = dt.date(2024, 12, 31)
        kw = dict(
            org_id="1.2.276.0.76.4.17.9999", org_name="Test",
            org_street="Str", org_house="1", org_city="Berlin",
            org_plz="10115", org_state="Berlin", org_phone="",
            org_email="", author_id="A-1", author_prefix="Dr.",
            author_first="Max", author_last="Muster",
        )
        for i in range(1, 6):
            row = _empirical_one(i, minimal_dist, minimal_ddiag, start, end, **kw)
            total  = row.get("gcs_gesamt", "")
            eyes   = row.get("gcs_augen", "")
            verbal = row.get("gcs_verbal", "")
            motor  = row.get("gcs_motorik", "")
            if total and eyes and verbal and motor:
                assert int(total) == int(eyes) + int(verbal) + int(motor)


# ---------------------------------------------------------------------------
# Anonymize helpers  (in-memory DataFrames — no real AKTIN data needed)
# ---------------------------------------------------------------------------

class TestAnonymizeStubs:

    @pytest.fixture
    def src_row(self):
        """Minimal pandas Series mimicking one case_data.txt row."""
        import pandas as pd
        return pd.Series({
            "aufnahme_ts":          "2024-03-15 10:00:00",
            "entlassung_ts":        "2024-03-15 13:30:00",
            "start_arztkontakt_ts": "2024-03-15 10:25:00",
            "triage_ts":            "2024-03-15 10:05:00",
            "a_encounter_num":      "ENC-001",
            "age_in_years":         55,
            "geschlecht":           "M",
            "triage":               3.0,
            "cedis":                "201",
            "triagesystem":         "MTS",
            "zuweisung":            "Rettungsdienst",
            "transport":            "RTW",
            "verbleib":             "Entlassung nach Hause",
            "atemfrequenz":         18,
            "blutdruck_sys":        130,
            "herzfrequenz":         78,
        })

    @pytest.fixture
    def src_diag_lookup(self):
        return {"ENC-001": [("I21.9", "G"), ("I10", "G")]}

    def test_anonymize_row_builds_valid_cda(self, src_row, src_diag_lookup):
        import random
        random.seed(5)
        kw = dict(
            org_id="1.2.276.0.76.4.17.9999", org_name="Test",
            org_street="Str", org_house="1", org_city="Berlin",
            org_plz="10115", org_state="Berlin", org_phone="",
            org_email="", author_id="A-1", author_prefix="Dr.",
            author_first="Max", author_last="Muster",
        )
        row    = _anonymize_one(1, src_row, src_diag_lookup, 30, 2, **kw)
        fields = map_row(row)
        tree   = transform(fields)
        xml_bytes = etree.tostring(tree.getroot(), encoding="UTF-8")
        etree.fromstring(xml_bytes)

    def test_anonymize_row_same_calendar_month(self, src_row, src_diag_lookup):
        import random
        random.seed(7)
        kw = dict(
            org_id="1.2.276.0.76.4.17.9999", org_name="Test",
            org_street="Str", org_house="1", org_city="Berlin",
            org_plz="10115", org_state="Berlin", org_phone="",
            org_email="", author_id="A-1", author_prefix="Dr.",
            author_first="Max", author_last="Muster",
        )
        row = _anonymize_one(1, src_row, src_diag_lookup, 30, 2, **kw)
        admission = dt.datetime.strptime(row["aufnahme_zeitpunkt"], "%Y-%m-%d %H:%M:%S")
        # Original was 2024-03; year/month may shift slightly due to jitter but should stay near
        assert admission.year == 2024
        assert admission.month == 3

    def test_anonymize_diagnoses_from_lookup(self, src_row, src_diag_lookup):
        import random
        random.seed(9)
        kw = dict(
            org_id="1.2.276.0.76.4.17.9999", org_name="Test",
            org_street="Str", org_house="1", org_city="Berlin",
            org_plz="10115", org_state="Berlin", org_phone="",
            org_email="", author_id="A-1", author_prefix="Dr.",
            author_first="Max", author_last="Muster",
        )
        row = _anonymize_one(1, src_row, src_diag_lookup, 30, 2, **kw)
        assert row["icd10gm_code"] == "I21.9"
        assert row["diagnose_2"]   == "I10"

    def test_anonymize_pii_cleared(self, src_row, src_diag_lookup):
        import random
        random.seed(11)
        kw = dict(
            org_id="1.2.276.0.76.4.17.9999", org_name="Test",
            org_street="Str", org_house="1", org_city="Berlin",
            org_plz="10115", org_state="Berlin", org_phone="",
            org_email="", author_id="A-1", author_prefix="Dr.",
            author_first="Max", author_last="Muster",
        )
        row = _anonymize_one(1, src_row, src_diag_lookup, 30, 2, **kw)
        for pii_col in ("patient_vorname", "patient_nachname", "patient_strasse"):
            assert row[pii_col] == "", f"{pii_col} should be empty"

    def test_build_diag_lookup(self):
        import pandas as pd
        df = pd.DataFrame({
            "a_encounter_num": ["E1", "E1", "E2"],
            "icd_code":        ["I21.9", "I10", "R55"],
            "diagnose_zusatz": ["G", "G", "V"],
        })
        lookup = _build_diag_lookup(df)
        assert lookup["E1"] == [("I21.9", "G"), ("I10", "G")]
        assert lookup["E2"] == [("R55", "V")]
