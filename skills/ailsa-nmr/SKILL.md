---
name: ailsa-nmr
description: Use the locally installed AILSA toolkit for NMR-assisted organic structure elucidation, 13C dereplication, candidate shift prediction, or checking AILSA readiness. Applies to Bruker spectra, supported JCAMP-DX data, and explicit shift lists; full CASE needs connectivity evidence and a molecular formula.
---

# AILSA for Codex

Drive the local Python CLI directly. No Claude account, Claude agent-team flag, or separate model API key is needed for this integration. This is a Codex adaptation of AILSA's workflow, not a reproduction of its Claude benchmark.

## Locate the runtime

Install this companion skill alongside `reaction-nmr-review`. Follow the [runtime setup guide](https://github.com/RainWatcher2077/reaction-nmr-review/blob/main/docs/ailsa-runtime.md) if AILSA is missing. The skill can also be used on its own for AILSA workflows.

Use an existing verified AILSA wrapper when the user or project provides one. Otherwise invoke this skill's [launcher](scripts/ailsa) by absolute path. It uses the AILSA checkout in `AILSA_HOME` (default `~/.local/share/reaction-nmr-review/ailsa`), optionally the verified LSD binary directory in `LSD_BIN_DIR`, and optionally the SQLite file in `LUCY_DATABASE`. Set overrides to absolute paths for use across data directories. The runtime guide pins a known upstream baseline. Check the installed commands with `--help` because upstream interfaces may change.

## Choose the requested workflow

- **Status / readiness:** run `--version`, `lsd check`, `database info`, and `predict c13 'CCO' --format json`. Check statistical-detection capability separately with `detect hybridisation 130.5 --format json` and inspect schema, `has_data`, coverage and warnings, not exit status alone. A database can support prediction/ranking/dereplication while lacking usable statistical priors. Report NUS separately with `nus check` when relevant.
- **Predict 13C from SMILES:** run `predict c13 '<SMILES>' --format json`; report atom indices, shifts, confidence and missing predictions. Keep observed and predicted shifts distinct. HOSE generation uses molecules without explicit hydrogens; do not call RDKit `AddHs()`.
- **Dereplicate a known compound:** use `dereplicate c13 --help` to confirm the accepted input. The documented baseline CLI takes a Bruker spectrum and formula; a shift list alone requires the supported Python API. Present database hits as candidates with scores and coverage. A database match is not proof of identity. The reference database mixes predicted COCONUT shifts with experimental NMRShiftDB shifts.
- **Full CASE / unknown structure:** read [references/case-codex.md](references/case-codex.md), then follow the scientific references routed there. Full CASE begins from spectra and does not perform compound-database dereplication. The reference database remains appropriate for statistical priors and candidate shift prediction.

Resolve the dataset and formula from the user's message or a formula-only sidecar; ask only for missing information that cannot be inferred reliably. Preserve raw spectra. Write generated work in a new analysis directory without overwriting an earlier run. For images/PDFs or incomplete peak lists, describe what evidence is available and what is missing; do not imply that a raw-data CASE pipeline has run.

## Statistical capability and restricted CASE

The official Figshare v3 database has schema 3 and supports prediction, ranking and dereplication. Check the actual statistical-detection response. Report **restricted CASE, statistical priors unavailable** if the installed database lacks the required detection data. Do not invent missing fields, backfill default probabilities, force a schema migration, or rebuild the database merely to make readiness look successful.

When the required detection schema/data is unavailable or a detection result says `has_data: false`, disable database-derived hybridisation, neighbour, HHB and ring priors. Missing data is not frequency zero, a forbidden bond, or chemical evidence. Continue evidence-driven CASE using formula/DBE, DEPT, HSQC, HMBC, COSY and symmetry when those data are adequate; retain independent constraint reviews, multiplicity coverage and identity gates. Record the restricted mode in both progress and final reports. Real shift prediction and candidate ranking may continue against the installed database.

## Results and limits

Return links to the report and relevant spectra/constraint/candidate artifacts. State unresolved constraints, missing experiments, prediction coverage, candidate ambiguity, and whether the result is provisional. Constitution and stereochemistry are separate claims; do not infer stereochemical validation from this pipeline. Published AILSA performance measured in Claude does not establish Codex accuracy.
