---
name: start-here
description: 'Start here (lead) — the one prompt for any start: a new idea in chat, uploaded documentation, or an existing project. Paste it to the `lead` agent and keep only the block that fits.'
argument-hint: 'your idea, the documents you attached, or the repo path'
agent: lead
---
<!-- GENERATED from prompts/00-start-here.md by scripts/build-prompts.py -->
@lead start project ${input:project_name}. Resume from docs/project-state.md if it exists.

Input (keep the one that applies):
- IDEA: ${input:idea}
- DOCUMENTS: ${input:documents} — use the document-ingest skill; cite doc + section/page for every item; never invent.
- EXISTING PROJECT: ${input:repo_paths} — first ask explorer for a quick read-only overview per repo, then ask me before going deep.

Work through your pipeline and stop at every gate for my approval:
GATE 1 project brief → GATE 2 decisions (ADRs) → GATE 3 architecture plan → GATE 4 backlog before creating issues.
Ask me ONE question at a time (docs/agents/interaction-standard.md): a recommended answer, 2–4 options with a one-line consequence each, and "other"; most blocking first; adapt the next question to my answer; never ask what the documents or repo already say; summarise every 3–5 answers. I may reply "go with your suggestions", "skip", "later" or "recommend for me".
Each GATE is a single question: "Approve? yes / changes".
Keep reports short and in plain language: what was done, what I need to decide, what happens next.
Never merge, release, create repos/issues before the gate, touch servers, or show secret values.
Update docs/project-state.md after every step.
