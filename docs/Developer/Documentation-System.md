# Documentation System Contract

## Purpose

This page defines how Binancial documentation should be structured, written, and improved. It is the operating contract for docs and the reference point for every documentation change.

The goal is to make Binancial documentation behave like one coherent product.

## What 10/10 Means

For Binancial, 10/10 docs means the full system is:

- accurate to the code and current package architecture
- easy to enter for a new user
- deep enough for serious integration and contributor work
- coherent across product pages, reference pages, and package READMEs
- grounded in real runnable workflows and real artefacts

## Canonical Source Rules

Binancial documentation should have one clear ownership model.

- [README.md](../../README.md) is the product home page and first-success entry point.
- [docs/README.md](../README.md) is the canonical public docs hub.
- `/docs` is the canonical source for public concepts, workflows, and API/reference pages.
- `/docs/Developer` is the canonical source for contributor and maintainer process docs.
- package `README`s under `/binancial` are orientation pages for module ownership and boundaries, not the main public reference.

Content should be authored once whenever possible. If the same explanation appears in multiple places, one page should be canonical and the others should route to it.

## Information Architecture

The docs should be organized into five top-level sections:

- `Overview`
- `Guides`
- `Reference`
- `Developer`
- `Packages`

### Section Responsibilities

- `Overview` explains what Binancial is, what it is not, and how the whole system fits together.
- `Guides` teach workflows and tasks from start to finish.
- `Reference` documents surfaces, conventions, arguments, outputs, and edge cases.
- `Developer` documents contribution, release, maintenance, and internal documentation rules.
- `Packages` explains module ownership, boundaries, entry points, and where to read next.

## Narrative Spine

Every major public page should reinforce the same core Binancial story:

1. Binancial wraps the Binance API into single-line commands for market data.
2. Raw trades and klines are fetched through the `data` module.
3. Raw trades are aggregated into custom klines through the `compute` module.
4. The `utils` module provides shared helpers for API initialization and data formatting.

If a page does not help a reader understand its place in that story, it should route clearly to the pages that do.

## Register And Writing Rules

All Binancial documentation should use the same register:

- precise
- technical
- concise
- accessible to an informed new user
- direct rather than academic

### Writing Rules

- Start with what the thing is and why a reader would use it.
- Prefer concrete behavior over abstract framing.
- Keep theory only where it directly improves practical understanding.
- Explain current surface area honestly; do not imply future behavior as present behavior.
- Prefer examples that show inputs, outputs, and artefacts.
- Do not use unexplained internal jargon.
- Do not duplicate large sections of content across pages.
- End pages with explicit reading routes or next steps when useful.

## Page Types And Required Blocks

Every page should fit one primary page type.

### Home Page

Purpose: product framing and first success.

Required blocks:

- what Binancial is
- what Binancial is not
- capability summary
- first successful workflow
- clear routes into the rest of the docs

### Docs Hub

Purpose: route readers by task and audience.

Required blocks:

- system overview
- reading order by user type
- explicit routes into guides, reference, developer docs, and package docs

### Guide

Purpose: teach a job or workflow from start to finish.

Required blocks:

- what this guide covers
- prerequisites
- current scope
- at least one concrete example
- expected artefacts or outputs
- related pages or next steps

### Reference

Purpose: document an interface or surface comprehensively and predictably.

Required blocks:

- short intro and scope
- conventions or naming rules
- structured entry documentation
- output columns or return behavior where relevant
- edge cases or caveats where relevant

### Developer Page

Purpose: guide contributors and maintainers.

Required blocks:

- page purpose
- required reading or prerequisites
- process or checklist
- failure cases or review notes where relevant
- linked related maintenance pages

### Package README

Purpose: orient readers inside a module without replacing canonical public docs.

Required blocks:

- what the package owns
- what it does not own
- key entry points
- major dependencies or adjacent modules
- link to canonical public docs

## Navigation And Cross-Link Rules

Navigation should reduce guesswork.

- The home page and docs hub must both provide reading paths by task.
- Large pages should be indexed near the top.
- Public workflow pages should link forward through the narrative spine.
- Package READMEs should link outward to canonical docs rather than trying to become their own mini-sites.
- Cross-links should prefer the next page a reader should open, not every vaguely related page.

## Terminology Rules

Use one terminology set across the whole docs system.

- Product name: `Binancial`
- Raw data endpoints: `data` module
- Computed aggregations: `compute` module
- Shared helpers: `utils` module
- Trade-built candles: `spot klines`

## How To Use This Page

Before rewriting any major docs slice:

- confirm the target page type
- confirm where the page sits in the narrative spine
- confirm whether the page is canonical or secondary

If a proposed docs change conflicts with this contract, update this page first or explicitly document the exception.
