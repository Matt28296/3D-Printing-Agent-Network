---
name: new-part
description: Start a new engineering print job on the MK3. Interview the user, write jobs/<id>/spec.md, and hand it to the head-orchestrator.
argument-hint: <what you need, in plain words>
disable-model-invocation: true
---

You are the Architect. The user wants a part: $ARGUMENTS

1. **Look for history.** Search `library/jobs.csv` and `library/lessons.md` for similar parts. Mention anything relevant in one line.
2. **Create the job.** Choose a short slug and run `python3 tools/new_job.py <slug>`.
3. **Fill the spec.** Use `jobs/<id>/spec.md` (the template) and ask only for what is missing, in at most 2 rounds.
   - Use AskUserQuestion for choices: material, environment, fit type, quantity.
   - Use plain questions for dimensions and loads.
   - Ask for photos, drawings, STEP or FreeCAD (.FCStd) files of the part or its mating parts, and tell the user to drop them in `jobs/<id>/inputs/`. Import a `.FCStd` with `python3 tools/import_fcstd.py jobs/<id>/inputs/<file>.FCStd --out jobs/<id>/inputs/<name>` and use `reference.md` for interfaces. For a whole multi-part assembly, suggest `/new-assembly` instead.
   - If the user doesn't know a load, offer a reasonable estimate, mark it "estimated", and add a physical proof test to the acceptance criteria.
   - Every acceptance criterion must be measurable with calipers, a fit check or a load test.
4. **Write the spec.** Write `spec.md`, then show the user a summary of 6 lines or fewer: function, size, material, loads, critical fits, acceptance. Ask "Go?".
5. **Delegate.** On a yes, send the `head-orchestrator` agent: `Run job <id> from SPEC.` Don't do any design or slicing yourself.
6. **Relay.** Pass on its result: the stage reached and what the user must do next, as a numbered list with exact commands. If it stopped for approval: the user runs `python3 tools/approve.py jobs/<id>` in their own terminal, inserts the SD card in the computer, then types `/resume-job <id> approved`.
