# MK3 AutoPrint

A Claude Code project that takes a plain-language part request all the way to an inspected, engineering-grade print on an Original Prusa MK3, MK3S or MK3S+ that prints **from SD card** (no network connection). A hierarchy of agents does the work, and deterministic scripts plus safety hooks keep it honest.

- **Set it up:** [SETUP_PROMPT.md](SETUP_PROMPT.md)
- **Every agent prompt:** `.claude/agents/`
- **Knowledge the agents preload:** `.claude/skills/`
- **Project rules every agent loads:** [CLAUDE.md](CLAUDE.md)

---

## 1. What "fully automated" means here

**Automated:**
- requirements interview and spec, including reading your FreeCAD `.FCStd` parts and assemblies as references
- material and orientation decisions
- parametric CAD (build123d)
- manufacturability review
- strength check
- slicing (PrusaSlicer CLI)
- G-code validation
- copying the approved G-code to the SD card, verified byte for byte
- the inspection checklist
- recording measured results so the next job starts from them

**Still human, on purpose or because of physics:**
- loading and drying filament, and preparing the sheet
- **approving the exact G-code file**
- moving the SD card to the printer, starting the print on its LCD, and telling Claude how it went
- removing the part
- measuring and load-testing it
- typing a new Linear Advance K into your PrusaSlicer filament profile

`config/safety.json` has a `require_human_approval` switch. Setting it to `false` lets a validated file go to the SD card without approval; the tool and hook still re-validate every export. Keep it `true` unless someone is always near the printer.

**Honest limits:**
- **CAD.** Agent-written CAD is strong for prismatic functional parts: brackets, mounts, adapters, enclosures, jigs. It is weak at organic surfaces, complex lofts and anything judged on looks.
- **Strength.** A strength verdict is only as good as the material data behind it. Until you have measured calibration coupons, the best honest verdict for a loaded part is `NEEDS_TEST`, which adds a physical proof test to the acceptance criteria.
- **Offline printer.** Agents can't see the printer. Print time, failures and anything odd during the print come from what you report.
- **Hooks.** They are guardrails against mistakes, not a sandbox against a determined adversary.

## 2. Architecture

```
You
└─ Main session = ARCHITECT  (Opus · launch with --effort max)
   plans with you, writes jobs/<id>/spec.md, never builds anything
   └─ head-orchestrator  (Sonnet · high)
      runs the stage gates, sole writer of status.json, never builds
      ├─ design-lead       (Sonnet)  → cad-engineer (Sonnet*), dfm-reviewer (Haiku), strength-analyst (Sonnet*)
      ├─ slicing-lead      (Sonnet)  → slicer-engineer (Haiku), gcode-auditor (Haiku)
      ├─ print-ops-lead    (Sonnet)  → print-operator (Haiku)
      ├─ calibration-lead  (Sonnet)  → calibration-tech (Haiku) + borrows cad-engineer, slicer-engineer, gcode-auditor
      ├─ librarian         (Haiku)
      └─ toolsmith         (Sonnet)

Deterministic layer (no LLM): tools/*.py · tools/gcode_validator.py · tools/approve.py · .claude/hooks/*
```

The deepest chain is Architect → orchestrator → lead → worker. That is three layers below the main session, which is exactly Claude Code's default nesting limit for subagents.

### Stage gates

```
SPEC → DESIGN → SLICE → AWAITING_APPROVAL ─(you run approve.py, insert card)→ ON_SD_CARD
─(you start it on the LCD)→ PRINTING ─(you report it finished)→ AWAITING_INSPECTION
─(you fill inspection.md)→ RECORD → DONE
```

Each gate is a file whose first line is `VERDICT: PASS/FAIL`, or JSON with `"pass": true`. The orchestrator checks the files itself instead of trusting summaries. After three failures of the same gate it escalates to you instead of looping.

## 3. What each agent is equipped with

| Agent | Model | Claude Code tools | Preloaded skills | MCP |
|---|---|---|---|---|
| head-orchestrator | Sonnet | Agent, Read, Write, Edit, Glob, Grep | none | none |
| design-lead | Sonnet | Agent, Read, Write, Edit, Glob, Grep | fdm-design-rules, material-selection, prusaslicer-settings | none |
| cad-engineer | Sonnet | Read, Write, Edit, Bash, Glob, Grep | build123d-cad, fdm-design-rules | build123d |
| dfm-reviewer | Haiku | Read, Write, Glob, Grep, Bash | fdm-design-rules, material-selection | build123d |
| strength-analyst | Sonnet | Read, Write, Edit, Bash, Glob, Grep | strength-checks, material-selection | none |
| slicing-lead | Sonnet | Agent, Read, Write, Edit, Glob, Grep | prusaslicer-settings, material-selection | none |
| slicer-engineer | Haiku | Bash, Read, Write, Glob | none | none |
| gcode-auditor | Haiku | Bash, Read, Write, Glob, Grep | none | none |
| print-ops-lead | Sonnet | Agent, Read, Write, Edit, Glob, Grep | material-selection | none |
| print-operator | Haiku | Bash, Read | none | none |
| calibration-lead | Sonnet | Agent, Read, Write, Edit, Glob, Grep | calibration-methods, prusaslicer-settings, material-selection | none |
| calibration-tech | Haiku | Bash, Read, Write, Edit, Glob | calibration-methods, build123d-cad | none |
| librarian | Haiku | Read, Write, Edit, Glob, Grep | none | none |
| toolsmith | Sonnet | Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch | build123d-cad, calibration-methods | none |

**Project-wide equipment:**
- **Python venv** (`.venv`, from `requirements.txt`). A SessionStart hook puts it first on PATH, so every `python3` an agent runs has build123d, trimesh and the rest.
- **build123d MCP server** (build123d-mcp 0.3.90 via `uvx`). It adds interactive CAD measurement, printability analysis and hole detection. Its `export`, `bank_candidate` and `install_skill` tools are denied, so files only come from `tools/cad_build.py`.
- **pyright-lsp plugin** (official marketplace). It gives Python code intelligence and diagnostics to every agent that edits Python.
- **Tested tools** in `tools/`: `cadlib.py` (CAD helpers), `cad_build.py`, `render.py`, `mesh_check.py`, `slice.py`, `vendor_profiles.py`, `gcode_validator.py`, `approve.py`, `export_sd.py`, `new_job.py`. Setup adds `calibration/`.
- **CAD cookbook** in `docs/cad-cookbook/`: examples the test suite builds every run.
- **FreeCAD support without FreeCAD installed.** `tools/import_fcstd.py` reads `.FCStd` files (parts, Assembly-workbench joints) straight from the file. It exports each part as STEP/STL, lists every joint with its pin and bore diameters, flags parts too big for the bed, and gives the largest scale at which everything fits. Agents can build directly on the reference STEP geometry. Worked example: `docs/reference/excavator/` (FreeCAD's excavator-arm assembly: 13 parts, 16 joints; boom and stick need splitting or about 61 % scale).

**Deliberately not installed:**
- **Printer-control MCP servers.** The printer is offline, and they would bypass the approval gate anyway.
- **Community CAD plugins.** They don't add anything this setup lacks.

## 4. Design decisions, and why

1. **The filesystem is the message bus.** A subagent hands back only its final message. Putting every hand-off in `jobs/<id>/` makes each step checkable, resumable in a later session, and auditable.
2. **LLMs decide; scripts do.** Anything that must be exactly right lives in tested Python, not in a prompt: machine limits, G-code checks, the approval binding, printer API calls. Agents never write G-code; a hook blocks any `.gcode` write.
3. **One validator, three enforcement points.** `gcode-auditor`, `approve.py` and the PreToolUse hook all call the same `validate()`, so they can't disagree. An approval is bound to the file's SHA-256: change one byte and the approval is void.
4. **Knowledge as preloaded skills.** Design rules, material choice, slicer settings, CAD patterns, strength maths and calibration methods are project skills. Each agent preloads only the skills its job needs, so they are in context from its first turn, not left to chance. Skills live under `.claude/`, so agents can read them but not rewrite them.
5. **Model tiers follow Opus → Sonnet → Haiku, with two deliberate exceptions.** `cad-engineer` and `strength-analyst` run on Sonnet because wrong geometry code and wrong engineering calculations fail *silently*. Haiku workers do checklists, run tools and parse outputs. Change one `model:` line to experiment.
6. **A learning loop with a human in it.** Measured results go into `library/`, which overrides the defaults in the skills and is append-only. Proposed prompt or rule changes go to `library/proposed-changes.md` for you to apply.

## 5. Claude Code behaviour this relies on

Checked against the Claude Code docs in October 2026.

- **Subagent frontmatter:** `name`, `description`, `tools`, `model`, `effort` (`low` to `max`), `skills` (preloads the full skill text) and `color`.
- **Nesting:** subagents can spawn subagents up to 3 layers deep by default.
- **Spawn lists are not enforced.** An `Agent(name, …)` allowlist inside a subagent's tools is ignored, so which agents a lead calls is set by its prompt. Workers have no `Agent` tool.
- **MCP tools must be named.** A subagent with a `tools:` list must list MCP tools explicitly (`mcp__build123d__*`).
- **Hooks fire inside subagents too.** `CLAUDE_ENV_FILE` from a SessionStart hook applies to every Bash command.
- **Effort.** `effortLevel` in settings can't be `max`, so launch with `claude --effort max`.
- **Trust.** Project MCP approvals, `allow` rules, hooks and plugin declarations need workspace trust.

## 6. Setup

Follow [SETUP_PROMPT.md](SETUP_PROMPT.md). In short:
1. Unzip into a new folder.
2. Install uv and PrusaSlicer 2.9.x yourself.
3. Run `claude --effort max` in the folder and trust it.
4. Paste the prompt.

The setup session then:
- verifies the files
- builds the venv and runs the tests
- connects the MCP server and the plugin, then asks you to restart once
- interviews you about your printer and finds your SD card drive
- has toolsmith build the calibration tools
- runs a readiness check on all 14 agents
- runs a full dry-run design that stops at the approval gate

## 7. Daily use

| Step | You do |
|---|---|
| New part | `/new-part a bracket holding a 2 kg shelf, PETG, M4 screws` |
| Approve | in **your own terminal**: `python3 tools/approve.py jobs/<id>` |
| Copy to SD card | insert the card in the computer, then `/resume-job <id> approved` |
| Print | eject the card, insert it in the MK3, Print from SD → the named file, watch the first layer |
| After the print | `/resume-job <id> printed` (say how it went), then fill in `jobs/<id>/inspection.md` |
| Record | `/resume-job <id> inspected` |
| Print a FreeCAD assembly | copy the `.FCStd` into the folder, then `/new-assembly <file> <what it's for>` |
| Calibrate a material | `/calibrate PETG Prusament`, then `/calibrate PETG Prusament next` |
| What's waiting on me? | `/job-status` |

**Headless runs.** You can run a job headless once its spec is written. It still stops at the approval gate:

```bash
claude -p "Run job jobs/<id> from SPEC by delegating to the head-orchestrator agent." \
  --permission-mode dontAsk --max-turns 200 --output-format json
```

## 8. Safety model

| Risk | Control |
|---|---|
| Unapproved or changed file reaches the printer | Only `tools/export_sd.py` (protected) copies G-code to the card. It and the hook require `approval.json` whose SHA-256 matches, under 24 h old, plus a fresh validator pass. The copy is verified by hash |
| G-code copied or written by hand | Hooks block cp/mv/Copy-Item/robocopy/redirection of `.gcode`, and Write/Edit of `.gcode` anywhere, including the card |
| Agent approves its own print | Deny rule plus hook block `approve.py` and approval writes; `approve.py` refuses without a terminal |
| Dangerous G-code (over-temperature, out of bounds, EEPROM writes, cold extrusion, heaters left on, wrong printer or nozzle) | `tools/gcode_validator.py`, tested on real PrusaSlicer output |
| Agent edits the rules that limit it | Hooks plus deny rules block edits to `config/safety.json`, `.claude/` (agents, skills, hooks, settings), `CLAUDE.md`, the validator and the approver |
| Downloads and network tools | Hooks block curl, wget, Invoke-WebRequest and similar; no printer MCP |
| Runaway loops | 3-strike gate escalation; workers can't spawn agents |
| Bad material assumptions | Library-first rules; `NEEDS_TEST` verdicts add proof tests to acceptance criteria |

## 9. Extending it

- **Swap a model:** edit the agent's `model:` line.
- **OrcaSlicer:** add a second backend to `tools/slice.py` that reads the same `slice_plan.json`. Orca has hole-only XY compensation.
- **Enclosure or hardened nozzle:** update `config/printer.json`, and the material rules open up ASA, PC, PA and filled grades.
- **Going networked later:** fit a Raspberry Pi Zero 2 W with PrusaLink, then add a printer client behind the same approval gate.
- **Publishing:** the repo is self-contained. Commit everything except `.venv`, and keep secrets in environment variables only.

## 10. Still to verify on your machine

- The PrusaSlicer integration test on your version. It was tested here on 2.7.2; 2.9.x is expected to behave the same.
- A first real SD export and print with your card and card reader.
- **Windows:** the hooks run through Git Bash via `.claude/hooks/run_py.sh`, which finds a working Python (venv, `python`, `py -3` or `uv`) and **blocks everything** if none works, rather than failing open. Claude Code's PowerShell tool is switched off in settings, and the guard also understands PowerShell commands in case it's switched back on.
- Commands you type with Claude Code's `!` prefix probably bypass hooks. `approve.py` refuses non-terminal input anyway, but run approvals in a separate terminal.
