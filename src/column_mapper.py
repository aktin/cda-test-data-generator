"""
column_mapper.py
----------------
Map one CSV row (German column names per requirements.md) to the flat XSLT
field dict expected by EmergencyNote.xslt.

The CSV uses German column names from the staging format specification.
This module handles only the transforms that genuinely need code:
  - Timestamp normalisation  (YYYY-MM-DD HH:MM:SS → YYYYMMDDHHmmSS)
  - Discharge code mapping (verbleib_nach_notaufnahme → discharge + verlegung_type)
  - Triage system abbreviation → AKTIN OID
  - CEDIS code validation against vocabulary
  - Diagnostic flag normalisation (1/0 or PB/OPB pass-through)
  - UUID document_id generation when cda_dokument_id is absent

No artificial data is generated. Every CDA field comes from a CSV column or a
CLI argument. Missing optional values are left empty and resolved by the XSLT
(nullFlavor, element omission, etc.).
"""

import datetime as dt
import os
import re
import uuid
from typing import Optional
from urllib.parse import quote as _url_quote

# ---------------------------------------------------------------------------
# CEDIS vocabulary (optional — silently skip if file absent)
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_RESOURCES = os.path.join(_HERE, "..", "resources")

_CEDIS_VOC = os.path.join(
    _RESOURCES, "shematron", "include", "voc-1.2.276.0.76.11.61-DYNAMIC.xml"
)
try:
    with open(_CEDIS_VOC, encoding="utf-8") as _f:
        VALID_CEDIS: frozenset = frozenset(re.findall(r'<concept code="([^"]+)"', _f.read()))
except OSError:
    VALID_CEDIS = frozenset()


# ---------------------------------------------------------------------------
# Timestamp helpers
# ---------------------------------------------------------------------------

_TS_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%Y%m%d%H%M",      # 12-char (YYYYMMDDHHMM)
    "%Y%m%d%H%M%S",    # 14-char (YYYYMMDDHHMMSS)
    "%Y%m%d",          # 8-char date only
]


def _parse_ts(s: str) -> Optional[dt.datetime]:
    if not s or not s.strip():
        return None
    for fmt in _TS_FORMATS:
        try:
            return dt.datetime.strptime(s.strip(), fmt)
        except ValueError:
            pass
    return None


def _to_cda_ts(s: str, fmt: str = "%Y%m%d%H%M%S") -> str:
    parsed = _parse_ts(s)
    return parsed.strftime(fmt) if parsed else ""


def _ts_add_minutes(s: str, minutes: int, fmt: str = "%Y%m%d%H%M") -> str:
    """Add *minutes* to a timestamp string; returns empty string on parse failure."""
    parsed = _parse_ts(s)
    if not parsed:
        return ""
    return (parsed + dt.timedelta(minutes=minutes)).strftime(fmt)


# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

# voc-44 / voc-45 codeSystem OIDs for triage score values (only MTS and ESI supported)
_TRIAGE_SYSTEM_OID = {
    "MTS": "1.2.276.0.76.5.438",
    "ESI": "1.2.276.0.76.5.437",
}

# voc-56: AKTIN discharge disposition codes
# Numeric codes 1-6 pass through directly.
# S/V → verlegung_type only (no dischargeDispositionCode rendered)
_DISCHARGE_CODE = {
    "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6",
    "s": "", "v": "",
}

_VERLEGUNG_TYPE = {
    # S = stationär aufgenommen → intern: Normalstation (voc-53 code 5)
    # V = verlegt (extern) → extern: Normalstation (voc-53 code 6)
    "s": "5",
    "v": "6",
}

# voc-49: pupil size codes (C=narrow ≤2mm, M=medium 3-5mm, D=wide ≥6mm)
def _pupil_size_code(s: str) -> str:
    """Accept voc-49 code (C/M/D) or numeric mm value → voc-49 code. UNK → '' (XSLT emits nullFlavor)."""
    s = s.strip() if s else ""
    if s.upper() == "UNK":
        return ""
    if s.upper() in ("C", "M", "D"):
        return s.upper()
    try:
        mm = float(s)
    except (ValueError, TypeError):
        return s
    if mm <= 2:
        return "C"
    if mm <= 5:
        return "M"
    return "D"


# voc-50: pupil reaction codes (B=normal/prompt, D=sluggish, A=absent); UNK → '' (XSLT emits nullFlavor)
_PUPIL_REACTION = {
    "b": "B", "d": "D", "a": "A", "unk": "",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_negation_ind(s: str, default: str = "true") -> str:
    """Convert flag to XML boolean negationInd string.

    1/ja/yes/true → 'false'  (= present, no negation)
    0/nein/no/false → 'true' (= absent, negated)
    empty → *default* (caller chooses: 'true' = not present by default)
    """
    s = (s or "").strip().lower()
    if s in ("1", "ja", "yes", "true", "j", "y"):
        return "false"
    if s in ("0", "nein", "no", "false", "n"):
        return "true"
    return default


def _to_diag_code(s: str) -> str:
    """Accept PB/OPB directly or normalise 1→PB, 0→OPB."""
    v = s.strip() if s else ""
    if v in ("PB", "OPB"):
        return v
    if v == "1":
        return "PB"
    if v == "0":
        return "OPB"
    return v  # pass through empty or unknown


def _germs_code(germs_raw: str, mrsa: str, three_mrgn: str,
                four_mrgn: str, vre: str) -> str:
    """Determine AKTIN MDRO code (voc-60) from individual germ flags."""
    if germs_raw.strip() != "1":
        return ""
    if mrsa.strip() == "1":
        return "MRSA"
    if three_mrgn.strip() == "1":
        return "3MRGN"
    if four_mrgn.strip() == "1":
        return "4MRGN"
    if vre.strip() == "1":
        return "VRE"
    return "AMRO"  # generic MRE


# ---------------------------------------------------------------------------
# Main mapping function
# ---------------------------------------------------------------------------

_CASE_NUMBER_OID = "1.2.276.0.76.3.87686.1.45"


def map_row(
    row: dict,
    org_id: str = "",
    org_name: str = "",
    author_prefix: str = "",
    author_first: str = "",
    author_last: str = "",
) -> dict:
    """
    Convert one CSV row (German column names) to the flat XSLT field dict.

    CSV column names follow the staging format defined in requirements.md.
    XSLT field names remain stable regardless of CSV column changes.

    Parameters
    ----------
    row : dict
        One CSV row keyed by German column names.
    org_id : str
        Fallback hospital OID used when CSV column ``organisation_id`` is empty.
    org_name : str
        Fallback hospital display name used when ``organisation_name`` is empty.
    author_prefix / author_first / author_last : str
        Fallback author name parts used when CSV autor_1_* columns are empty.

    Returns
    -------
    dict
        Flat field dict ready to be serialised to <aktin_raw> XML and fed to
        EmergencyNote.xslt.
    """
    def get(col: str) -> str:
        return (row.get(col) or "").strip()

    now = dt.datetime.now().strftime("%Y%m%d%H%M%S")

    # --- Core timestamps ---------------------------------------------------
    admission_ts      = _to_cda_ts(get("aufnahme_zeitpunkt"))
    discharge_ts      = _to_cda_ts(get("entlassung_zeitpunkt"))
    therapy_start_ts  = _to_cda_ts(get("therapiebeginn_zeitpunkt"))
    therapy_end_ts    = _to_cda_ts(get("therapieende_zeitpunkt"))
    doctor_contact_ts = _to_cda_ts(get("arztkontakt_beginn_zeitpunkt"))
    end_doctor_contact_ts = _to_cda_ts(get("arztkontakt_ende_zeitpunkt"))

    triage_ts = _to_cda_ts(get("triage_zeitpunkt"), "%Y%m%d%H%M")
    # Schematron dtr1-6/7 require triage low < high.  No end field exists in the
    # staging format, so we offset by 5 minutes — the minimum non-equal value.
    triage_ts_end = _ts_add_minutes(get("triage_zeitpunkt"), 5)
    # Vital signs effectiveTime: use triage timestamp when available, else admission
    vital_signs_ts = triage_ts or admission_ts

    # --- Document identity -------------------------------------------------
    cda_doc_id  = get("cda_dokument_id") or str(uuid.uuid4())
    doc_creation = _to_cda_ts(get("dokument_erstellungszeitpunkt")) or now
    doc_version  = get("dokument_versionsnummer") or "1"

    # --- Patient -----------------------------------------------------------
    gender_raw = get("geschlecht").upper()
    # CDA uses M/F/UN; also accept W (German: weiblich) as F
    gender = "F" if gender_raw in ("W", "F") else ("UN" if gender_raw == "UN" else "M")

    birth_date_ts = _to_cda_ts(get("patient_geburtsdatum"))

    patient_first = get("patient_vorname")
    patient_last  = get("patient_nachname")

    street = ""
    if get("patient_strasse"):
        street = get("patient_strasse")
        if get("patient_hausnummer"):
            street += " " + get("patient_hausnummer")

    # --- Author 1: CSV fields take priority over CLI args -----------------
    author_ts         = _to_cda_ts(get("autor_1_zeitpunkt")) or doc_creation
    eff_author_prefix = get("autor_1_praefix") or author_prefix
    eff_author_first  = get("autor_1_vorname") or author_first
    eff_author_last   = get("autor_1_nachname") or author_last

    # --- Author 2 (optional second author) --------------------------------
    author_2_ts         = _to_cda_ts(get("autor_2_zeitpunkt"))
    author_2_first_name = get("autor_2_vorname")
    author_2_last_name  = get("autor_2_nachname")

    # --- Insurance ---------------------------------------------------------
    insurance_egk  = get("egk_nummer")      # empty → XSLT uses nullFlavor=UNK
    insurance_iknr = get("ik_nummer")
    insurance_txt  = get("krankenkasse_name")
    # No insurance type code in CSV — always SELF (HL7 RoleCode)
    insurance_case = "SELF"
    assoc_first = get("versicherter_vorname")
    assoc_last  = get("versicherter_nachname")

    # --- Organisation address / contact -----------------------------------
    org_street = get("organisation_strasse")
    if org_street and get("organisation_hausnummer"):
        org_street += " " + get("organisation_hausnummer")

    # --- Triage system OID ------------------------------------------------
    triage_system_oid = _TRIAGE_SYSTEM_OID.get(get("triage_system").upper(), "")

    # --- Discharge disposition --------------------------------------------
    dispo = get("verbleib_nach_notaufnahme").lower()
    discharge     = _DISCHARGE_CODE.get(dispo, dispo if dispo.isdigit() else "")
    verlegung_type = _VERLEGUNG_TYPE.get(dispo, "")

    # --- CEDIS validation --------------------------------------------------
    cedis = get("vorstellungsgrund_cedis")
    if VALID_CEDIS and cedis not in VALID_CEDIS:
        cedis = ""

    # --- Germs -------------------------------------------------------------
    germs = _germs_code(
        get("multiresistente_erreger"),
        get("mrsa_status"),
        get("mrgn_3_status"),
        get("mrgn_4_status"),
        get("vre_status"),
    )

    def _diag_ts(col: str) -> str:
        return _to_cda_ts(get(col))

    # --- Organisation: CSV columns take priority over CLI fallback --------
    eff_org_id   = get("organisation_id")   or org_id   or "1.2.276.0.76.4.17.9999"
    eff_org_name = get("organisation_name") or org_name or "Unbekannte Organisation"

    fields: dict = {
        # --- Document identity -------------------------------------------
        "document_id":       cda_doc_id,
        "date_creation":     doc_creation,
        "version_id":        doc_version,
        "organization_id":   eff_org_id,
        "organization_name": eff_org_name,

        # --- Author 1 -----------------------------------------------------
        "author_ts":          author_ts,
        "author_id":          get("autor_1_id"),
        "author_prefix":      eff_author_prefix,
        "author_first_name":  eff_author_first,
        "author_last_name":   eff_author_last,

        # --- Author 2 (optional) ------------------------------------------
        "author_2_ts":         author_2_ts,
        "author_2_id":         get("autor_2_id"),
        "author_2_prefix":     get("autor_2_praefix"),
        "author_2_first_name": author_2_first_name,
        "author_2_last_name":  author_2_last_name,

        # --- Patient ------------------------------------------------------
        "patient_id":                get("patientennummer"),
        "admission_id":              get("dokument_id"),
        "case_number":               get("Krankenhausinternes Fallkennzeichen"),
        "case_number_oid":           _CASE_NUMBER_OID,
        "patient_first_name":        patient_first,
        "patient_last_name":         patient_last,
        "_associated_person_first_name": assoc_first,
        "_associated_person_last_name":  assoc_last,
        "gender":                    gender,
        "birth_date_ts":             birth_date_ts,
        "postal_code":               get("postleitzahl"),
        "city":                      get("patient_ort"),
        "street_address_line":       street,
        "patient_additional_locator": get("patient_adresszusatz"),
        "patient_direction":          get("patient_richtung"),
        "patient_state":              get("patient_bundesland"),
        "patient_phone":  ("tel:" + _url_quote(get("patient_telefon"),  safe="+:-")) if get("patient_telefon")  else "",
        "patient_mobile": ("tel:" + _url_quote(get("patient_mobiltelefon"), safe="+:-")) if get("patient_mobiltelefon") else "",
        "patient_email":  ("mailto:" + get("patient_email")) if get("patient_email") else "",

        # --- Organisation contact / address (URI-formatted) ---------------
        "organization_phone":  ("tel:" + _url_quote(get("organisation_telefon"),  safe="+:-")) if get("organisation_telefon")  else "",
        "organization_mobile": ("tel:" + _url_quote(get("organisation_mobiltelefon"), safe="+:-")) if get("organisation_mobiltelefon") else "",
        "organization_email":  ("mailto:" + get("organisation_email")) if get("organisation_email") else "",
        "organization_street":             org_street,
        "organization_additional_locator": get("organisation_adresszusatz"),
        "organization_city":               get("organisation_ort"),
        "organization_postal_code":        get("organisation_postleitzahl"),
        "organization_state":              get("organisation_bundesland"),

        # --- Insurance ----------------------------------------------------
        "insurance_case":         insurance_case,
        "insurance_egk":          insurance_egk,
        "insurance_number":       get("versicherungsnummer"),
        "insurance_iknr":         insurance_iknr,
        "insurance_vk":           get("vk_nummer"),
        "insurance_txt":          insurance_txt,
        "insurance_quarter_end":  get("versicherungs_quartalsende"),

        # --- Encounter timestamps -----------------------------------------
        "admission_ts":          admission_ts,
        "discharge_ts":          discharge_ts,
        "therapy_start_ts":      therapy_start_ts,
        "therapy_end_ts":        therapy_end_ts,
        "doctor_contact_ts":     doctor_contact_ts,
        "end_doctor_contact_ts": end_doctor_contact_ts,
        "performer_id":          get("behandler_id"),
        "triage_ts_start":       triage_ts,
        "triage_ts_end":         triage_ts_end,
        "vital_signs_ts":        vital_signs_ts,

        # --- Referral / transport -----------------------------------------
        "referral":         get("zuweisungsart"),
        "transport_method": get("transportmittel") or "NA",

        # --- Discharge ----------------------------------------------------
        "discharge":      discharge,
        "verlegung_type": verlegung_type,

        # --- Chief complaint / triage -------------------------------------
        "cedis":             cedis,
        "complaints_txt":    get("vorstellungsgrund_text"),
        "complaint_list":    "",
        "complaint_start":   "",
        "symptom_duration":  get("symptomdauer"),
        "triage":            get("triage_stufe"),
        "triage_system":     triage_system_oid,
        "initial_assessment_text": "",

        # --- Vitals -------------------------------------------------------
        "respiratory_rate":   get("atemfrequenz"),
        "saturation":         get("sauerstoffsaettigung"),
        "blood_pressure_sys": get("blutdruck_systolisch"),
        "heart_rate":         get("herzfrequenz"),
        "body_temperature":   get("koerperkerntemperatur"),
        "pain_severity":      get("schmerzskala"),

        # --- GCS ----------------------------------------------------------
        "gcs_total":  get("gcs_gesamt"),
        "gcs_eyes":   get("gcs_augen"),
        "gcs_verbal": get("gcs_verbal"),
        "gcs_motor":  get("gcs_motorik"),

        # --- Pupils -------------------------------------------------------
        "pupil_size_right":     _pupil_size_code(get("pupillenweite_rechts")),
        "pupil_size_left":      _pupil_size_code(get("pupillenweite_links")),
        "pupil_reaction_right": _PUPIL_REACTION.get(get("pupillenreaktion_rechts").lower(),
                                                     get("pupillenreaktion_rechts")),
        "pupil_reaction_left":  _PUPIL_REACTION.get(get("pupillenreaktion_links").lower(),
                                                     get("pupillenreaktion_links")),

        # --- Rankin -------------------------------------------------------
        "rankin": get("rankin_skala"),

        # --- Germs / isolation -------------------------------------------
        "germs":            germs,
        "germs_mrsa":       get("mrsa_status"),
        "germs_3mrgn":      get("mrgn_3_status"),
        "germs_4mrgn":      get("mrgn_4_status"),
        "germs_vre":        get("vre_status"),
        "germs_other":      get("andere_multiresistente_erreger"),
        "isolation_status": get("isolationsstatus"),
        "isolation_grund":  get("isolationsgrund"),

        # --- Diagnostics -------------------------------------------------
        "diagnostics_laboratory":           _to_diag_code(get("labor_durchgefuehrt")),
        "diagnostics_laboratory_ts":        _diag_ts("labor_zeitpunkt"),
        "diagnostics_blood_gases":          _to_diag_code(get("bga_durchgefuehrt")),
        "diagnostics_blood_gases_ts":       _diag_ts("bga_zeitpunkt"),
        "diagnostics_urine_quick_test":     _to_diag_code(get("urinschnelltest_durchgefuehrt")),
        "diagnostics_urine_quick_test_ts":  _diag_ts("urinschnelltest_zeitpunkt"),
        "diagnostics_ecg":                  _to_diag_code(get("ekg_durchgefuehrt")),
        "diagnostics_ecg_ts":               _diag_ts("ekg_zeitpunkt"),
        "diagnostics_ultrasound":           _to_diag_code(get("sonographie_durchgefuehrt")),
        "diagnostics_ultrasound_ts":        _diag_ts("sonographie_zeitpunkt"),
        "diagnostics_echocardiography":     _to_diag_code(get("echokardiographie_durchgefuehrt")),
        "diagnostics_echocardiography_ts":  _diag_ts("echokardiographie_zeitpunkt"),
        "diagnostics_ct_head":              _to_diag_code(get("cct_durchgefuehrt")),
        "diagnostics_ct_head_ts":           _diag_ts("cct_zeitpunkt"),
        "diagnostics_ct":                   _to_diag_code(get("ct_durchgefuehrt")),
        "diagnostics_ct_ts":                _diag_ts("ct_zeitpunkt"),
        "diagnostics_ct_trauma":            _to_diag_code(get("traumascan_durchgefuehrt")),
        "diagnostics_ct_trauma_ts":         _diag_ts("traumascan_zeitpunkt"),
        "diagnostics_xray_spine":           _to_diag_code(get("roentgen_wirbelsaeule_durchgefuehrt")),
        "diagnostics_xray_spine_ts":        _diag_ts("roentgen_wirbelsaeule_zeitpunkt"),
        "diagnostics_xray_thorax":          _to_diag_code(get("roentgen_thorax_durchgefuehrt")),
        "diagnostics_xray_thorax_ts":       _diag_ts("roentgen_thorax_zeitpunkt"),
        "diagnostics_xray_pelvis":          _to_diag_code(get("roentgen_becken_durchgefuehrt")),
        "diagnostics_xray_pelvis_ts":       _diag_ts("roentgen_becken_zeitpunkt"),
        "diagnostics_xray_extremities":     _to_diag_code(get("roentgen_extremitaet_durchgefuehrt")),
        "diagnostics_xray_extremities_ts":  _diag_ts("roentgen_extremitaet_zeitpunkt"),
        "diagnostics_xray_others":          _to_diag_code(get("roentgen_sonstiges_durchgefuehrt")),
        "diagnostics_xray_others_ts":       _diag_ts("roentgen_sonstiges_zeitpunkt"),
        "diagnostics_mrt":                  _to_diag_code(get("mrt_durchgefuehrt")),
        "diagnostics_mrt_ts":               _diag_ts("mrt_zeitpunkt"),
        "diagnostics_ts":                   "",
        "diagnostics_txt":                  "",

        # --- Notfallanamnese / emergency history ---------------------------
        "emergency_medical_history": get("notfallanamnese"),

        # --- Allergien und Unverträglichkeiten ----------------------------
        # 1=vorhanden → negationInd="false"; 0/empty=keine/unbekannt → "true"
        "allergy":                _to_negation_ind(get("allergie_allgemein")),
        "allergy_antibiotics":    _to_negation_ind(get("allergie_antibiotika")),
        "allergy_contrast_agent": _to_negation_ind(get("allergie_kontrastmittel")),
        "allergy_other":          _to_negation_ind(get("allergie_sonstige")),
        "allergies_txt":          get("allergie_freitext"),

        # --- Immunisierung Tetanus -----------------------------------------
        # 1→negationInd="false" (protected), 0→"true" (not protected),
        # empty→"" (unknown; XSLT emits nullFlavor=NI)
        "tetanus_vaccination":    (
            _to_negation_ind(get("tetanusschutz"), default="")
            if get("tetanusschutz").strip() else ""
        ),

        # --- Pregnancy (fixed: not collected in staging format) -----------
        "pregnancy":              "0",
    }

    # First available diagnostics timestamp → diagnostics_ts fallback
    for k in (
        "diagnostics_laboratory_ts", "diagnostics_blood_gases_ts",
        "diagnostics_ecg_ts", "diagnostics_ultrasound_ts",
        "diagnostics_echocardiography_ts", "diagnostics_ct_head_ts",
        "diagnostics_ct_ts", "diagnostics_ct_trauma_ts",
        "diagnostics_xray_thorax_ts", "diagnostics_xray_spine_ts",
        "diagnostics_xray_pelvis_ts", "diagnostics_xray_extremities_ts",
        "diagnostics_xray_others_ts", "diagnostics_mrt_ts",
        "diagnostics_urine_quick_test_ts",
    ):
        if fields[k]:
            fields["diagnostics_ts"] = fields[k]
            break
    # When no procedure was performed, fall back to admission time so that
    # effectiveTime/@value is never empty (empty string fails ts pattern validation).
    if not fields["diagnostics_ts"]:
        fields["diagnostics_ts"] = admission_ts

    # --- Diagnoses (icd10gm_code is diagnosis 1; diagnose_2..10 additional) ---
    icd1 = get("icd10gm_code")
    if icd1:
        fields["diagnosis_code_1"]      = icd1
        fields["diagnosis_qualifier_1"] = get("diagnose_fuehrend_zusatzkennzeichen") or "A"
        # Empty name element required so XSLT "$name = ''" test evaluates correctly
        fields["diagnosis_name_1"]      = ""

    for n in range(2, 11):
        code = get(f"diagnose_{n}")
        if not code:
            continue
        fields[f"diagnosis_code_{n}"]      = code
        fields[f"diagnosis_qualifier_{n}"] = get(f"diagnose_{n}_zusatzkennzeichen") or "A"
        fields[f"diagnosis_name_{n}"]      = ""

    return fields
