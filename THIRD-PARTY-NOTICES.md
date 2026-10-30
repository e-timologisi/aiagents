# Third-party notices

The aiagents kit is licensed under the MIT License, Copyright (c) 2026 e-timologisi (see `LICENSE`).
It also contains material copied or adapted from the third-party projects below. **That material
remains under its original MIT license and copyright**, reproduced in full here; the e-timologisi
copyright does not apply to it. Each third-party skill directory also carries `LICENSE.upstream` and
`UPSTREAM.md`, and installs copy this file to `docs/agents/THIRD-PARTY-NOTICES.md` so the notices
travel with the files.

## mattpocock/skills

Source: https://github.com/mattpocock/skills (retrieved 2026-10-30)

```text
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## humanlayer/skills

Source: https://github.com/humanlayer/skills (retrieved 2026-10-30). Used in `core/skills/pr/SKILL.md` (Summary
section: menu of visuals and placement guidance), taken from the `show-me` skill
([plugins/show-me/skills/show-me/SKILL.md](https://github.com/humanlayer/skills/blob/bba9d13ab34f0a87f1cc33df4dd196372393ddfc/plugins/show-me/skills/show-me/SKILL.md), last upstream commit
`bba9d13ab34f`) via mattpocock/skills' `pr` skill. The `pr` frontmatter `metadata.credits` and
`core/skills/pr/CREDITS.md` keep that credit.

```text
MIT License

Copyright (c) 2026 HumanLayer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Provenance

Compared programmatically on 2026-10-30 (difflib ratio on whitespace-normalised text without
frontmatter, against the current upstream file; then exact match against the upstream file history).
"Ratio" is against the current upstream file; "Kit matches upstream commit" is the upstream revision
the kit copy was taken from.

| Kit path | Upstream | Kit matches upstream commit | Last upstream commit touching path | Ratio | Status |
|---|---|---|---|---|---|
| `core/skills/code-review/SKILL.md` | [mattpocock/skills/skills/engineering/code-review/SKILL.md](https://github.com/mattpocock/skills/blob/3da8c01116264675eeefbd6e9d59c734de9095cc/skills/engineering/code-review/SKILL.md) | `3da8c0111626` | `7739eaed7f8f` | 0.996 | identical to an earlier upstream revision |
| `core/skills/codebase-design/SKILL.md` | [mattpocock/skills/skills/engineering/codebase-design/SKILL.md](https://github.com/mattpocock/skills/blob/321658273cb1d20b76026717d027d505790106d4/skills/engineering/codebase-design/SKILL.md) | `321658273cb1` | `321658273cb1` | 1.000 | identical |
| `core/skills/codebase-design/DEEPENING.md` | [mattpocock/skills/skills/engineering/codebase-design/DEEPENING.md](https://github.com/mattpocock/skills/blob/321658273cb1d20b76026717d027d505790106d4/skills/engineering/codebase-design/DEEPENING.md) | `321658273cb1` | `321658273cb1` | 1.000 | identical |
| `core/skills/codebase-design/DESIGN-IT-TWICE.md` | [mattpocock/skills/skills/engineering/codebase-design/DESIGN-IT-TWICE.md](https://github.com/mattpocock/skills/blob/d80fa0f4ebe0c5714af0adf8670336065233ecc6/skills/engineering/codebase-design/DESIGN-IT-TWICE.md) | `d80fa0f4ebe0` | `7739eaed7f8f` | 0.994 | identical to an earlier upstream revision |
| `core/skills/diagnosing-bugs/SKILL.md` | [mattpocock/skills/skills/engineering/diagnosing-bugs/SKILL.md](https://github.com/mattpocock/skills/blob/f3fc5632f401156837ee3872f14fe33ccf1024ea/skills/engineering/diagnosing-bugs/SKILL.md) | `f3fc5632f401` | `f3fc5632f401` | 1.000 | identical |
| `core/skills/diagnosing-bugs/scripts/hitl-loop.template.sh` | [mattpocock/skills/skills/engineering/diagnosing-bugs/scripts/hitl-loop.template.sh](https://github.com/mattpocock/skills/blob/321658273cb1d20b76026717d027d505790106d4/skills/engineering/diagnosing-bugs/scripts/hitl-loop.template.sh) | `321658273cb1` | `321658273cb1` | 1.000 | identical |
| `core/skills/domain-modeling/SKILL.md` | [mattpocock/skills/skills/engineering/domain-modeling/SKILL.md](https://github.com/mattpocock/skills/blob/d80fa0f4ebe0c5714af0adf8670336065233ecc6/skills/engineering/domain-modeling/SKILL.md) | `d80fa0f4ebe0` | `d80fa0f4ebe0` | 1.000 | identical |
| `core/skills/domain-modeling/ADR-FORMAT.md` | [mattpocock/skills/skills/engineering/domain-modeling/ADR-FORMAT.md](https://github.com/mattpocock/skills/blob/321658273cb1d20b76026717d027d505790106d4/skills/engineering/domain-modeling/ADR-FORMAT.md) | `321658273cb1` | `321658273cb1` | 1.000 | identical |
| `core/skills/domain-modeling/GLOSSARY-FORMAT.md` | [mattpocock/skills/skills/engineering/domain-modeling/GLOSSARY-FORMAT.md](https://github.com/mattpocock/skills/blob/d80fa0f4ebe0c5714af0adf8670336065233ecc6/skills/engineering/domain-modeling/GLOSSARY-FORMAT.md) | `d80fa0f4ebe0` | `d80fa0f4ebe0` | 1.000 | identical |
| `core/skills/grilling/SKILL.md` | [mattpocock/skills/skills/productivity/grilling/SKILL.md](https://github.com/mattpocock/skills/blob/95249b0b49782349740fd9b8c6ce32b4e59e497a/skills/productivity/grilling/SKILL.md) | `95249b0b4978` | `7739eaed7f8f` | 0.992 | identical to an earlier upstream revision |
| `core/skills/pr/SKILL.md` | [mattpocock/skills/skills/engineering/pr/SKILL.md](https://github.com/mattpocock/skills/blob/e484a8095543718ced436b9b49a8160ed4554000/skills/engineering/pr/SKILL.md) | `e484a8095543` | `e484a8095543` | 1.000 | identical (upstream itself incorporates humanlayer/skills `show-me`, see THIRD-PARTY-NOTICES.md) |
| `core/skills/pr/CREDITS.md` | [mattpocock/skills/skills/engineering/pr/CREDITS.md](https://github.com/mattpocock/skills/blob/a7d038f6bf7f01b516408e95e2fb56e0b338fa6f/skills/engineering/pr/CREDITS.md) | `a7d038f6bf7f` | `a7d038f6bf7f` | 1.000 | modified: `show-me` link corrected from humanlayer/humanlayer to humanlayer/skills (2026-10-30) |
| `core/skills/tdd/SKILL.md` | [mattpocock/skills/skills/engineering/tdd/SKILL.md](https://github.com/mattpocock/skills/blob/3f599139104dfceabc7754eeb91319802f85e042/skills/engineering/tdd/SKILL.md) | `3f599139104d` | `3f599139104d` | 1.000 | identical |
| `core/skills/tdd/mocking.md` | [mattpocock/skills/skills/engineering/tdd/mocking.md](https://github.com/mattpocock/skills/blob/62f43a18177be6ec82da242e59ffbc490a4c22ea/skills/engineering/tdd/mocking.md) | `62f43a18177b` | `62f43a18177b` | 1.000 | identical |
| `core/skills/tdd/tests.md` | [mattpocock/skills/skills/engineering/tdd/tests.md](https://github.com/mattpocock/skills/blob/43ea0884b07a3e67a5a07f025ce92aefa983177b/skills/engineering/tdd/tests.md) | `43ea0884b07a` | `43ea0884b07a` | 1.000 | identical |
| `core/skills/writing-for-agents/SKILL.md` | [mattpocock/skills/skills/productivity/writing-for-agents/SKILL.md](https://github.com/mattpocock/skills/blob/321658273cb1d20b76026717d027d505790106d4/skills/productivity/writing-for-agents/SKILL.md) | `321658273cb1` | `321658273cb1` | 0.932 | modified: section "Agent source format (this project)" appended (kit-authored) |
| `core/skills/writing-for-agents/SKILL-MECHANICS.md` | [mattpocock/skills/skills/productivity/writing-for-agents/SKILL-MECHANICS.md](https://github.com/mattpocock/skills/blob/321658273cb1d20b76026717d027d505790106d4/skills/productivity/writing-for-agents/SKILL-MECHANICS.md) | `321658273cb1` | `321658273cb1` | 1.000 | identical |
| `core/docs-templates/domain.md` | [mattpocock/skills/skills/engineering/setup-matt-pocock-skills/domain.md](https://github.com/mattpocock/skills/blob/d80fa0f4ebe0c5714af0adf8670336065233ecc6/skills/engineering/setup-matt-pocock-skills/domain.md) | `d80fa0f4ebe0` | `d80fa0f4ebe0` | 0.924 | modified: multi-context layout example removed; attribution comment added |
| `core/docs-templates/issue-tracker.md` | [mattpocock/skills/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md](https://github.com/mattpocock/skills/blob/5b7cade4d68947f34dae71326a0ce89f09e22c9c/skills/engineering/setup-matt-pocock-skills/issue-tracker-github.md) | `5b7cade4d689` | `59db609eb1e1` | 0.700 | identical to an earlier upstream revision (renamed); attribution comment added |
| `core/docs-templates/triage-labels.md` | [mattpocock/skills/skills/engineering/setup-matt-pocock-skills/triage-labels.md](https://github.com/mattpocock/skills/blob/5b7cade4d68947f34dae71326a0ce89f09e22c9c/skills/engineering/setup-matt-pocock-skills/triage-labels.md) | `5b7cade4d689` | `5b7cade4d689` | 1.000 | identical; attribution comment added |

Third-party directories (each has `UPSTREAM.md` + `LICENSE.upstream`):

- `core/skills/code-review/`
- `core/skills/codebase-design/`
- `core/skills/diagnosing-bugs/`
- `core/skills/domain-modeling/`
- `core/skills/grilling/`
- `core/skills/pr/`
- `core/skills/tdd/`
- `core/skills/writing-for-agents/`

Derived templates (attribution comment at the top of each file):

- `core/docs-templates/domain.md`, `core/docs-templates/issue-tracker.md`, `core/docs-templates/triage-labels.md`

Every other file under `core/`, `packs/`, `repo-types/`, `prompts/` and `scripts/` had no upstream
match with ratio ≥ 0.6 and is kit-authored (MIT © e-timologisi).
