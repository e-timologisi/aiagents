---
name: document-ingest
description: "Extract requirements, terms, constraints, stakeholders, risks, contradictions and gaps from uploaded documents (md, txt, PDF, images, docx exports) with source references and confidence. Use when the owner provides specifications, tenders, regulations, notes or screenshots."
---

# Document ingest

## Steps
1. **Inventory**: list every document (name, type, pages/sections, date, author if stated). Ask for missing files the documents reference.
2. **Chunk long documents** by section or ~10 pages; process chunks in order and keep a running list, so nothing is lost to context limits. Note which chunks were read.
3. **Extract** per chunk:
   - requirements (functional, non-functional) → `R-001…`
   - constraints (legal/compliance, technical, budget, deadlines) → `C-001…`
   - glossary terms → term, meaning, source
   - stakeholders and roles
   - risks → `K-001…`
4. **Cite** every item: `<doc> §<section>` or `<doc> p.<page>`; quote short phrases for critical items.
5. **Confidence**: `high` (explicit), `medium` (clear but implicit), `low` (interpreted). Never invent; unclear = gap.
6. **Contradictions**: items that conflict across or within documents, with both sources.
7. **Gaps**: what a builder needs but the documents do not say → questions for the owner, each with a recommended answer.
8. Write `docs/requirements-register.md` (`requirements-register` skill) and a summary for the lead.

## Images and PDFs
- Screenshots/mockups: describe screens, fields and flows; tag `confidence: medium` unless labels are legible.
- Scanned PDFs: if text is unreadable, say which pages and ask for a text version.
- Tables: keep them as tables; note units and currency.
- Never copy personal data from documents into the register; replace with descriptions.

## Legal content
Summaries of laws or regulations are `to be validated by {{DOMAIN_EXPERT}}`; never add figures or obligations that are not in the source.

## Asking the owner (after extraction)
Extract everything first. Then ask ONLY the genuinely open questions (gaps, contradictions, low-confidence items that matter), **one question at a time**, most blocking first, per `docs/agents/interaction-standard.md`: recommended answer, 2–4 options with consequences, "other". Never ask what a document already answers; quote it and ask only to confirm if it matters. Questions you do not ask now go to the question queue with a default.
