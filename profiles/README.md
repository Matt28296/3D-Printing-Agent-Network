# Profiles

Agents build every slice from these files plus explicit overrides in `slice_plan.json`. One `.ini` per profile:

- `printer/`: your MK3/MK3S printer profile
- `print/`: the print profiles agents may start from (e.g. 0.20mm QUALITY)
- `filament/`: one file per filament you own

**Best: your own tuned profiles.** In PrusaSlicer, select the profile in each tab, then use File → Export → Export Config.

**Fallback: Prusa's stock profiles,** generated from the vendor bundle that ships with PrusaSlicer:

    python3 tools/vendor_profiles.py --list printer --filter MK3S
    python3 tools/vendor_profiles.py --printer "Original Prusa i3 MK3S & MK3S+" \
        --print "0.20mm QUALITY @MK3" --filament "Prusament PETG" --filament "Prusament PLA"
