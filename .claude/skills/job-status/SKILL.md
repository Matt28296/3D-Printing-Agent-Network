---
name: job-status
description: Summarize MK3 print jobs (one job, or all open jobs) and list what each is waiting for. Use when the user asks where a job stands or what needs their attention.
argument-hint: [job-id]
---

Read `jobs/*/status.json`, or only `jobs/$ARGUMENTS/status.json` if a job id was given. Don't delegate, and don't change anything.

Reply with one line per job: id · stage · last update · what it waits for.
- **AWAITING_APPROVAL**: `python3 tools/approve.py jobs/<id>` in your own terminal
- **ON_SD_CARD**: put the card in the printer and Print from SD → the file named in `sd_export.json`
- **PRINTING**: you're printing it; tell Claude `/resume-job <id> printed` when it's done (estimated time is in `slice_stats.json`)
- **AWAITING_INSPECTION**: fill in `jobs/<id>/inspection.md`

List jobs waiting on the user first. Skip DONE jobs unless the user asked for that job by id.
