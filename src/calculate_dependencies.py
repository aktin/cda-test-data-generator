import pandas as pd
import datetime as dt


def calculate_dependencies(filename: str) -> None:
    df = pd.read_csv(filename, dtype=str)

    for _, row in df.iterrows():
        # Therapiebeginn
        row["therapiebeginn_ts"] = (dt.datetime.strptime(row["aufnahme_ts"], "%Y%m%d%H%M%S")
                                    + dt.timedelta(minutes=int(row["_aufnahme_therapiebeginn"]))).strftime("%Y%m%d%H%M%S")

        # Arztkontakt
        row["arztkontakt_ts"] = (dt.datetime.strptime(row["therapiebeginn_ts"], "%Y%m%d%H%M%S")
                                    + dt.timedelta(minutes=int(row["_therapiebeginn_arztkontakt"]))).strftime("%Y%m%d%H%M%S")

        # End Arztkontakt
        row["end_arztkontakt_ts"] = (dt.datetime.strptime(row["arztkontakt_ts"], "%Y%m%d%H%M%S")
                                    + dt.timedelta(minutes=int(row["_arztkontakt_endarztkontakt"]))).strftime("%Y%m%d%H%M%S")

        # Entlassung
        row["entlassung_ts"] = (dt.datetime.strptime(row["end_arztkontakt_ts"], "%Y%m%d%H%M%S")
                                    + dt.timedelta(minutes=int(row["_endarztkontakt_entlassung"]))).strftime("%Y%m%d%H%M%S")

        # Triage_start
        row["triage_ts_start"] = (dt.datetime.strptime(row["entlassung_ts"], "%Y%m%d%H%M%S")
                                    + dt.timedelta(minutes=int(row["_entlassung_triagestart"]))).strftime("%Y%m%d%H%M")

        # Triage_end
        row["triage_end_ts"] = (dt.datetime.strptime(row["triage_ts_start"], "%Y%m%d%H%M")
                                  + dt.timedelta(minutes=int(row["_triagestart_triageend"]))).strftime("%Y%m%d%H%M")

    df.to_csv(filename, index=False)