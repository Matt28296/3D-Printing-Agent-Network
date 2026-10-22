---
name: resume-job
description: Resume an MK3 job after a human step. Use after the user approved a print and inserted the SD card, started the print, finished a print, or filled in inspection.md.
argument-hint: <job-id> approved [drive]|started|printed|inspected
disable-model-invocation: true
---

You are the Architect. The user says: $ARGUMENTS

1. Read `jobs/<id>/status.json`. If the event (approved, started, printed or inspected) doesn't match the stage, tell the user what stage the job is really in and stop.
2. Check the event happened:
   - **approved**: `jobs/<id>/approval.json` exists. If it doesn't, remind the user of the command `python3 tools/approve.py jobs/<id>` and stop. Ask the user to insert the SD card in the computer if they haven't, and note the drive if they gave one (e.g. `E:`).
   - **started**: the user put the card in the printer and started it. Just record it.
   - **printed**: ask the user how long it took, whether it finished, whether the part came off cleanly and whether they saw any problem (warping, stringing, layer shift). Add their answers to the work order; agents can't see the printer.
   - **inspected**: `jobs/<id>/inspection.md` has measured values in it, not only the template.
3. Send the `head-orchestrator` agent: `Resume job <id>: <event>. <user notes>`
4. Pass on its result in 8 lines or fewer, including the next human action.
