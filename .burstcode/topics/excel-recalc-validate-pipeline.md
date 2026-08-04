# How does `recalc.py`'s LibreOffice headless recalculation integrate with `validate_dcf.py`'s `data_only=True` workbook loading to ensure formula values are computed before validation checks run?

_Topic id: `excel-recalc-validate-pipeline` — generated at 2026-05-15T11:40:18.033Z_

> `validate_dcf.py` explicitly loads the workbook with `data_only=True` to check computed values, but `recalc.py` notes that openpyxl writes formulas without computing them. The pipeline likely requires `recalc.py` to run first, but there's no explicit orchestration visible here. Investigating how these two scripts are chained or if `validate_dcf.py` fails silently when formulas aren't pre-calculated.

## Summary

No investigation topic was provided in the prompt. The field after 'Investigation topic:' is empty, so there is nothing to investigate.
