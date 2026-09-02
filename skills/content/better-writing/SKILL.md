---
name: better-writing
description: "Draft, rewrite, line edit, review, humanise, adapt, or synthesise natural-language prose from drafts, notes, PDFs, scans, Source Packs, or large document collections while preserving facts, provenance, exact literals, uncertainty, project terminology, and voice. Use when the requested result is polished English or Russian prose. Do not use for code-only work, standalone fact-checking, pure data analysis, documentation lookup, or authorship classification."
metadata:
  version: "2.7.0"
---

# Better writing

Make prose clear, faithful, specific, well-shaped, and recognisably owned by its writer.

Core instructions are portable. Optional diagnostics and package checks require Python 3.10+.

## Route the request

Choose the job before touching the prose.

| Job | Use it when | Primary references |
|---|---|---|
| Draft | The user needs new prose from notes, evidence, or a brief | `references/operating-contract.md`, `references/genre-modes.md` |
| Rewrite | A draft exists and may be restructured or recast | `references/edit-decision-protocol.md`, `references/revision-pass-stack.md`, `references/quality-gates.md` |
| Line edit | The shape works; sentences need clarity, rhythm, or economy | `references/edit-decision-protocol.md`, `references/foundations.md`, `references/voice-and-rhythm.md` |
| Review | The user wants diagnosis or comments, not a rewritten artefact | `references/quality-gates.md` |
| Humanise | The prose feels generic, machine-smooth, formulaic, or unlike its author | `references/ai-isms-and-humanisation.md`, `references/genericity-and-stiffness.md`; add `references/formulaic-language-catalogue.md` for explicit avoidance or dense formulae |
| Adapt | The substance should stay while audience, genre, channel, length, or voice changes | `references/genre-modes.md`, `references/style-bundles.md` |
| Synthesis | PDFs, scans, or many files must become a source-backed article, report, chapter, or summary | `references/pdf-and-large-corpora.md`, `references/operating-contract.md`, `references/genre-modes.md` |
| Project-bound | Repeated work must follow stable audiences, terminology, approved facts, voice, privacy, or delivery rules | `references/project-profiles.md`, then the job-specific references |

Mixed requests can use more than one job. Keep scope clean: if a request combines a code fix with an error-message rewrite, this skill may revise the user-facing words but does not edit the surrounding source, syntax, or code behaviour. Never rename, rewrite, or reinterpret code constructs to satisfy a style or diction rule. In mixed documentation, edit only the natural-language prose and preserve machine-readable material exactly.

For an explicit request to remove, replace, limit, or standardise em dashes, semicolons, or colons, read `references/punctuation-and-sentence-flow.md`. Load it conditionally; ordinary line editing and humanisation do not imply a punctuation ban.

For Russian source or target prose, read `references/russian-profile.md`. Apply Russian grammar, typography, register, and uncertainty rules instead of importing English punctuation or anti-formula heuristics. The English `scan_aiisms.py` corpus is not a Russian-language detector.

For PDFs, scans, OCR output, tables used as evidence, or a large collection of source files, read `references/pdf-and-large-corpora.md` before drafting. Inventory the corpus, preserve source and page locators, validate extraction against rendered pages, and work in bounded semantic chunks. Use specialised PDF tooling for extraction, OCR, rendering, or PDF creation; this skill owns the editorial synthesis. Use a data-analysis workflow instead when calculation, aggregation, modelling, or charting is the primary result.

When the user supplies a project profile, asks for house-style continuity, or expects reusable audiences, terminology, approved facts, voice, output, or privacy rules, read `references/project-profiles.md`. Validate a file-backed profile before relying on it. A profile is durable context, not superior authority: the current request and supplied evidence override it.

For repeatable, incremental, multi-source, or handoff-ready work, read `references/source-packs-and-claim-audits.md`. Use its Source Pack layout to keep raw material, extraction, chunks, manifests, claims, issues, and deliverables separate. Audit material claims before calling a source-backed deliverable complete.

Use another workflow for code-only implementation, standalone fact-checking, or authorship classification. This skill may rewrite prose produced alongside those tasks, but it does not perform them.

## Set intervention and delivery

Use the narrowest intervention that solves the reader-facing problem:

- **Minimal:** correct mechanics and local ambiguity; preserve wording, order, and cadence wherever they already work.
- **Standard:** improve paragraph logic, sentence clarity, and consistency without recasting the piece. Use this default for ordinary rewrite requests.
- **Deep:** restructure, recast, or change genre when the user requests it or the current shape cannot achieve the stated outcome.

Respect an explicit output mode. **Clean** returns only the finished artefact; **annotated** adds a short change log; **review-only** diagnoses without producing a replacement; **side-by-side** pairs source units with revisions. When the user requests a rewrite but no mode, default to clean output. Never silently turn review-only work into a rewrite.

## Operating workflow

### 1. Establish the writing contract

Infer what the supplied context already settles. Identify:

- reader, deliverable, and desired outcome
- source material and factual authority
- source coverage, provenance, extraction quality, and unresolved files when the material is a PDF or corpus
- required length, format, locale, house style, and deadline
- whether the user wants a draft, rewrite, review, humanisation pass, or adaptation
- intervention depth and output mode

If a project profile is supplied or explicitly requested, load only the fields relevant to the job. Validate it with `scripts/validate_project_profile.py`, record any conflicting term or rule, and never let it silently override the current request, source evidence, or approval boundary.

For an existing draft, build a preservation ledger before editing. Protect facts, numbers, dates, names, quotations, citations, commands, paths, API identifiers, legal or technical terms, explicit uncertainty, and lines that carry the writer's voice.

For a PDF or multi-file job, build a source manifest and claim ledger before writing. For repeatable or incremental work, store them in a Source Pack. Do not treat OCR output as authoritative until representative pages and all suspicious regions have been compared with the rendered source. Keep raw extraction, normalised text, summaries, claims, issues, and final prose as separate layers.

Ask only when a missing choice would materially change the result. Never invent evidence, experience, approval, customer language, or confidence the source does not contain.

Do not treat unsupported praise or marketing posture as a factual invariant. If removing vague claims leaves too little to write, surface the evidence gap or ask for the missing mechanism instead of rearranging the same abstractions.

Read `references/operating-contract.md` when the source is sensitive, highly constrained, collaborative, or likely to lose important detail.

**Complete when:** the reader, outcome, edit freedom, source authority, and protected material are known or explicitly marked unknown.

### 2. Diagnose before rewriting

For every rewrite or line edit of an existing draft, read `references/edit-decision-protocol.md`. Start from **keep**, then consider a local **repair**, and use a **recast** only when repair cannot solve the named reader-facing problem. A substantive candidate replaces the source only if it fixes that problem without an unrequested loss of meaning, specificity, evidence, voice, or useful cadence.

Name the failure at the right scale:

- whole-piece: wrong genre, audience, order, thesis, or scope
- section: missing step, evidence, turn, or decision
- paragraph: mixed jobs, buried point, repetition, weak transition
- sentence: unclear actor, abstraction, drag, monotony, or false emphasis
- surface: grammar, spelling, punctuation, formatting, or house style

Preserve what already works. A good edit is not a demonstration that every sentence can be changed.

**Complete when:** the smallest responsible layer and the draft's strongest material are both identified.

### 3. Fix shape before style

Choose the page shape in `references/genre-modes.md`. Give each section and paragraph one job. Put the main point where that genre expects it. Order evidence so the reader never has to guess why it is present.

Read `references/natural-structure-and-digestibility.md` when the request calls for a substantial structural recast, a more natural flow, or repair of dense, wall-of-text, or over-chunked prose. Use its worked transformations to split at changes of job, not at arbitrary lengths.

For review-only work, stop short of rewriting: report the diagnosis, cite exact passages, rank issues by reader impact, and offer a rewrite only as a clearly labelled example.

**Complete when:** the opening establishes the right contract, the middle advances it without echoing itself, and the ending performs the genre's real closing task.

### 4. Run two clarity passes

Use `references/revision-pass-stack.md`.

1. **Paragraph pass:** one job per paragraph, visible logic, no repeated claim, evidence beside the claim it supports.
2. **Sentence pass:** clear actor and action, concrete nouns and verbs, related words together, honest qualifications, informative emphasis.

Adjudicate each substantive candidate against the source, not against an imagined ideal sentence. If a smaller repair works, prefer it. If the candidate is only different, restore the source.

Do not compress every sentence. Restore connective tissue when the page starts to read like chopped notes. When a long passage needs reshaping, choose paragraphs, lists, headings, or tables from the information's real shape; formatting cannot replace reasoning.

When punctuation is the edit target, classify the relation before changing the mark. A colon fulfils a promise, a semicolon balances close independent clauses, and a conjunction or subordinate clause should name logic that punctuation would otherwise leave implicit. Protect literal punctuation in code, URLs, times, ratios, quotations, labels, and configuration.

**Complete when:** a reader can follow the argument or procedure on the first read without losing the draft's meaning or cadence.

### 5. Restore voice and specificity

Use `references/voice-and-rhythm.md` for stance, cadence, sentence movement, and read-aloud repair. Use `references/style-bundles.md` to calibrate a voice from samples or declared traits without imitating a living writer's signature.

Human signal comes from judgement, selection, detail, and position—not fake typos, random slang, decorative swearing, invented anecdotes, or forced informality.

**Complete when:** the prose has a discernible point of view, sentence movement suits the thought, and the writer's high-signal details remain intact.

### 6. Humanise only when needed

For ordinary drafting and editing, only confirm that the revision did not introduce assistant residue, empty ceremony, unsupported benefit language, or a formula that hides the actor, mechanism, evidence, or consequence. Do not turn this final check into a phrase hunt.

Run the full pass and read `references/ai-isms-and-humanisation.md` plus `references/formulaic-language-catalogue.md` only when the user asks to remove AI-like words or phrases, ban formulaic diction, make prose less robotic, or when the diagnosed problem is generic authority, excessive symmetry, service tone, or repeated rhetorical frames.

Apply the catalogue's action levels:

- remove wrappers and empty stage directions
- rewrite canned semantic frames from supported meaning, even when they occur once
- review ordinary words and structural signals in context or clusters
- protect literal, technical, legal, measured, quoted, and writer-owned uses

Never perform a synonym swap to satisfy an avoidance rule. This applies across the catalogue, not only to individual watch words. `Bridge the gap` does not become `close the divide`; identify what is missing and what action changes it. `Marks a significant shift` does not become `signals a major transformation`; state the before and after. `Plays a critical role`, `unlocks value`, and `research shows` likewise need a supported action, result, or source. If the source lacks the necessary substance, delete, narrow, or query the claim.

If a substantial English-language draft exists as a file and humanisation is in scope, run:

```bash
python3 scripts/scan_aiisms.py path/to/draft.md
```

Use `--format json` for automation and `--gate` only as a conservative multi-pattern cluster gate. A normal scan already surfaces single remove-, rewrite-, and review-labelled matches. Judge those matches against their exceptions; the scanner cannot determine whether a use is exact, suitable for its genre, or evidence of authorship. Treat an em dash, polished sentence, or ordinary word as context—not proof.

Rewrite the thought, not just the flagged token. Preserve dialect, accessibility choices, second-language voice, quoted material, literal terminology, and intentional rhetoric.

**Complete when:** remove and rewrite rules are resolved or deliberately retained, review-only clusters have been judged in context, and the revision reads better by ordinary editorial standards—not merely less detectable.

### 7. Calibrate the deliverable

Apply the target genre, audience, locale, and house style. Check headings, lists, calls to action, examples, and ending shape. Keep formatting proportional to the material; not every paragraph wants a heading and not every thought wants a bullet.

**Complete when:** the artefact looks and sounds native to its destination without losing factual or personal identity.

### 8. Pass the quality gates and stop

Run the gates in `references/quality-gates.md`:

1. fidelity
2. logic and evidence
3. clarity and cadence
4. voice and humanisation
5. genre and mechanics
6. final proof

Compare the revision against the preservation ledger. Re-run deterministic diagnostics after the last substantive edit, not before it. Stop when every remaining change is merely different, not better.

Inspect the final diff as a set of decisions. Every substantive change must have a precise internal reason and must survive the comparative-dominance test in `references/edit-decision-protocol.md`; rollback changes made only for polish, metric improvement, or stylistic conformity.

For a large local collection, create a deterministic manifest before synthesis:

```bash
python3 scripts/build_corpus_manifest.py path/to/sources --output corpus-manifest.json
```

Use `--chunks-dir prepared-chunks` for bounded chunks of readable text and Markdown sources. The helper inventories PDFs but does not extract or OCR them. Reconcile the final deliverable against the manifest and source ledger: every file must be ready, duplicate, skipped, or failed, and every material claim must have a source locator or be labelled as editorial synthesis.

When a project profile is part of the job, validate it before applying its defaults:

```bash
python3 scripts/validate_project_profile.py path/to/project-profile.json --gate
```

When a claim ledger exists, audit it after the last substantive edit:

```bash
python3 scripts/check_claim_coverage.py path/to/claim-ledger.jsonl --gate
```

Add `--strict-confidence` when every used material claim must have medium or high confidence. The audit rejects unsupported used claims, undisclosed conflicts, unresolved or excluded claims used in prose, and unlabelled editorial synthesis. It cannot judge whether a supported paraphrase is semantically faithful, so retain the manual logic-and-evidence gate.

For a file-backed, fidelity-sensitive edit, run:

```bash
python3 scripts/check_preservation.py path/to/source.md path/to/revision.md --gate
```

The checker verifies exact code, inline literals, quotations, URLs, paths, numeric tokens, and English or Russian uncertainty markers. Treat added numbers as warnings unless `--strict-additions` is justified. It cannot prove that names, causal meaning, or paraphrased claims are preserved, so complete the semantic fidelity gate manually.

**Complete when:** the deliverable passes every applicable gate, protected material matches the source, and no known critical issue remains.

## Output contract

Follow the selected output mode. In clean mode, lead with the artefact and omit process narration. In annotated mode, put the artefact first and keep the change log brief. In review-only mode, rank findings by reader impact and do not append a silent replacement. In side-by-side mode, align source and revision at the smallest useful unit without splitting every sentence mechanically.

When useful and allowed by the mode, report:

- important structural choices
- protected facts or literals
- unresolved factual questions
- deliberate exceptions to a diagnostic signal

Do not claim a passage was AI-written. Do not turn stylistic preference into an accusation.

## Quick reference

| Need | Read or run |
|---|---|
| Brief, preservation ledger, and edit freedom | `references/operating-contract.md` |
| Decide whether a proposed edit is genuinely better than the source | `references/edit-decision-protocol.md` |
| Exact revision order and loopbacks | `references/revision-pass-stack.md` |
| Natural structure, paragraph architecture, and long-prose digestibility | `references/natural-structure-and-digestibility.md` |
| Grammar, clarity, and modern usage baseline | `references/foundations.md` |
| Cadence, stance, and voice repair | `references/voice-and-rhythm.md` |
| Em-dash replacement, semicolon and colon judgement, and sentence-flow repair | `references/punctuation-and-sentence-flow.md` |
| Generic, corporate, ceremonial, or inflated prose | `references/genericity-and-stiffness.md` |
| AI-like patterns, humanisation, false positives, and scanner use | `references/ai-isms-and-humanisation.md` |
| Contextual avoid rules, phrase families, natural rewrites, and protected uses | `references/formulaic-language-catalogue.md` |
| Docs, PRs, specs, memos, reports, essays, email, UI, and copy | `references/genre-modes.md` |
| Personal voice sheets and style calibration | `references/style-bundles.md` |
| Russian grammar, typography, register, and Russian-language humanisation | `references/russian-profile.md` |
| PDF extraction quality, OCR, page provenance, and large-corpus synthesis | `references/pdf-and-large-corpora.md` |
| Reusable audience, terminology, approved facts, voice, output, and privacy rules | `references/project-profiles.md` |
| Incremental source packages, claim ledgers, provenance, conflicts, and claim coverage | `references/source-packs-and-claim-audits.md` |
| Acceptance criteria and final proof | `references/quality-gates.md` |
| Research basis and limits | `references/research-notes.md` |
| Failure recovery | `references/gotchas.md` |
| Exact-literal and uncertainty preservation | `scripts/check_preservation.py` |
| Corpus inventory, SHA-256 deduplication, and bounded text chunks | `scripts/build_corpus_manifest.py` |
| Project-profile schema and authority checks | `scripts/validate_project_profile.py` |
| Source-backed claim coverage and conflict checks | `scripts/check_claim_coverage.py` |

## Templates

- `templates/rewrite-worksheet.md` records the brief, preservation ledger, pass results, and final gates.
- `templates/personal-style-sheet.md` captures a writer's real habits from samples before revision smooths them away.
- `templates/project-profile.json` provides a reusable, dependency-free project context.
- `templates/source-pack.json` defines the Source Pack manifest.
- `templates/claim-ledger.jsonl` shows supported, conflicted, unresolved, excluded, and editorial-synthesis claims.

## Non-negotiables

1. Never improve style by changing the facts.
2. Never convert uncertainty into confidence without evidence.
3. Never invent personal experience, quotations, citations, proof, or customer language.
4. Never mimic a named writer's signature; translate the request into high-level traits.
5. Never use a phrase list or detector score as proof of authorship.
6. Never sand away dialect, accessibility, or second-language identity to make prose look statistically “human.”
7. Never satisfy a formulaic-language rule through synonym substitution alone.
8. Never keep editing after the applicable gates pass and the remaining options are taste-equivalent.
9. Never alter code, identifiers, selectors, configuration keys, or other machine-readable constructs; revise only the natural-language prose in scope.
10. Never turn unreadable OCR, missing pages, failed files, or an unverified table into a confident claim.
11. Never imply full-corpus coverage without accounting for every supplied file and disclosing skipped or failed sources.
12. Never let a project profile override the current request, supplied evidence, explicit approval, or a safety boundary.
13. Never claim complete source support without auditing every used material claim or explicitly disclosing that no claim ledger was maintained.
14. Never keep a substantive change that cannot be tied to a precise reader-facing problem and shown to outperform keeping the source.
