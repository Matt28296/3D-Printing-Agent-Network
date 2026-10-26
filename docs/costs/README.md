# Robot build costs

`robot_build_costs.xlsx` prices every bought part of the three robot test builds (desktop arm, tracked rover, hexapod) in Canadian dollars, as checked on 26 October 2026 (arm parts list updated for its round 3), plus PETG and print electricity. Every total is a live formula: change a price or a quantity (blue cells) and the totals update.

| Robot | Buying everything for it alone, with HST | Value of the parts it uses, with HST |
|---|---|---|
| Desktop robot arm | about $297 | about $181 |
| Tracked rover | about $381 | about $210 |
| Hexapod | about $461 | about $341 |
| All three bought together | about $917 | |

Not counted: the Logitech Brio 4K (already owned), shipping and tools. Prices come from Canadian retailers where one was readable, with US stores and a few labelled estimates otherwise; the Prices sheet gives each source and a confidence.

To rebuild after a price or BOM change: edit `prices_*.csv` or `bom.py`, run `python3 build_xlsx.py` from this folder (it writes `Robot build costs.xlsx` next to itself), then recalculate the workbook in LibreOffice or Excel. `python3 recalc.py` does both with LibreOffice installed and writes the totals to `costs.json`.

PETG and print time: the hexapod uses its sliced figures (26 Oct: 388 g, 31.6 h over 9 plates); the arm and rover still use estimates until their round 4 slices. The rover's N20 motors must have a 10 mm shaft (at least 9.6 mm), which doesn't change the price.
