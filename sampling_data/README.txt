Place your AKTIN raw export files here:

  case_data.txt   — tab-separated case-level export
  diag_data.txt   — tab-separated diagnosis export (joined by a_encounter_num)

Then run:

  python generate.py --mode empirical --count 200
  python generate.py --mode anonymize --count 50

No --data-dir flag needed when files are in this folder.
