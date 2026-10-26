# Robot build costs

`robot_build_costs.xlsx` prices every bought part of the three robot test builds (desktop arm, tracked rover, hexapod) in Canadian dollars, as checked on 26 October 2026, plus PETG and print electricity. Every total is a live formula: change a price or a quantity (blue cells) and the totals update.

| Robot | Buying everything for it alone, with HST | Value of the parts it uses, with HST |
|---|---|---|
| Desktop robot arm | about $288 | about $176 |
| Tracked rover | about $381 | about $210 |
| Hexapod | about $461 | about $342 |
| All three bought together | about $907 | |

Not counted: the Logitech Brio 4K (already owned), shipping and tools. Prices come from Canadian retailers where one was readable, with US stores and a few labelled estimates otherwise; the Prices sheet gives each source and a confidence.

To rebuild after a price or BOM change: edit `prices_*.csv` or `bom.py`, run `python3 build_xlsx.py` from this folder (it writes `Robot build costs.xlsx` next to itself), then recalculate the workbook in LibreOffice or Excel.
