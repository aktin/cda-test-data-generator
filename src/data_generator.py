"""
data_generator.py
-----------------
Three-mode synthetic CDA data generator using the csv2cda staging format.

Modes
~~~~~
synthetic  (default)
    Pure random generation with clinically plausible distributions.
    No external data required.  Zero extra dependencies.

empirical
    Reads AKTIN raw exports (case_data.txt + diag_data.txt), learns empirical
    distributions (admission-hour weights, LOS, vital-sign distributions,
    categorical frequencies, procedure absence rates, ICD-code frequencies),
    and generates N synthetic rows that statistically resemble the source data.
    Requires ``pandas>=1.3``.

anonymize
    Reads AKTIN raw exports, produces one anonymised output row per input row
    (or a random sample when n < total rows):
      - Random day reassigned within the same calendar month.
      - Admission time jittered by ±time_jitter_minutes (default 30 min).
      - LOS and inter-event offsets (triage, doctor contact) preserved exactly.
      - Numeric vitals jittered by small Gaussian noise.
      - GCS scores kept intact (discrete ordinal).
      - All PII (names, addresses, document IDs) freshly generated.
      - Diagnoses matched from diag_data.txt via encounter key.
    Requires ``pandas>=1.3``.

All modes return ``list[dict]`` with German staging-CSV column names matching
the DATA_DICTIONARY, ready for ``column_mapper.map_row``.
"""

import calendar
import csv
import datetime as dt
import os
import random
import uuid

# ---------------------------------------------------------------------------
# CEDIS vocabulary (loaded from resources/cedis.csv)
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_RESOURCES = os.path.join(_HERE, "..", "resources")

_CEDIS_FALLBACK = [
    ("001", "Herzstillstand (nicht traumatisch)"),
    ("003", "Brustschmerz (kardial)"),
    ("004", "Brustschmerz (nicht kardial)"),
    ("007", "Allgemeine Schwäche"),
    ("008", "Synkope/Präsynkope"),
    ("201", "Kopfschmerz"),
    ("211", "Schwindel"),
    ("301", "Bauchschmerz"),
    ("401", "Rückenschmerz"),
    ("501", "Wunde/Schürfwunde"),
]


def _load_cedis() -> list:
    path = os.path.join(_RESOURCES, "cedis.csv")
    try:
        with open(path, encoding="utf-8") as f:
            return [(r["cedis"], r["display_name"])
                    for r in csv.DictReader(f, delimiter=";")]
    except OSError:
        return _CEDIS_FALLBACK


_CEDIS: list = _load_cedis()
_CEDIS_CODES: list = [c for c, _ in _CEDIS]

# ---------------------------------------------------------------------------
# Isolation grund: display name → ICD-10 / voc-55 code mapping
# case_data.txt stores the German display name; the XSLT expects the code.
# ---------------------------------------------------------------------------
_ISOLATION_GRUND_MAP = {
    "multiresistenter Keim": "U80",
    "Gastroenteritis":       "A09.9",
    "Tuberkulose":           "A16.9",
    "Meningitis":            "G03.9",
    "Andere":                "OTH",
}

# ---------------------------------------------------------------------------
# Raw AKTIN → staging CSV column mappings  (used by empirical + anonymize)
# ---------------------------------------------------------------------------

# (staging_col, {raw_value: staging_value} or None for passthrough)
_RAW_TO_STAGING_CAT = {
    "geschlecht":              ("geschlecht",               {"M": "M", "F": "F", "W": "W", "X": "UN"}),
    "zuweisung":               ("zuweisungsart",            {
        "Vertragsarzt/Praxis":                        "VAP",
        "KV-Notfallpraxis am Krankenhaus":            "KVNPIK",
        "KV-Notdienst ausserhalb des Krankenhauses":  "KVNDAK",
        "Rettungsdienst":                             "RD",
        "Notarzt":                                    "NA",
        "Klinik/Verlegung":                           "KLINV",
        "Zuweisung nicht durch Arzt":                 "NPHYS",
        "Andere":                                     "OTH",
    }),
    "transport":               ("transportmittel",          {
        "KTW":         "1",
        "RTW":         "2",
        "NAW/NEF/ITW": "3",
        "RTH/ITH":     "4",
        "Ohne":        "NA",
        "Andere":      "OTH",
    }),
    "cedis":                   ("vorstellungsgrund_cedis",   None),
    "triage":                  ("triage_stufe",              None),   # float → int str; special
    "triagesystem":            ("triage_system",             None),   # keep MTS/ESI; mapper adds OID
    "verbleib":                ("verbleib_nach_notaufnahme", {
        "Tod":                                          "1",
        "Entlassung gegen aerztlichen Rat":             "2",
        "Behandlung durch Pat. abgebrochen":            "3",
        "Sonstige Entlassung":                          "3",
        "Entlassung nach Hause":                        "4",
        "Entlassung zu weiterbehandelnden Arzt":        "5",
        "Aufnahme auf Normalstation":                   "S",
        "Aufnahme auf Ueberwachungsstation":            "S",
        "Aufnahme in Funktionsbereich":                 "S",
        "kein Arztkontakt":                             "6",
        "Verlegung extern in Funktionsbereich":         "V",
        "Verlegung extern auf Ueberwachungsstation":    "V",
        "Verlegung extern auf Normalstation":           "V",
    }),
    "isolation_status":        ("isolationsstatus",          {
        "Isolation": "1", "Umkehrisolation": "1",
    }),
    "isolation_grund":         ("isolationsgrund",           None),
    "pupillenweite_rechts":    ("pupillenweite_rechts",      None),
    "pupillenweite_links":     ("pupillenweite_links",       None),
    "pupillenreaktion_rechts": ("pupillenreaktion_rechts",   None),
    "pupillenreaktion_links":  ("pupillenreaktion_links",    None),
}

# (staging_col, min, max, jitter_std, as_int)
_RAW_TO_STAGING_NUM = {
    "atemfrequenz":   ("atemfrequenz",          0,  99,  1.0, True),
    "saettigung":     ("sauerstoffsaettigung",  0, 100,  1.0, True),
    "blutdruck_sys":  ("blutdruck_systolisch",  0, 300,  5.0, True),
    "herzfrequenz":   ("herzfrequenz",          0, 300,  3.0, True),
    "kerntemperatur": ("koerperkerntemperatur", 30, 45,  0.2, False),
    "schmerzskala":   ("schmerzskala",          0,  10,  0.5, True),
    "gcs_summe":      ("gcs_gesamt",            3,  15,  0.0, True),
    "gcs_augen":      ("gcs_augen",             1,   4,  0.0, True),
    "gcs_verbal":     ("gcs_verbal",            1,   5,  0.0, True),
    "gcs_motorisch":  ("gcs_motorik",           1,   6,  0.0, True),
    "rankin":         ("rankin_skala",          0,   6,  0.0, True),
    "symptom_dauer":  ("symptomdauer",          0,  99,  2.0, True),
}

# Raw timestamp column → (staging done-col, staging ts-col)
_RAW_PROC_TS = {
    "labor_ts":                  ("labor_durchgefuehrt",              "labor_zeitpunkt"),
    "bga_ts":                    ("bga_durchgefuehrt",                "bga_zeitpunkt"),
    "BGA_ts":                    ("bga_durchgefuehrt",                "bga_zeitpunkt"),
    "urinschnelltest_ts":        ("urinschnelltest_durchgefuehrt",    "urinschnelltest_zeitpunkt"),
    "Urinschnelltest_ts":        ("urinschnelltest_durchgefuehrt",    "urinschnelltest_zeitpunkt"),
    "ekg_ts":                    ("ekg_durchgefuehrt",                "ekg_zeitpunkt"),
    "sonographie_ts":            ("sonographie_durchgefuehrt",        "sonographie_zeitpunkt"),
    "Sonographie_ts":            ("sonographie_durchgefuehrt",        "sonographie_zeitpunkt"),
    "echo_ts":                   ("echokardiographie_durchgefuehrt",  "echokardiographie_zeitpunkt"),
    "cct_ts":                    ("cct_durchgefuehrt",                "cct_zeitpunkt"),
    "ct_ts":                     ("ct_durchgefuehrt",                 "ct_zeitpunkt"),
    "traumascan_ts":             ("traumascan_durchgefuehrt",         "traumascan_zeitpunkt"),
    "Traumascan_ts":             ("traumascan_durchgefuehrt",         "traumascan_zeitpunkt"),
    "roengten_wirbelsaeule_ts":  ("roentgen_wirbelsaeule_durchgefuehrt", "roentgen_wirbelsaeule_zeitpunkt"),
    "Roengten_Wirbelsaeule_ts":  ("roentgen_wirbelsaeule_durchgefuehrt", "roentgen_wirbelsaeule_zeitpunkt"),
    "roentgen_thorax_ts":        ("roentgen_thorax_durchgefuehrt",    "roentgen_thorax_zeitpunkt"),
    "roentgen_becken_ts":        ("roentgen_becken_durchgefuehrt",    "roentgen_becken_zeitpunkt"),
    "roentgen_extremitaet_ts":   ("roentgen_extremitaet_durchgefuehrt", "roentgen_extremitaet_zeitpunkt"),
    "roentgen_sonstiges_ts":     ("roentgen_sonstiges_durchgefuehrt", "roentgen_sonstiges_zeitpunkt"),
    "mrt_ts":                    ("mrt_durchgefuehrt",                "mrt_zeitpunkt"),
}

# Raw boolean flag column → (staging done-col, staging ts-col)
_RAW_PROC_FLAG = {
    "labor":                  ("labor_durchgefuehrt",              "labor_zeitpunkt"),
    "BGA":                    ("bga_durchgefuehrt",                "bga_zeitpunkt"),
    "Urinschnelltest":        ("urinschnelltest_durchgefuehrt",    "urinschnelltest_zeitpunkt"),
    "ekg":                    ("ekg_durchgefuehrt",                "ekg_zeitpunkt"),
    "Sonographie":            ("sonographie_durchgefuehrt",        "sonographie_zeitpunkt"),
    "echo":                   ("echokardiographie_durchgefuehrt",  "echokardiographie_zeitpunkt"),
    "cct":                    ("cct_durchgefuehrt",                "cct_zeitpunkt"),
    "ct":                     ("ct_durchgefuehrt",                 "ct_zeitpunkt"),
    "Traumascan":             ("traumascan_durchgefuehrt",         "traumascan_zeitpunkt"),
    "Roengten_Wirbelsaeule":  ("roentgen_wirbelsaeule_durchgefuehrt", "roentgen_wirbelsaeule_zeitpunkt"),
    "roentgen_thorax":        ("roentgen_thorax_durchgefuehrt",    "roentgen_thorax_zeitpunkt"),
    "roentgen_becken":        ("roentgen_becken_durchgefuehrt",    "roentgen_becken_zeitpunkt"),
    "roentgen_extremitaet":   ("roentgen_extremitaet_durchgefuehrt", "roentgen_extremitaet_zeitpunkt"),
    "roentgen_sonstiges":     ("roentgen_sonstiges_durchgefuehrt", "roentgen_sonstiges_zeitpunkt"),
    "mrt":                    ("mrt_durchgefuehrt",                "mrt_zeitpunkt"),
}

# All staging procedure pairs (done_col, ts_col) — used to fill defaults
_ALL_STAGING_PROCS = list(_RAW_PROC_TS.values()) + [
    v for k, v in _RAW_PROC_FLAG.items()
    if v not in list(_RAW_PROC_TS.values())
]
# Deduplicate preserving insertion order
_seen = set()
_ALL_STAGING_PROCS_UNIQUE = []
for _p in _ALL_STAGING_PROCS:
    if _p[0] not in _seen:
        _seen.add(_p[0])
        _ALL_STAGING_PROCS_UNIQUE.append(_p)

# ---------------------------------------------------------------------------
# Synthetic-mode lookup tables
# ---------------------------------------------------------------------------

_FIRST_NAMES_M = [
    "Alexander", "Andreas", "Christian", "Daniel", "David",
    "Felix", "Jan", "Jonas", "Julian", "Klaus",
    "Leon", "Lukas", "Markus", "Michael", "Peter",
    "Stefan", "Thomas", "Tobias", "Maximilian", "Sebastian",
]
_FIRST_NAMES_F = [
    "Anna", "Emma", "Hannah", "Julia", "Katharina",
    "Laura", "Lea", "Lisa", "Maria", "Mia",
    "Nicole", "Sandra", "Sarah", "Sophia", "Stefanie",
    "Vanessa", "Lena", "Marie", "Luisa", "Franziska",
]
_LAST_NAMES = [
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber",
    "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann",
    "Schäfer", "Koch", "Richter", "Bauer", "Klein",
    "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann",
    "Braun", "Krüger", "Hofmann", "Hartmann", "Lange",
    "Schmitt", "Werner", "Schmitz", "Krause", "Meier",
]
_STREETS = [
    "Hauptstraße", "Bahnhofstraße", "Schillerstraße", "Goethestraße",
    "Gartenweg", "Lindenweg", "Musterstraße", "Kirchweg",
    "Parkstraße", "Waldstraße", "Bergstraße", "Talstraße",
]
_CITIES = [
    ("Berlin",           "10115", "Berlin"),
    ("Hamburg",          "20095", "Hamburg"),
    ("München",          "80331", "Bayern"),
    ("Köln",             "50667", "Nordrhein-Westfalen"),
    ("Frankfurt am Main","60311", "Hessen"),
    ("Stuttgart",        "70173", "Baden-Württemberg"),
    ("Düsseldorf",       "40213", "Nordrhein-Westfalen"),
    ("Leipzig",          "04109", "Sachsen"),
    ("Dortmund",         "44135", "Nordrhein-Westfalen"),
    ("Essen",            "45127", "Nordrhein-Westfalen"),
    ("Bremen",           "28195", "Bremen"),
    ("Dresden",          "01067", "Sachsen"),
    ("Hannover",         "30159", "Niedersachsen"),
    ("Nürnberg",         "90402", "Bayern"),
    ("Duisburg",         "47051", "Nordrhein-Westfalen"),
]
_INSURANCES = [
    ("Techniker Krankenkasse", "101575519"),
    ("Barmer",                 "104212505"),
    ("DAK-Gesundheit",         "101320001"),
    ("AOK Bayern",             "108310400"),
    ("IKK classic",            "107265005"),
    ("BKK VBU",                "103609999"),
    ("Unbekannt", ""),
    ("Unbekannt", ""),
]
_REFERRAL_CODES   = ["VAP", "KVNDAK", "KVNPIK", "RD", "NA", "KLINV", "NPHYS", "OTH"]
_REFERRAL_WEIGHTS = [15, 12, 8, 30, 10, 8, 10, 7]
_TRANSPORT_CODES   = ["NA", "1", "2", "3", "4", "OTH"]
_TRANSPORT_WEIGHTS = [25, 15, 30, 20, 5, 5]
_TRIAGE_SYSTEMS   = [("MTS", 70), ("ESI", 30)]
_DISCHARGE_CODES   = ["1", "2", "3", "4", "5", "6", "S", "V"]
_DISCHARGE_WEIGHTS = [1, 2, 3, 40, 10, 5, 30, 9]
_QUALIFIERS       = ["A", "G", "V", "Z"]
_QUALIFIER_WEIGHTS = [5, 70, 20, 5]
_PUPIL_SIZES      = ["C", "M", "D", "UNK"]
_PUPIL_SIZE_W     = [10, 60, 5, 25]
_PUPIL_REACTIONS  = ["B", "D", "A", "UNK"]
_PUPIL_REACTION_W = [65, 10, 5, 20]
_ISOLATION_REASONS= ["U80", "A09.9", "A16.9", "G03.9", "OTH"]

_ICD_POOL = [
    "I21.9", "I20.0", "I10", "J18.9", "K35.80", "S06.0", "M54.5",
    "R55",   "R07.4", "R51", "J06.9", "K29.7",  "T14.0", "S52.5",
    "I63.9", "E11.9", "N23", "G40.9", "F10.0",  "T39.1", "R60.0",
    "K80.20","J44.1", "I48.0","Z87.39","I25.9",  "G47.0",
]
_ICD_SECONDARY = [
    "I10", "E11.9", "I25.9", "M54.5", "J44.1", "F17.2", "Z87.39",
    "G47.0","K29.7", "Z96.6", "I48.0", "N18.3", "E78.5", "I50.9", "J45.9",
]
_HISTORY_TEMPLATES = [
    "Relevante Anamnese: {complaint}. Keine Vorerkrankungen bekannt.",
    "Relevante Anamnese: {complaint}. Vorerkrankungen und Dauermedikation wurden orientierend erhoben.",
    "Patient berichtet: {complaint}. Keine Allergien bekannt.",
    "{complaint}. Vorerkrankungen: Hypertonie, Diabetes.",
]
_ALLERGY_TEXTS = [
    "", "", "",
    "Penicillin (Exanthem)", "jodhaltiges Kontrastmittel",
    "Latex, Pflasterkleber", "Penicillin, Kontrastmittel, Latex",
]

_VITALS_BY_TRIAGE = {
    1: {"rr": (60,130),  "hr": (40,160),  "spo2": (70,95),  "rf": (0,40),  "temp": (34.5,40.5), "pain": (0,10),  "gcs": (3,10)},
    2: {"rr": (80,180),  "hr": (50,150),  "spo2": (80,99),  "rf": (8,35),  "temp": (35.0,40.0), "pain": (5,10),  "gcs": (8,14)},
    3: {"rr": (90,190),  "hr": (55,130),  "spo2": (88,100), "rf": (10,30), "temp": (35.5,39.5), "pain": (3,9),   "gcs": (12,15)},
    4: {"rr": (100,170), "hr": (60,110),  "spo2": (92,100), "rf": (12,24), "temp": (36.0,38.5), "pain": (1,7),   "gcs": (14,15)},
    5: {"rr": (110,160), "hr": (60,100),  "spo2": (95,100), "rf": (12,20), "temp": (36.2,37.8), "pain": (0,5),   "gcs": (15,15)},
}

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _ts_fmt(d: dt.datetime) -> str:
    return d.strftime("%Y-%m-%d %H:%M:%S")


def _weighted_choice(choices, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    acc = 0
    for c, w in zip(choices, weights):
        acc += w
        if r < acc:
            return c
    return choices[-1]


def _flag(prob: float) -> str:
    return "1" if random.random() < prob else "0"


def _quarter_end(d: dt.date) -> str:
    for qe in [dt.date(d.year, 3, 31), dt.date(d.year, 6, 30),
               dt.date(d.year, 9, 30), dt.date(d.year, 12, 31)]:
        if d <= qe:
            return qe.strftime("%Y%m%d")
    return dt.date(d.year, 12, 31).strftime("%Y%m%d")


def _fresh_ids(index: int, admission_dt: dt.datetime) -> dict:
    """Generate fresh document/patient IDs for a row."""
    return {
        "patientennummer":              f"SYN-P-{index:05d}",
        "dokument_id":                  f"SYN-ENC-{admission_dt.year}-{index:05d}",
        "Krankenhausinternes Fallkennzeichen": f"KH-{50000 + index}",
        "cda_dokument_id":              str(uuid.uuid4()),
        "dokument_erstellungszeitpunkt": _ts_fmt(admission_dt + dt.timedelta(minutes=random.randint(0, 5))),
        "dokument_versionsnummer":      "1",
    }


def _synthetic_demographics(index: int, gender: str) -> dict:
    if gender in ("F", "W"):
        first = random.choice(_FIRST_NAMES_F)
    else:
        first = random.choice(_FIRST_NAMES_M)
    last = random.choice(_LAST_NAMES)
    city, plz, state = random.choice(_CITIES)
    age = random.randint(18, 92)
    birth_year = dt.date.today().year - age
    birth_date = dt.date(birth_year, random.randint(1, 12), random.randint(1, 28))
    return {
        "patient_vorname":     first,
        "patient_nachname":    last,
        "patient_geburtsdatum": birth_date.strftime("%Y-%m-%d"),
        "patient_strasse":     random.choice(_STREETS),
        "patient_hausnummer":  str(random.randint(1, 120)),
        "patient_richtung":    "",
        "patient_adresszusatz": "",
        "patient_ort":         city,
        "patient_bundesland":  state,
        "postleitzahl":        plz,
        "patient_telefon":     "",
        "patient_mobiltelefon": "",
        "patient_email":       "",
    }


def _synthetic_insurance(admission_date: dt.date) -> dict:
    ins_name, ins_ik = random.choice(_INSURANCES)
    if ins_name != "Unbekannt":
        egk_nr = f"E{random.randint(100000000, 999999999):09d}"
        v_nr   = f"V{random.randint(100000000, 999999999):09d}"
        qe     = _quarter_end(admission_date)
    else:
        egk_nr = v_nr = qe = ""
    return {
        "krankenkasse_name":          ins_name,
        "ik_nummer":                  ins_ik,
        "egk_nummer":                 egk_nr,
        "versicherungsnummer":        v_nr,
        "versicherungs_quartalsende": qe,
        "versicherter_vorname":       "",
        "versicherter_nachname":      "",
        "vk_nummer":                  "",
    }


def _org_author_fields(org_id, org_name, org_phone, org_email,
                       org_street, org_house, org_city, org_plz, org_state,
                       author_id, author_prefix, author_first, author_last,
                       admission_dt: dt.datetime) -> dict:
    return {
        "autor_1_zeitpunkt":    _ts_fmt(admission_dt + dt.timedelta(minutes=random.randint(0, 5))),
        "autor_1_id":           author_id,
        "autor_1_praefix":      author_prefix,
        "autor_1_vorname":      author_first,
        "autor_1_nachname":     author_last,
        "autor_2_zeitpunkt":    "",
        "autor_2_id":           "",
        "autor_2_praefix":      "",
        "autor_2_vorname":      "",
        "autor_2_nachname":     "",
        "organisation_id":      org_id,
        "organisation_name":    org_name,
        "organisation_telefon": org_phone,
        "organisation_mobiltelefon": "",
        "organisation_email":   org_email,
        "organisation_strasse": org_street,
        "organisation_hausnummer": org_house,
        "organisation_adresszusatz": "",
        "organisation_ort":     org_city,
        "organisation_postleitzahl": org_plz,
        "organisation_bundesland": org_state,
    }


def _allergy_fields(prob_present: float = 0.30) -> dict:
    present = _flag(prob_present)
    return {
        "allergie_allgemein":       present,
        "allergie_antibiotika":     _flag(0.15) if present == "1" else "0",
        "allergie_kontrastmittel":  _flag(0.10) if present == "1" else "0",
        "allergie_sonstige":        _flag(0.20) if present == "1" else "0",
        "allergie_freitext":        random.choice(_ALLERGY_TEXTS) if present == "1" else "",
    }


def _empty_pii() -> dict:
    """Empty PII block used in anonymize/empirical modes."""
    return {
        "patient_vorname": "", "patient_nachname": "",
        "patient_geburtsdatum": "", "patient_strasse": "",
        "patient_hausnummer": "", "patient_richtung": "",
        "patient_adresszusatz": "", "patient_ort": "",
        "patient_bundesland": "", "postleitzahl": "",
        "patient_telefon": "", "patient_mobiltelefon": "", "patient_email": "",
    }


def _diagnose_pad(row: dict) -> None:
    """Ensure diagnose_2..10 keys always exist."""
    for n in range(2, 11):
        row.setdefault(f"diagnose_{n}", "")
        row.setdefault(f"diagnose_{n}_zusatzkennzeichen", "")


# ---------------------------------------------------------------------------
# ═══════════════════════════  SYNTHETIC MODE  ═══════════════════════════════
# ---------------------------------------------------------------------------

def generate_rows(
    count: int,
    start_date: dt.date = None,
    end_date: dt.date = None,
    org_id: str = "1.2.276.0.76.4.17.9999",
    org_name: str = "AKTIN Testklinikum",
    org_street: str = "Krankenhausstraße",
    org_house: str = "1",
    org_city: str = "Berlin",
    org_plz: str = "10115",
    org_state: str = "Berlin",
    org_phone: str = "+49 30 12345-0",
    org_email: str = "notaufnahme@example.org",
    author_prefix: str = "Dr.",
    author_first: str = "Mara",
    author_last: str = "Behnke",
    author_id: str = "A-4711",
    seed: int = None,
) -> list:
    """
    Generate *count* synthetic ED cases with clinically plausible random values.
    No external data required.
    """
    if seed is not None:
        random.seed(seed)

    today = dt.date.today()
    if start_date is None:
        start_date = dt.date(2000, 1, 1)
    if end_date is None:
        end_date = today
    date_range_days = max((end_date - start_date).days, 1)

    kw = dict(
        org_id=org_id, org_name=org_name, org_street=org_street,
        org_house=org_house, org_city=org_city, org_plz=org_plz,
        org_state=org_state, org_phone=org_phone, org_email=org_email,
        author_id=author_id, author_prefix=author_prefix,
        author_first=author_first, author_last=author_last,
    )
    return [_synthetic_one(i, start_date, date_range_days, **kw)
            for i in range(1, count + 1)]


def _synthetic_one(index, start_date, date_range_days, **kw) -> dict:
    # --- Timestamps ---------------------------------------------------------
    admission_date = start_date + dt.timedelta(days=random.randint(0, date_range_days))
    admission = dt.datetime(admission_date.year, admission_date.month, admission_date.day,
                            random.randint(0, 23), random.randint(0, 59))
    triage        = admission   + dt.timedelta(minutes=random.randint(1, 10))
    doctor        = triage      + dt.timedelta(minutes=random.randint(5, 25))
    therapy_start = doctor      + dt.timedelta(minutes=random.randint(-2, 5))
    discharge     = admission   + dt.timedelta(minutes=random.randint(30, 8 * 60))
    therapy_end   = discharge   - dt.timedelta(minutes=random.randint(0, 20))
    end_doctor    = discharge   - dt.timedelta(minutes=random.randint(5, 20))

    # --- Triage -------------------------------------------------------------
    triage_sys   = _weighted_choice([s for s, _ in _TRIAGE_SYSTEMS], [w for _, w in _TRIAGE_SYSTEMS])
    triage_level = random.choices([1, 2, 3, 4, 5], weights=[3, 15, 40, 35, 7])[0]
    vr           = _VITALS_BY_TRIAGE[triage_level]
    has_vitals   = triage_level <= 4 or random.random() < 0.7

    # --- Vitals -------------------------------------------------------------
    if has_vitals:
        rr   = random.randint(*vr["rr"])
        hr   = random.randint(*vr["hr"])
        spo2 = round(random.uniform(*vr["spo2"]), 1)
        rf   = random.randint(*vr["rf"])
        temp = round(random.uniform(*vr["temp"]), 1)
        pain = random.randint(*vr["pain"])
    else:
        rr = hr = spo2 = rf = temp = pain = ""

    # --- GCS ----------------------------------------------------------------
    has_gcs = has_vitals and (triage_level <= 3 or random.random() < 0.5)
    if has_gcs:
        total = random.randint(*vr["gcs"])
        eyes   = min(4, max(1, round(total * 4 / 15 + random.uniform(-0.5, 0.5))))
        verbal = min(5, max(1, round(total * 5 / 15 + random.uniform(-0.5, 0.5))))
        motor  = min(6, max(1, total - eyes - verbal))
        total  = eyes + verbal + motor
        gcs_total, gcs_eyes, gcs_verbal, gcs_motor = str(total), str(eyes), str(verbal), str(motor)
    else:
        gcs_total = gcs_eyes = gcs_verbal = gcs_motor = ""

    # --- Pupils -------------------------------------------------------------
    if has_gcs and random.random() < 0.6:
        psr = _weighted_choice(_PUPIL_SIZES, _PUPIL_SIZE_W)
        psl = _weighted_choice(_PUPIL_SIZES, _PUPIL_SIZE_W)
        prr = _weighted_choice(_PUPIL_REACTIONS, _PUPIL_REACTION_W)
        prl = _weighted_choice(_PUPIL_REACTIONS, _PUPIL_REACTION_W)
    else:
        psr = psl = prr = prl = "UNK"

    # --- Isolation / MRE ----------------------------------------------------
    isolation  = _flag(0.05)
    iso_reason = random.choice(_ISOLATION_REASONS) if isolation == "1" else ""
    mre        = _flag(0.03)
    mrsa       = _flag(0.3)  if mre == "1" else "0"
    three_mrgn = _flag(0.2)  if mre == "1" and mrsa == "0" else "0"
    four_mrgn  = _flag(0.1)  if mre == "1" and mrsa == "0" and three_mrgn == "0" else "0"
    vre        = _flag(0.2)  if mre == "1" and mrsa == "0" and three_mrgn == "0" and four_mrgn == "0" else "0"

    # --- Diagnostics --------------------------------------------------------
    def diag(prob, offset=(10, 90)):
        if random.random() < prob:
            return "PB", _ts_fmt(doctor + dt.timedelta(minutes=random.randint(*offset)))
        return "OPB", ""

    lab_d,    lab_t    = diag(0.75, (10, 60))
    bga_d,    bga_t    = diag(0.30, (15, 45))
    urin_d,   urin_t   = diag(0.25, (15, 50))
    ekg_d,    ekg_t    = diag(0.55, (5, 30))
    sono_d,   sono_t   = diag(0.20, (20, 70))
    echo_d,   echo_t   = diag(0.08, (30, 90))
    cct_d,    cct_t    = diag(0.15, (30, 90))
    ct_d,     ct_t     = diag(0.20, (30, 90))
    trauma_d, trauma_t = diag(0.05, (20, 60))
    rxsp_d,   rxsp_t   = diag(0.08, (20, 60))
    rxtx_d,   rxtx_t   = diag(0.30, (15, 60))
    rxpel_d,  rxpel_t  = diag(0.05, (20, 60))
    rxext_d,  rxext_t  = diag(0.12, (15, 50))
    rxoth_d,  rxoth_t  = diag(0.05, (20, 60))
    mrt_d,    mrt_t    = diag(0.07, (40, 120))

    # --- CEDIS / chief complaint --------------------------------------------
    cedis_code, cedis_txt = random.choice(_CEDIS)
    sym_dur = random.choice([5, 10, 15, 30, 60, 120, 240, 480, 1440, 2880, 10080])

    # --- Discharge / diagnosis ----------------------------------------------
    discharge_code   = _weighted_choice(_DISCHARGE_CODES, _DISCHARGE_WEIGHTS)
    primary_icd      = random.choice(_ICD_POOL)
    primary_qualifier= _weighted_choice(_QUALIFIERS, _QUALIFIER_WEIGHTS)
    n_sec  = random.choices([0, 1, 2, 3], weights=[40, 35, 20, 5])[0]
    others = random.sample([c for c in _ICD_SECONDARY if c != primary_icd], min(n_sec, len(_ICD_SECONDARY) - 1))

    # --- Demographics (gender needed before demographics call) --------------
    gender = random.choice(["M", "F", "W"])

    row: dict = {
        **_fresh_ids(index, admission),
        "geschlecht":                    gender,
        "aufnahme_zeitpunkt":            _ts_fmt(admission),
        "entlassung_zeitpunkt":          _ts_fmt(discharge),
        "triage_system":                 triage_sys,
        "triage_stufe":                  str(triage_level),
        "triage_zeitpunkt":              _ts_fmt(triage),
        "arztkontakt_beginn_zeitpunkt":  _ts_fmt(doctor),
        "arztkontakt_ende_zeitpunkt":    _ts_fmt(end_doctor),
        "therapiebeginn_zeitpunkt":      _ts_fmt(therapy_start),
        "therapieende_zeitpunkt":        _ts_fmt(therapy_end),
        "behandler_id":                  "",
        "zuweisungsart":                 _weighted_choice(_REFERRAL_CODES, _REFERRAL_WEIGHTS),
        "transportmittel":               _weighted_choice(_TRANSPORT_CODES, _TRANSPORT_WEIGHTS),
        "vorstellungsgrund_cedis":       cedis_code,
        "vorstellungsgrund_text":        cedis_txt,
        "symptomdauer":                  str(sym_dur),
        "atemfrequenz":                  str(rf)   if rf   != "" else "",
        "sauerstoffsaettigung":          str(spo2) if spo2 != "" else "",
        "blutdruck_systolisch":          str(rr)   if rr   != "" else "",
        "herzfrequenz":                  str(hr)   if hr   != "" else "",
        "koerperkerntemperatur":         str(temp) if temp != "" else "",
        "schmerzskala":                  str(pain) if pain != "" else "",
        "gcs_gesamt":                    gcs_total,
        "gcs_augen":                     gcs_eyes,
        "gcs_verbal":                    gcs_verbal,
        "gcs_motorik":                   gcs_motor,
        "pupillenweite_rechts":          psr,
        "pupillenweite_links":           psl,
        "pupillenreaktion_rechts":       prr,
        "pupillenreaktion_links":        prl,
        "rankin_skala":                  str(random.choices([0,1,2,3,4,5,6], weights=[30,20,15,15,10,8,2])[0]),
        "isolationsstatus":              isolation,
        "isolationsgrund":               iso_reason,
        "multiresistente_erreger":       mre,
        "mrsa_status":                   mrsa,
        "mrgn_3_status":                 three_mrgn,
        "mrgn_4_status":                 four_mrgn,
        "vre_status":                    vre,
        "andere_multiresistente_erreger":"0",
        "labor_durchgefuehrt":           lab_d,    "labor_zeitpunkt":               lab_t,
        "bga_durchgefuehrt":             bga_d,    "bga_zeitpunkt":                 bga_t,
        "urinschnelltest_durchgefuehrt": urin_d,   "urinschnelltest_zeitpunkt":     urin_t,
        "ekg_durchgefuehrt":             ekg_d,    "ekg_zeitpunkt":                 ekg_t,
        "sonographie_durchgefuehrt":     sono_d,   "sonographie_zeitpunkt":         sono_t,
        "echokardiographie_durchgefuehrt": echo_d, "echokardiographie_zeitpunkt":   echo_t,
        "cct_durchgefuehrt":             cct_d,    "cct_zeitpunkt":                 cct_t,
        "ct_durchgefuehrt":              ct_d,     "ct_zeitpunkt":                  ct_t,
        "traumascan_durchgefuehrt":      trauma_d, "traumascan_zeitpunkt":          trauma_t,
        "roentgen_wirbelsaeule_durchgefuehrt": rxsp_d,  "roentgen_wirbelsaeule_zeitpunkt": rxsp_t,
        "roentgen_thorax_durchgefuehrt": rxtx_d,   "roentgen_thorax_zeitpunkt":     rxtx_t,
        "roentgen_becken_durchgefuehrt": rxpel_d,  "roentgen_becken_zeitpunkt":     rxpel_t,
        "roentgen_extremitaet_durchgefuehrt": rxext_d, "roentgen_extremitaet_zeitpunkt": rxext_t,
        "roentgen_sonstiges_durchgefuehrt": rxoth_d,   "roentgen_sonstiges_zeitpunkt":    rxoth_t,
        "mrt_durchgefuehrt":             mrt_d,    "mrt_zeitpunkt":                 mrt_t,
        "verbleib_nach_notaufnahme":     discharge_code,
        "icd10gm_code":                  primary_icd,
        "diagnose_fuehrend":             "1",
        "diagnose_fuehrend_zusatzkennzeichen": primary_qualifier,
        "notfallanamnese":               random.choice(_HISTORY_TEMPLATES).format(
                                             complaint=cedis_txt.split(";")[0].strip()),
        "tetanusschutz":                 random.choice(["0", "1", "1", "1", ""]),
        **_synthetic_demographics(index, gender),
        **_synthetic_insurance(admission_date),
        **_org_author_fields(**kw, admission_dt=admission),
        **_allergy_fields(),
    }

    for n, sec in enumerate(others, start=2):
        row[f"diagnose_{n}"] = sec
        row[f"diagnose_{n}_zusatzkennzeichen"] = _weighted_choice(_QUALIFIERS, _QUALIFIER_WEIGHTS)

    _diagnose_pad(row)
    return row


# ---------------------------------------------------------------------------
# ═══════════════════════════  EMPIRICAL MODE  ═══════════════════════════════
# ---------------------------------------------------------------------------

def generate_rows_empirical(
    case_data_path: str,
    diag_data_path: str,
    count: int,
    start_date: dt.date = None,
    end_date: dt.date = None,
    org_id: str = "1.2.276.0.76.4.17.9999",
    org_name: str = "AKTIN Testklinikum",
    org_street: str = "Krankenhausstraße",
    org_house: str = "1",
    org_city: str = "Berlin",
    org_plz: str = "10115",
    org_state: str = "Berlin",
    org_phone: str = "+49 30 12345-0",
    org_email: str = "notaufnahme@example.org",
    author_prefix: str = "Dr.",
    author_first: str = "Mara",
    author_last: str = "Behnke",
    author_id: str = "A-4711",
    seed: int = None,
) -> list:
    """
    Generate *count* synthetic rows whose statistical distributions mirror
    those observed in the AKTIN raw exports at *case_data_path* /
    *diag_data_path*.

    Patient identifiers and PII are freshly generated; no real patient data
    is reproduced.  Requires ``pandas>=1.3``.
    """
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas is required for empirical mode: pip install pandas>=1.3") from exc

    if seed is not None:
        random.seed(seed)

    print(f"[empirical] Loading {case_data_path} ...")
    df_case = pd.read_csv(case_data_path, sep="\t", low_memory=False)
    print(f"[empirical] Loading {diag_data_path} ...")
    df_diag = pd.read_csv(diag_data_path, sep="\t", low_memory=False)

    dist  = _analyze_case_data(df_case)
    ddiag = _analyze_diag_data(df_diag)

    today = dt.date.today()
    if start_date is None:
        start_date = dt.date(2000, 1, 1)
    if end_date is None:
        end_date = today

    kw = dict(
        org_id=org_id, org_name=org_name, org_street=org_street,
        org_house=org_house, org_city=org_city, org_plz=org_plz,
        org_state=org_state, org_phone=org_phone, org_email=org_email,
        author_id=author_id, author_prefix=author_prefix,
        author_first=author_first, author_last=author_last,
    )
    print(f"[empirical] Generating {count} synthetic rows ...")
    rows = [_empirical_one(i, dist, ddiag, start_date, end_date, **kw)
            for i in range(1, count + 1)]
    print(f"[empirical] Done.")
    return rows


def _empirical_one(index, dist, ddiag, start_date, end_date, **kw) -> dict:
    # --- Admission timestamp (empirical hour weights) -----------------------
    start_dt = dt.datetime(start_date.year, start_date.month, start_date.day)
    end_dt   = dt.datetime(end_date.year,   end_date.month,   end_date.day)
    day_off  = random.randint(0, max((end_dt - start_dt).days, 0))
    hour     = (random.choices(range(24), weights=dist["hour_weights"], k=1)[0]
                if dist["hour_weights"] and sum(dist["hour_weights"]) > 0
                else random.randint(0, 23))
    base_day = start_dt + dt.timedelta(days=day_off)
    admission = base_day.replace(hour=hour, minute=random.randint(0, 59), second=0)
    admission_date = admission.date()

    # --- LOS and offsets (bootstrap from empirical samples) ----------------
    los       = float(random.choice(dist["los_samples"]))   if dist["los_samples"]       else float(random.randint(60, 300))
    ak_off    = float(random.choice(dist["ak_offsets"]))    if dist["ak_offsets"]         else 30.0
    triage_off= float(random.choice(dist["triage_offsets"]))if dist["triage_offsets"]     else 5.0
    los       = max(30.0, los)
    ak_off    = max(1.0, ak_off)
    triage_off= max(0.0, triage_off)

    discharge     = admission + dt.timedelta(minutes=los)
    triage        = admission + dt.timedelta(minutes=triage_off)
    doctor        = admission + dt.timedelta(minutes=ak_off)
    therapy_start = doctor    + dt.timedelta(minutes=max(0, int(los * 0.05)))
    therapy_end   = discharge - dt.timedelta(minutes=random.randint(0, 20))
    end_doctor    = doctor    + dt.timedelta(minutes=max(1, int(los * 0.20)))

    # --- Categorical fields (empirical frequencies) -------------------------
    def cat(raw_col, staging_col, mapping):
        freq = dist["cat"].get(raw_col, {})
        miss = dist["missing"].get(raw_col, 1.0)
        if not freq or random.random() < miss:
            return staging_col, ""
        val = random.choices(list(freq.keys()), weights=list(freq.values()), k=1)[0]
        if raw_col == "triage":
            try:
                val = str(int(float(val)))
            except (ValueError, TypeError):
                val = ""
        elif mapping:
            val = mapping.get(val, val)
        return staging_col, val

    cat_fields = {}
    for raw_col, (staging_col, mapping) in _RAW_TO_STAGING_CAT.items():
        if raw_col in ("isolation_status", "isolation_grund"):
            continue
        _, val = cat(raw_col, staging_col, mapping)
        cat_fields[staging_col] = val

    if not cat_fields.get("zuweisungsart"):
        cat_fields["zuweisungsart"] = "OTH"

    # --- Numeric fields (bootstrap + jitter) --------------------------------
    num_fields = {}
    for raw_col, (staging_col, mn, mx, jitter, as_int) in _RAW_TO_STAGING_NUM.items():
        samples = dist["num"].get(raw_col)
        if samples:
            val = float(random.choice(samples))
            if jitter > 0:
                val += random.gauss(0, jitter)
            val = max(mn, min(mx, val))
            num_fields[staging_col] = str(int(round(val))) if as_int else str(round(val, 2))
        else:
            num_fields[staging_col] = ""

    # GCS consistency
    if all(num_fields.get(c) for c in ("gcs_augen", "gcs_verbal", "gcs_motorik")):
        total = int(num_fields["gcs_augen"]) + int(num_fields["gcs_verbal"]) + int(num_fields["gcs_motorik"])
        num_fields["gcs_gesamt"] = str(max(3, min(15, total)))

    # Age → birth date
    age_samples = dist["num"].get("age_in_years")
    if age_samples:
        age = int(max(0, min(120, float(random.choice(age_samples)) + random.gauss(0, 2))))
    else:
        age = random.randint(18, 80)
    birth_year = admission.year - age
    birth_date = dt.date(birth_year, random.randint(1, 12), random.randint(1, 28))

    # --- Procedures (empirical absence rates) -------------------------------
    proc_fields = _empirical_procedures(dist["proc_absence"], doctor)

    # --- Isolation / germs --------------------------------------------------
    iso_fields = _empirical_isolation(dist)

    # --- Diagnoses (empirical ICD frequencies) ------------------------------
    diag_fields = _empirical_diagnoses(ddiag)

    row: dict = {
        **_fresh_ids(index, admission),
        "geschlecht":                    cat_fields.get("geschlecht", "M"),
        "aufnahme_zeitpunkt":            _ts_fmt(admission),
        "entlassung_zeitpunkt":          _ts_fmt(discharge),
        "triage_system":                 cat_fields.get("triage_system", "MTS"),
        "triage_stufe":                  cat_fields.get("triage_stufe", "3"),
        "triage_zeitpunkt":              _ts_fmt(triage),
        "arztkontakt_beginn_zeitpunkt":  _ts_fmt(doctor),
        "arztkontakt_ende_zeitpunkt":    _ts_fmt(end_doctor),
        "therapiebeginn_zeitpunkt":      _ts_fmt(therapy_start),
        "therapieende_zeitpunkt":        _ts_fmt(therapy_end),
        "behandler_id":                  "",
        "zuweisungsart":                 cat_fields.get("zuweisungsart", "OTH"),
        "transportmittel":               cat_fields.get("transportmittel", "NA"),
        "vorstellungsgrund_cedis":       cat_fields.get("vorstellungsgrund_cedis", ""),
        "vorstellungsgrund_text":        "",
        "symptomdauer":                  num_fields.get("symptomdauer", ""),
        "atemfrequenz":                  num_fields.get("atemfrequenz", ""),
        "sauerstoffsaettigung":          num_fields.get("sauerstoffsaettigung", ""),
        "blutdruck_systolisch":          num_fields.get("blutdruck_systolisch", ""),
        "herzfrequenz":                  num_fields.get("herzfrequenz", ""),
        "koerperkerntemperatur":         num_fields.get("koerperkerntemperatur", ""),
        "schmerzskala":                  num_fields.get("schmerzskala", ""),
        "gcs_gesamt":                    num_fields.get("gcs_gesamt", ""),
        "gcs_augen":                     num_fields.get("gcs_augen", ""),
        "gcs_verbal":                    num_fields.get("gcs_verbal", ""),
        "gcs_motorik":                   num_fields.get("gcs_motorik", ""),
        "pupillenweite_rechts":          cat_fields.get("pupillenweite_rechts", "UNK"),
        "pupillenweite_links":           cat_fields.get("pupillenweite_links", "UNK"),
        "pupillenreaktion_rechts":       cat_fields.get("pupillenreaktion_rechts", "UNK"),
        "pupillenreaktion_links":        cat_fields.get("pupillenreaktion_links", "UNK"),
        "rankin_skala":                  num_fields.get("rankin_skala", ""),
        "verbleib_nach_notaufnahme":     cat_fields.get("verbleib_nach_notaufnahme", "4"),
        "notfallanamnese":               "",
        "tetanusschutz":                 random.choice(["0", "1", "1", "1", ""]),
        **iso_fields,
        **proc_fields,
        **diag_fields,
        "patient_geburtsdatum":          birth_date.strftime("%Y-%m-%d"),
        **_empty_pii(),
        **_synthetic_insurance(admission_date),
        **_org_author_fields(**kw, admission_dt=admission),
        **_allergy_fields(0.30),
    }
    # Override PII placeholders that came from _empty_pii but need to coexist
    row["patient_geburtsdatum"] = birth_date.strftime("%Y-%m-%d")
    _diagnose_pad(row)
    return row


def _empirical_procedures(proc_absence: dict, doctor_dt: dt.datetime) -> dict:
    out = {}
    for done_col, ts_col in _ALL_STAGING_PROCS_UNIQUE:
        # Reverse-lookup absence rate from the cda_col name used in distribution_analyzer
        cda_name = done_col.replace("_durchgefuehrt", "")
        cda_name = cda_name.replace("roentgen_", "diagnostics_xray_")
        cda_name = cda_name.replace("echokardiographie", "diagnostics_echocardiography")
        # Map staging column names to the distribution_analyzer cda_col keys
        _DONE_TO_DIST = {
            "labor_durchgefuehrt":                    "diagnostics_laboratory",
            "bga_durchgefuehrt":                      "diagnostics_blood_gases",
            "urinschnelltest_durchgefuehrt":          "diagnostics_urine_quick_test",
            "ekg_durchgefuehrt":                      "diagnostics_ecg",
            "sonographie_durchgefuehrt":              "diagnostics_ultrasound",
            "echokardiographie_durchgefuehrt":        "diagnostics_echocardiography",
            "cct_durchgefuehrt":                      "diagnostics_ct_head",
            "ct_durchgefuehrt":                       "diagnostics_ct",
            "traumascan_durchgefuehrt":               "diagnostics_ct_trauma",
            "roentgen_wirbelsaeule_durchgefuehrt":    "diagnostics_xray_spine",
            "roentgen_thorax_durchgefuehrt":          "diagnostics_xray_thorax",
            "roentgen_becken_durchgefuehrt":          "diagnostics_xray_pelvis",
            "roentgen_extremitaet_durchgefuehrt":     "diagnostics_xray_extremities",
            "roentgen_sonstiges_durchgefuehrt":       "diagnostics_xray_others",
            "mrt_durchgefuehrt":                      "diagnostics_mrt",
        }
        dist_key = _DONE_TO_DIST.get(done_col, "")
        absence  = proc_absence.get(dist_key, 0.8)
        if random.random() >= absence:
            out[done_col] = "PB"
            out[ts_col]   = _ts_fmt(doctor_dt + dt.timedelta(minutes=random.randint(10, 90)))
        else:
            out[done_col] = "OPB"
            out[ts_col]   = ""
    return out


def _empirical_isolation(dist: dict) -> dict:
    iso_freq    = dist["cat"].get("isolation_status", {})
    iso_missing = dist["missing"].get("isolation_status", 0.99)
    if not iso_freq or random.random() < iso_missing:
        iso_val = "0"
    else:
        raw = random.choices(list(iso_freq.keys()), weights=list(iso_freq.values()), k=1)[0]
        iso_val = "1" if raw in ("Isolation", "Umkehrisolation") else "0"

    grund_freq    = dist["cat"].get("isolation_grund", {})
    grund_missing = dist["missing"].get("isolation_grund", 0.9)
    if iso_val == "0" or not grund_freq or random.random() < grund_missing:
        iso_grund = "U80" if iso_val == "1" else ""
    else:
        iso_grund = random.choices(list(grund_freq.keys()), weights=list(grund_freq.values()), k=1)[0]

    mre = "1" if iso_val == "1" and random.random() < 0.5 else "0"
    return {
        "isolationsstatus":              iso_val,
        "isolationsgrund":               iso_grund,
        "multiresistente_erreger":       mre,
        "mrsa_status":                   _flag(0.3) if mre == "1" else "0",
        "mrgn_3_status":                 "0",
        "mrgn_4_status":                 "0",
        "vre_status":                    "0",
        "andere_multiresistente_erreger":"0",
    }


def _empirical_diagnoses(ddiag: dict) -> dict:
    icd_freq  = ddiag.get("icd_codes", {})
    qual_freq = ddiag.get("diagnose_zusatz", {})
    cnt_dist  = ddiag.get("diag_count", {})

    def sample_icd():
        if not icd_freq:
            return random.choice(_ICD_POOL)
        return random.choices(list(icd_freq.keys()), weights=list(icd_freq.values()), k=1)[0]

    def sample_qual():
        if not qual_freq:
            return _weighted_choice(_QUALIFIERS, _QUALIFIER_WEIGHTS)
        return random.choices(list(qual_freq.keys()), weights=list(qual_freq.values()), k=1)[0]

    # Number of diagnoses per encounter
    if cnt_dist:
        n_diag = random.choices(list(cnt_dist.keys()), weights=list(cnt_dist.values()), k=1)[0]
        n_diag = max(1, min(10, n_diag))
    else:
        n_diag = random.choices([1, 2, 3], weights=[50, 35, 15])[0]

    out = {
        "icd10gm_code":                      sample_icd(),
        "diagnose_fuehrend":                 "1",
        "diagnose_fuehrend_zusatzkennzeichen": sample_qual(),
    }
    for n in range(2, n_diag + 1):
        out[f"diagnose_{n}"]                    = sample_icd()
        out[f"diagnose_{n}_zusatzkennzeichen"]  = sample_qual()
    return out


# ---------------------------------------------------------------------------
# ═══════════════════════════  ANONYMIZE MODE  ════════════════════════════════
# ---------------------------------------------------------------------------

def generate_rows_anonymize(
    case_data_path: str,
    diag_data_path: str,
    count: int,
    org_id: str = "1.2.276.0.76.4.17.9999",
    org_name: str = "AKTIN Testklinikum",
    org_street: str = "Krankenhausstraße",
    org_house: str = "1",
    org_city: str = "Berlin",
    org_plz: str = "10115",
    org_state: str = "Berlin",
    org_phone: str = "+49 30 12345-0",
    org_email: str = "notaufnahme@example.org",
    author_prefix: str = "Dr.",
    author_first: str = "Mara",
    author_last: str = "Behnke",
    author_id: str = "A-4711",
    seed: int = None,
    time_jitter_minutes: int = 30,
    age_jitter_years: int = 2,
) -> list:
    """
    Anonymize real AKTIN export cases.

    Each input row is transformed into one output row:
      - Reassigned to a random day within the original calendar month.
      - Admission time jittered by ±time_jitter_minutes.
      - LOS and inter-event offsets preserved exactly.
      - Numeric vitals jittered by small Gaussian noise.
      - GCS kept intact.
      - All PII (names, addresses, IDs) freshly generated.
      - Diagnoses matched from diag_data.txt by encounter key.

    If count < number of available rows, a random sample of *count* rows is
    taken.  Requires ``pandas>=1.3``.
    """
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas is required for anonymize mode: pip install pandas>=1.3") from exc

    if seed is not None:
        random.seed(seed)

    print(f"[anonymize] Loading {case_data_path} ...")
    df_case = pd.read_csv(case_data_path, sep="\t", low_memory=False)
    print(f"[anonymize] Loading {diag_data_path} ...")
    df_diag = pd.read_csv(diag_data_path, sep="\t", low_memory=False)

    total = len(df_case)
    if count < total:
        df_case = df_case.sample(n=count, random_state=seed).reset_index(drop=True)
        print(f"[anonymize] Sampled {count} of {total} rows")
    else:
        if count > total:
            print(f"[anonymize] Requested {count} but only {total} available — using all")
        df_case = df_case.reset_index(drop=True)

    diag_lookup = _build_diag_lookup(df_diag)
    print(f"[anonymize] Anonymizing {len(df_case)} rows "
          f"(time_jitter=±{time_jitter_minutes} min, age_jitter=±{age_jitter_years} yr) ...")

    kw = dict(
        org_id=org_id, org_name=org_name, org_street=org_street,
        org_house=org_house, org_city=org_city, org_plz=org_plz,
        org_state=org_state, org_phone=org_phone, org_email=org_email,
        author_id=author_id, author_prefix=author_prefix,
        author_first=author_first, author_last=author_last,
    )
    rows = [
        _anonymize_one(i + 1, row, diag_lookup, time_jitter_minutes, age_jitter_years, **kw)
        for i, (_, row) in enumerate(df_case.iterrows())
    ]
    print(f"[anonymize] Done.")
    return rows


def _anonymize_one(index, src, diag_lookup, time_jitter_minutes, age_jitter_years, **kw) -> dict:
    import pandas as pd

    def _parse(val):
        if isinstance(val, str) and val.strip():
            try:
                return pd.to_datetime(val, utc=True).to_pydatetime().replace(tzinfo=None)
            except Exception:
                return None
        if pd.notna(val) and val:
            try:
                return pd.to_datetime(val, utc=True).to_pydatetime().replace(tzinfo=None)
            except Exception:
                return None
        return None

    def _raw(col):
        v = src.get(col)
        if v is None or (not isinstance(v, str) and pd.isna(v)):
            return ""
        return str(v).strip()

    # --- Parse source timestamps --------------------------------------------
    admission_orig = _parse(src.get("aufnahme_ts")) or dt.datetime(2022, 1, 1, 8, 0)
    discharge_orig = _parse(src.get("entlassung_ts"))
    doctor_orig    = _parse(src.get("start_arztkontakt_ts"))
    triage_orig    = _parse(src.get("triage_ts"))

    los_minutes  = max(30.0, (discharge_orig - admission_orig).total_seconds() / 60) if discharge_orig else float(random.randint(60, 300))
    ak_offset    = max(1.0,  (doctor_orig    - admission_orig).total_seconds() / 60) if doctor_orig    else 30.0
    triage_offset= max(0.0,  (triage_orig    - admission_orig).total_seconds() / 60) if triage_orig    else 5.0

    # --- Reassign to random day in same calendar month + jitter -------------
    new_day = random.randint(1, calendar.monthrange(admission_orig.year, admission_orig.month)[1])
    base    = admission_orig.replace(day=new_day)
    jitter  = dt.timedelta(minutes=random.randint(-time_jitter_minutes, time_jitter_minutes))
    admission    = base + jitter
    discharge    = admission + dt.timedelta(minutes=los_minutes)
    doctor       = admission + dt.timedelta(minutes=ak_offset)
    triage       = admission + dt.timedelta(minutes=triage_offset)
    therapy_start= doctor   + dt.timedelta(minutes=max(0, int(los_minutes * 0.05)))
    therapy_end  = max(
        discharge - dt.timedelta(minutes=random.randint(0, 20)),
        therapy_start + dt.timedelta(minutes=1),
    )
    end_doctor   = max(
        doctor + dt.timedelta(minutes=max(1, int(los_minutes * 0.20))),
        doctor + dt.timedelta(minutes=1),
    )

    admission_date = admission.date()

    # --- Age → birth date ---------------------------------------------------
    age_raw = src.get("age_in_years")
    if age_raw is not None and not (isinstance(age_raw, float) and pd.isna(age_raw)):
        age = int(float(age_raw)) + random.randint(-age_jitter_years, age_jitter_years)
        age = max(0, min(120, age))
    else:
        age = random.randint(18, 80)
    birth_date = dt.date(admission.year - age, random.randint(1, 12), random.randint(1, 28))

    # --- Categorical clinical fields ----------------------------------------
    cat_fields = {}
    for raw_col, (staging_col, mapping) in _RAW_TO_STAGING_CAT.items():
        if raw_col in ("isolation_status", "isolation_grund"):
            continue
        val = _raw(raw_col)
        if not val:
            cat_fields[staging_col] = ""
            continue
        if raw_col == "triage":
            try:
                val = str(int(float(val)))
            except (ValueError, TypeError):
                val = ""
        elif mapping:
            val = mapping.get(val, val)
        cat_fields[staging_col] = val

    if not cat_fields.get("zuweisungsart"):
        cat_fields["zuweisungsart"] = "OTH"

    # --- Numeric clinical fields (Gaussian jitter) --------------------------
    num_fields = {}
    for raw_col, (staging_col, mn, mx, jitter_std, as_int) in _RAW_TO_STAGING_NUM.items():
        val_raw = src.get(raw_col)
        if val_raw is None or (not isinstance(val_raw, str) and pd.isna(val_raw)):
            num_fields[staging_col] = ""
            continue
        try:
            val = float(val_raw)
        except (ValueError, TypeError):
            num_fields[staging_col] = ""
            continue
        if jitter_std > 0:
            val += random.gauss(0, jitter_std)
        val = max(mn, min(mx, val))
        num_fields[staging_col] = str(int(round(val))) if as_int else str(round(val, 2))

    # GCS consistency (keep as-is — discrete ordinal, jitter=0)
    if all(num_fields.get(c) for c in ("gcs_augen", "gcs_verbal", "gcs_motorik")):
        total = int(num_fields["gcs_augen"]) + int(num_fields["gcs_verbal"]) + int(num_fields["gcs_motorik"])
        num_fields["gcs_gesamt"] = str(max(3, min(15, total)))

    # --- Procedures: preserve presence/absence exactly ---------------------
    proc_fields = _anonymize_procedures(src, admission)

    # --- Isolation / germs -------------------------------------------------
    iso_raw   = _raw("isolation_status")
    iso_grund = _ISOLATION_GRUND_MAP.get(_raw("isolation_grund"), _raw("isolation_grund"))
    iso_val   = "1" if iso_raw in ("Isolation", "Umkehrisolation") else "0"
    iso_fields = {
        "isolationsstatus":              iso_val,
        "isolationsgrund":               iso_grund if iso_val == "1" else "",
        "multiresistente_erreger":       "1" if iso_val == "1" and random.random() < 0.5 else "0",
        "mrsa_status":                   "0",
        "mrgn_3_status":                 "0",
        "mrgn_4_status":                 "0",
        "vre_status":                    "0",
        "andere_multiresistente_erreger":"0",
    }

    # --- Diagnoses from diag_data lookup -----------------------------------
    enc_key = str(src["a_encounter_num"]) if "a_encounter_num" in src.index and not pd.isna(src.get("a_encounter_num")) else None
    diagnoses = diag_lookup.get(enc_key, []) if enc_key else []
    diag_fields: dict = {}
    if diagnoses:
        diag_fields["icd10gm_code"] = diagnoses[0][0]
        diag_fields["diagnose_fuehrend"] = "1"
        diag_fields["diagnose_fuehrend_zusatzkennzeichen"] = diagnoses[0][1]
        for n, (icd, qual) in enumerate(diagnoses[1:10], start=2):
            diag_fields[f"diagnose_{n}"]                   = icd
            diag_fields[f"diagnose_{n}_zusatzkennzeichen"] = qual
    else:
        diag_fields = {
            "icd10gm_code": "", "diagnose_fuehrend": "",
            "diagnose_fuehrend_zusatzkennzeichen": "",
        }

    row: dict = {
        **_fresh_ids(index, admission),
        "geschlecht":                    cat_fields.get("geschlecht", ""),
        "aufnahme_zeitpunkt":            _ts_fmt(admission),
        "entlassung_zeitpunkt":          _ts_fmt(discharge),
        "triage_system":                 cat_fields.get("triage_system", "MTS"),
        "triage_stufe":                  cat_fields.get("triage_stufe", ""),
        "triage_zeitpunkt":              _ts_fmt(triage),
        "arztkontakt_beginn_zeitpunkt":  _ts_fmt(doctor),
        "arztkontakt_ende_zeitpunkt":    _ts_fmt(end_doctor),
        "therapiebeginn_zeitpunkt":      _ts_fmt(therapy_start),
        "therapieende_zeitpunkt":        _ts_fmt(therapy_end),
        "behandler_id":                  "",
        "zuweisungsart":                 cat_fields.get("zuweisungsart", "OTH"),
        "transportmittel":               cat_fields.get("transportmittel", ""),
        "vorstellungsgrund_cedis":       cat_fields.get("vorstellungsgrund_cedis", ""),
        "vorstellungsgrund_text":        "",
        "symptomdauer":                  num_fields.get("symptomdauer", ""),
        "atemfrequenz":                  num_fields.get("atemfrequenz", ""),
        "sauerstoffsaettigung":          num_fields.get("sauerstoffsaettigung", ""),
        "blutdruck_systolisch":          num_fields.get("blutdruck_systolisch", ""),
        "herzfrequenz":                  num_fields.get("herzfrequenz", ""),
        "koerperkerntemperatur":         num_fields.get("koerperkerntemperatur", ""),
        "schmerzskala":                  num_fields.get("schmerzskala", ""),
        "gcs_gesamt":                    num_fields.get("gcs_gesamt", ""),
        "gcs_augen":                     num_fields.get("gcs_augen", ""),
        "gcs_verbal":                    num_fields.get("gcs_verbal", ""),
        "gcs_motorik":                   num_fields.get("gcs_motorik", ""),
        "pupillenweite_rechts":          cat_fields.get("pupillenweite_rechts", "UNK"),
        "pupillenweite_links":           cat_fields.get("pupillenweite_links", "UNK"),
        "pupillenreaktion_rechts":       cat_fields.get("pupillenreaktion_rechts", "UNK"),
        "pupillenreaktion_links":        cat_fields.get("pupillenreaktion_links", "UNK"),
        "rankin_skala":                  num_fields.get("rankin_skala", ""),
        "verbleib_nach_notaufnahme":     cat_fields.get("verbleib_nach_notaufnahme", ""),
        "notfallanamnese":               "",
        "tetanusschutz":                 random.choice(["0", "1", "1", "1", ""]),
        **iso_fields,
        **proc_fields,
        **diag_fields,
        "patient_geburtsdatum":          birth_date.strftime("%Y-%m-%d"),
        **_empty_pii(),
        **_synthetic_insurance(admission_date),
        **_org_author_fields(**kw, admission_dt=admission),
        **_allergy_fields(0.30),
    }
    row["patient_geburtsdatum"] = birth_date.strftime("%Y-%m-%d")
    _diagnose_pad(row)
    return row


def _anonymize_procedures(src, admission_dt: dt.datetime) -> dict:
    import pandas as pd
    out = {}
    assigned: set = set()

    # Prefer timestamp columns (presence = performed + timestamp)
    for raw_col, (done_col, ts_col) in _RAW_PROC_TS.items():
        if done_col in assigned:
            continue
        val = src.get(raw_col)
        if val is None or (not isinstance(val, str) and pd.isna(val)):
            continue
        try:
            ts_dt = pd.to_datetime(val, utc=True).to_pydatetime().replace(tzinfo=None)
            # Shift by the same jitter applied to admission
            out[done_col] = "PB"
            out[ts_col]   = _ts_fmt(ts_dt)
            assigned.add(done_col)
        except Exception:
            pass

    # Boolean flag columns for procedures not yet covered
    for raw_col, (done_col, ts_col) in _RAW_PROC_FLAG.items():
        if done_col in assigned:
            continue
        val = src.get(raw_col)
        if val is None or (not isinstance(val, str) and pd.isna(val)):
            continue
        performed = bool(val) and str(val).strip() not in ("0", "False", "false", "")
        out[done_col] = "PB" if performed else "OPB"
        out[ts_col]   = ""
        assigned.add(done_col)

    # Default OPB for any not found in source
    for done_col, ts_col in _ALL_STAGING_PROCS_UNIQUE:
        out.setdefault(done_col, "OPB")
        out.setdefault(ts_col, "")

    return out


# ---------------------------------------------------------------------------
# Distribution analysis helpers  (embedded; no import of distribution_analyzer)
# ---------------------------------------------------------------------------

def _analyze_case_data(df) -> dict:
    import pandas as pd
    dist: dict = {
        "num": {}, "cat": {}, "missing": {},
        "hour_weights": [], "los_samples": [],
        "triage_offsets": [], "ak_offsets": [],
        "proc_absence": {},
    }
    dist["missing"] = df.isnull().mean().to_dict()

    for raw_col, (_, mn, mx, _, as_int) in _RAW_TO_STAGING_NUM.items():
        if raw_col not in df.columns:
            continue
        series = df[raw_col].dropna()
        if series.empty:
            continue
        if as_int:
            dist["num"][raw_col] = series.apply(lambda v: int(float(v))).tolist()
        else:
            dist["num"][raw_col] = series.apply(lambda v: round(float(v), 2)).tolist()

    # Age as numeric
    if "age_in_years" in df.columns:
        s = df["age_in_years"].dropna()
        dist["num"]["age_in_years"] = s.apply(lambda v: int(float(v))).tolist()

    for raw_col, (staging_col, mapping) in _RAW_TO_STAGING_CAT.items():
        if raw_col not in df.columns:
            continue
        series = df[raw_col].dropna().astype(str)
        if raw_col == "triage":
            series = series.apply(lambda v: str(int(float(v))))
        vc = series.value_counts()
        dist["cat"][raw_col] = vc.to_dict()

    # Temporal
    df = df.copy()
    df["aufnahme_ts"] = pd.to_datetime(df.get("aufnahme_ts"), errors="coerce")
    hc = df["aufnahme_ts"].dt.hour.value_counts().sort_index().reindex(range(24), fill_value=0)
    dist["hour_weights"] = hc.tolist()

    df["entlassung_ts"] = pd.to_datetime(df.get("entlassung_ts"), errors="coerce")
    los = (df["entlassung_ts"] - df["aufnahme_ts"]).dt.total_seconds() / 60
    dist["los_samples"] = los.dropna().pipe(lambda s: s[(s >= 0) & (s <= 2880)]).tolist()

    if "triage_ts" in df.columns:
        df["triage_ts"] = pd.to_datetime(df["triage_ts"], errors="coerce")
        t_off = (df["triage_ts"] - df["aufnahme_ts"]).dt.total_seconds() / 60
        dist["triage_offsets"] = t_off.dropna().pipe(lambda s: s[(s >= 0) & (s <= 120)]).tolist()

    if "start_arztkontakt_ts" in df.columns:
        df["start_arztkontakt_ts"] = pd.to_datetime(df["start_arztkontakt_ts"], errors="coerce")
        a_off = (df["start_arztkontakt_ts"] - df["aufnahme_ts"]).dt.total_seconds() / 60
        dist["ak_offsets"] = a_off.dropna().pipe(lambda s: s[(s >= 0) & (s <= 360)]).tolist()

    # Procedure absence rates
    _DONE_TO_DIST = {
        "labor_durchgefuehrt":                 "diagnostics_laboratory",
        "bga_durchgefuehrt":                   "diagnostics_blood_gases",
        "urinschnelltest_durchgefuehrt":       "diagnostics_urine_quick_test",
        "ekg_durchgefuehrt":                   "diagnostics_ecg",
        "sonographie_durchgefuehrt":           "diagnostics_ultrasound",
        "echokardiographie_durchgefuehrt":     "diagnostics_echocardiography",
        "cct_durchgefuehrt":                   "diagnostics_ct_head",
        "ct_durchgefuehrt":                    "diagnostics_ct",
        "traumascan_durchgefuehrt":            "diagnostics_ct_trauma",
        "roentgen_wirbelsaeule_durchgefuehrt": "diagnostics_xray_spine",
        "roentgen_thorax_durchgefuehrt":       "diagnostics_xray_thorax",
        "roentgen_becken_durchgefuehrt":       "diagnostics_xray_pelvis",
        "roentgen_extremitaet_durchgefuehrt":  "diagnostics_xray_extremities",
        "roentgen_sonstiges_durchgefuehrt":    "diagnostics_xray_others",
        "mrt_durchgefuehrt":                   "diagnostics_mrt",
    }
    for done_col, dist_key in _DONE_TO_DIST.items():
        # Prefer flag columns, fall back to ts columns
        found = False
        for flag_col, (dc, _) in _RAW_PROC_FLAG.items():
            if dc == done_col and flag_col in df.columns:
                dist["proc_absence"][dist_key] = float(df[flag_col].isnull().mean())
                found = True
                break
        if not found:
            for ts_col, (dc, _) in _RAW_PROC_TS.items():
                if dc == done_col and ts_col in df.columns:
                    dist["proc_absence"][dist_key] = float(df[ts_col].isnull().mean())
                    break

    return dist


def _analyze_diag_data(df) -> dict:
    dist: dict = {"icd_codes": {}, "diagnose_zusatz": {}, "diag_count": {}}
    if "icd_code" in df.columns:
        dist["icd_codes"] = df["icd_code"].dropna().value_counts().to_dict()
    if "diagnose_zusatz" in df.columns:
        dist["diagnose_zusatz"] = df["diagnose_zusatz"].dropna().value_counts().to_dict()
    if "a_encounter_num" in df.columns:
        cnt = df.groupby("a_encounter_num").size().value_counts()
        dist["diag_count"] = {int(k): int(v) for k, v in cnt.items()}
    return dist


def _build_diag_lookup(df) -> dict:
    import pandas as pd
    enc_col = next((c for c in ["a_encounter_num", "encounter_num", "fall_id"]
                    if c in df.columns), None)
    if enc_col is None:
        return {}
    lookup: dict = {}
    for _, row in df.iterrows():
        enc = row[enc_col]
        icd = row.get("icd_code", "")
        qual = row.get("diagnose_zusatz", "G")
        if pd.notna(enc) and pd.notna(icd) and str(icd).strip():
            key = str(enc)
            lookup.setdefault(key, []).append((
                str(icd),
                str(qual) if pd.notna(qual) and str(qual).strip() else "G",
            ))
    return lookup
