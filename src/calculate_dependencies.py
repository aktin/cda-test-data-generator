import pandas as pd
import datetime as dt


def calculate_dependencies(filename: str) -> None:
    df = pd.read_csv(filename, dtype=str, na_values=[], keep_default_na=False)

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
        x = dt.timedelta(minutes=int(row["_entlassung_triagestart"]))
        y = dt.datetime.strptime(row["entlassung_ts"], "%Y%m%d%H%M%S")
        row["triage_ts_start"] = (y + x).strftime("%Y%m%d%H%M")

        # Triage_end
        x = dt.timedelta(minutes=int(row["_triagestart_triageend"]))
        y = dt.datetime.strptime(row["triage_ts_start"], "%Y%m%d%H%M")
        row["triage_ts_end"] = (y + x).strftime("%Y%m%d%H%M")


    df.to_csv(filename, index=False)
