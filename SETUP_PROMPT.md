# Setup prompt

## Before you paste it (2 minutes)

1. Make a new, empty folder, e.g. `~/mk3-autoprint`, and unzip `mk3-autoprint.zip` into it so that `CLAUDE.md` sits directly in that folder.
2. Install **uv** yourself; Claude can't, because downloads with curl are blocked in this project on purpose.
   - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows PowerShell: `irm https://astral.sh/uv/install.ps1 | iex`
   - Then open a **new** terminal.
3. Install **PrusaSlicer 2.9.x** from prusa3d.com if it isn't installed already.
   - Have the printer's **SD card** and a card reader for this computer handy. This setup is for an offline MK3 that prints from SD card.
   - **Windows:** also install **Git for Windows** (git-scm.com). Claude Code uses its Git Bash to run commands and the safety hooks. The project switches off Claude Code's PowerShell tool so every command goes through the guarded Bash path.
4. `cd` into the folder and start Claude Code: `claude --effort max`. Accept the "trust this folder" prompt and the prompt to enable the project MCP server `build123d`. The safety hooks, agents, skills and MCP server only load in a trusted folder.
5. Paste everything inside the box below.

---

```text
You are setting up MK3 AutoPrint in this folder: a multi-agent Claude Code system that designs, analyses, slices and, only with my approval, prints engineering-grade parts on my Original Prusa MK3 / MK3S / MK3S+. My printer is OFFLINE: every print goes to it on its SD card, which I move from this computer to the printer and start from the printer's LCD. Your job in this session is to make every agent fully equipped (tools, skills, MCP server, plugins, Python environment, printer config), prove each one works, and finish with a dry run that stops at the approval gate.

RULES FOR THIS SESSION
- You are the Architect from CLAUDE.md. For setup only, you may run setup commands yourself and send readiness checks to any agent directly.
- Install into the project's .venv, or with `uv tool`, without asking. Ask me before anything else: system packages, global installs, software not named here.
- Never copy G-code to an SD card in this session. Never run tools/approve.py. Never edit anything under .claude/, CLAUDE.md, config/safety.json, tools/gcode_validator.py, tools/approve.py or tools/export_sd.py: they are protected. If one of them needs a change, tell me the exact change.
- If a step fails, fix it or report it plainly. Never skip a step silently, and never weaken a test to make it pass.
- Keep a task list with one item per phase. At the end of each phase, report to me in 5 lines or fewer.

PHASE 0: CONFIRM THE PROJECT LOADED
1. Check that CLAUDE.md is in this folder.
   - If it isn't but mk3-autoprint.zip is: unzip it here so CLAUDE.md is at the top level. Then tell me to type /exit and run `claude --continue --effort max`, and stop. Agents, hooks and skills load only at startup.
2. Check that your available agent types include head-orchestrator, design-lead, cad-engineer, dfm-reviewer, strength-analyst, slicing-lead, slicer-engineer, gcode-auditor, print-ops-lead, print-operator, calibration-lead, calibration-tech, librarian and toolsmith. If any are missing, say which.
3. Verify the files:
   - Run: python3 -c "import hashlib,pathlib,sys;bad=[l.split('  ',1)[1] for l in pathlib.Path('MANIFEST.sha256').read_text().splitlines() if l and hashlib.sha256(pathlib.Path(l.split('  ',1)[1]).read_bytes()).hexdigest()!=l.split('  ',1)[0]];print('MANIFEST OK' if not bad else bad)"
   - Then confirm these safety-critical files have exactly these SHA-256 hashes. Use `sha256sum <files>`, or `shasum -a 256 <files>` on macOS; a Python one-liner naming these paths is blocked by the safety hook.
     5cd2e35e2829b501f44ce2c63b6feb7bb6c56d6f5ce949394b601357be9da0ce  .claude/hooks/guard_bash.py
     9593dececfd4f51d7cc1d01df35b61141a52af458b097ebd497f2d8995ec1f3a  .claude/hooks/protect_paths.py
     a74f7a253f00d29a179c931742e958c7e9bf28beff56e0ad952ff44657b3c42a  .claude/hooks/run_py.sh
     45fa21928088d0ed766f7846ad3cbf27cec296a326eaea9d1cde821537793fbd  tools/gcode_validator.py
     3419ff288c88d15058992ad2270c70ca04592faddfc8340e5d391befcca5ca29  tools/approve.py
     59bb3be1e0551a4f93f6142d73e859f18fd931a926e4db5c163185d554d07b4d  tools/export_sd.py
     f08bac1be9a45311f556cb0b7d5663cd8f69d5da99ad6869ee37d4768547e3e3  config/safety.json
     53c06c60876d5c5738a02fd4e06d96792018cf010ca6cb0521d7e4f3c8aadf07  .claude/settings.json
   - If anything differs, STOP and tell me. Don't continue.
4. Read CLAUDE.md, README.md and docs/tools-spec.md.

PHASE 1: SYSTEM PREREQUISITES (detect and report; don't install system software)
- Report: OS, shell, git, uv (`uv --version`), Python versions uv can use, and Node.js (optional).
- Find the PrusaSlicer command-line executable:
  - Linux: `prusa-slicer`, or the Flatpak or AppImage
  - macOS: /Applications/PrusaSlicer.app/Contents/MacOS/PrusaSlicer
  - Windows: C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe
- Print its version, and write the full path into config/printer.json "prusaslicer_path".
- If uv or PrusaSlicer is missing, stop and tell me exactly what to install.

PHASE 2: PROJECT PYTHON ENVIRONMENT
- Create and fill the venv: `uv venv --python 3.12 .venv`, then `uv pip install --python .venv -r requirements.txt`
- Check the imports and print versions: `.venv/bin/python -c "import build123d, trimesh, numpy, scipy, matplotlib, requests; print(build123d.__version__, trimesh.__version__)"` (on Windows use .venv\Scripts\python).
- Run the whole test suite with the venv's Python: `.venv/bin/python -m pytest -q`. It must pass, including the PrusaSlicer integration test (set PRUSASLICER=<path> for this run if needed).
  - If the integration test fails because my PrusaSlicer version differs from 2.7/2.9 behaviour, delegate the fix of tools/slice.py to the toolsmith agent and re-run.
  - If a protected file's test fails, report it to me.

PHASE 3: CLAUDE CODE INTEGRATIONS
- MCP server (declared in .mcp.json and pre-approved in .claude/settings.json):
  - Run `uvx --python 3.12 build123d-mcp@0.3.90 --version`.
  - Run `claude mcp list` and confirm build123d is listed.
- Plugin (declared in .claude/settings.json):
  - If `claude plugin marketplace list` lacks claude-plugins-official, run `claude plugin marketplace add anthropics/claude-plugins-official`.
  - Run `claude plugin install pyright-lsp@claude-plugins-official --scope project`.
  - Install its language server with `uv tool install pyright`, and confirm `pyright-langserver` is on PATH.
- Optional extras: offer these, don't install them.
  - commit-commands@claude-plugins-official, for git commit helpers.
  - The GitHub connector or plugin, if I want to publish this project.
  - Do NOT add any printer-control or OctoPrint/PrusaLink MCP server. This printer is offline, and G-code reaches it only through tools/export_sd.py, behind the safety hooks.
- Then tell me to type /exit, open a new terminal if I just installed uv or pyright, run `claude --continue --effort max` in this folder, and say "continue setup". Stop here.

PHASE 4: AFTER THE RESTART, VERIFY THE SESSION
- `python3 -c "import sys; print(sys.executable)"` must print a path inside this project's .venv. The SessionStart hook does this; on Windows it also maps `python3` to the venv's python.exe.
- Call mcp__build123d__version and mcp__build123d__health_check, and show me the results.
- pyright-lsp must be enabled: check with `claude plugin list`, or the /plugin menu if that command doesn't exist in my version.
- Safety hook check (one attempt only): run `python3 tools/approve.py jobs/none`. It must be BLOCKED by the deny rule or the hook. Show me the message.

PHASE 5: MY PRINTER, MATERIALS AND PROFILES
Use one round of AskUserQuestion, then write config/printer.json. Ask:
- printer: MK3, MK3S or MK3S+, with or without an MMU
- nozzle: 0.4 brass, hardened, or other
- enclosure: yes or no
- print sheets I own
- filaments on hand (brand + type + colour)
- SD card: ask me to insert it in this computer now, then run `python3 tools/export_sd.py --list` and ask me to confirm which drive it is. Save that drive in config/printer.json "sd_drive". If no drive appears, ask me for the drive letter or mount path.
Then profiles:
- If I have tuned PrusaSlicer profiles, tell me exactly how to export them into profiles/ (see profiles/README.md), and wait.
- Otherwise generate Prusa's stock profiles with tools/vendor_profiles.py:
  - my printer
  - 0.20mm QUALITY @MK3, plus any STRUCTURAL @MK3 print profile if `--list print --filter MK3` shows one
  - one filament profile per material I own (closest Prusament or Generic match)
- Put the profile paths in config/printer.json "profiles".

PHASE 6: BUILD THE CALIBRATION TOOLS (delegate to toolsmith)
Have toolsmith implement docs/tools-spec.md items 8 and 9, test-first:
- the calibration generators plus analyze.py, following the calibration-methods skill
- their tests
Every generated G-code file must pass tools/gcode_validator.py.
Review each return and re-delegate fixes until `python3 -m pytest -q` passes.
There is no printer client or monitor to build: the printer is offline and tools/export_sd.py (provided, protected, tested) handles the SD card.

PHASE 7: AGENT READINESS CHECK (every agent, in parallel batches)
The slash commands to confirm exist: /new-part, /new-assembly, /resume-job, /calibrate, /job-status.
Send each of the 14 agents this work order:

  "READINESS CHECK. Don't delegate, and don't create or change any file. Report:
   (1) the tool names you have
   (2) the title of each preloaded skill
   (3) the result of one harmless command from your allowed set, if you have Bash (e.g. `python3 tools/cad_build.py --help`)
   (4) if you have mcp__build123d tools: the result of mcp__build123d__version
   (5) READY, or exactly what is missing"

Then show me one table: agent · model · skills · MCP · harmless-command result · READY? Fix whatever is missing that I'm allowed to fix, and tell me about the rest.

PHASE 7b: FREECAD REFERENCE CHECK
Run `python3 tools/import_fcstd.py docs/reference/excavator/AssemblyExample.FCStd`. It must report 13 parts, 16 joints, and Boom and Stick too big for the bed. If I have my own FreeCAD files, tell me to copy them into this folder and that `/new-assembly <file>` or `/new-part` will use them.

PHASE 8: DRY RUN (design and slice only; no printing)
1. Create job `dryrun-l-bracket` with tools/new_job.py, and write its spec:
   - L-bracket, two legs 40 mm long, 20 mm wide
   - leg thickness: designer's choice, maximum 12 mm
   - one Ø 4.5 mm clearance hole for an M4 screw in each leg, 15 mm from the leg's end
   - PETG, room temperature indoors
   - 50 N static load at the tip of one leg, perpendicular to the leg
   - acceptance criteria: M4 screws pass freely; leg length 40.0 ± 0.3 mm; holds 50 N for 1 minute with no cracking or layer separation
2. Hand it to the head-orchestrator. Expect the strength check to push the design thicker before it passes. It must stop at AWAITING_APPROVAL.
3. Show me:
   - renders/iso.png
   - the orientation decision in design_brief.md
   - the strength.md verdict and lowest safety factor
   - the design_review.md verdict
   - audit.md
   - print time and grams
   - how many DESIGN and SLICE iterations it took
4. Prove the gate:
   - Run `python3 tools/export_sd.py jobs/<dry-run-id> --drive <my sd_drive> --dry-run`. The hook allows it, and the tool itself must answer NOT EXPORTED: no human approval.
   - Run the same command without `--dry-run`. The hook must BLOCK it for lack of approval, and nothing may appear on the card.
   - Show me both outputs. Don't try any other route.

PHASE 9: VERSION CONTROL
`git init` if needed, then commit everything except what .gitignore excludes, with the message "MK3 AutoPrint: initial setup".

PHASE 10: FINAL REPORT
Give me:
- the agent readiness table
- the integrations: venv, MCP server, plugin, hooks and their status
- the test count
- the dry-run summary
- what is still unverified (for example a first real SD export and print)
- the exact /calibrate command to start calibrating my main material
```
