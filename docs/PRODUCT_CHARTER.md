# Product charter — Medallio Economic Intelligence

## Product promise
Help the founder understand how Peru's economy and market conditions may affect Medallio, choose a response, and later verify whether the response created value.

This is the founder's personal intelligence cockpit and research instrument. It supports Medallio Company OS; it does not replace it.

## Primary user and job
Primary user: Diego, founder of Medallio.

Before a strategic or operating review, answer:
1. What changed in the external environment?
2. Which evidence is current and trustworthy?
3. Which parts of Medallio's business could be exposed or advantaged?
4. What decision or experiment is worth considering?
5. What happened after the decision, and what value can be verified?

## Product loop
Observe → interpret → decide → act → measure → learn.

- Observe public economic indicators and approved internal operating measures.
- Interpret each signal with source, freshness, quality, limitations, and confidence.
- Record the founder's choice, alternatives, rationale, and review date.
- Record actions with an owner, due date, and intended result.
- Measure outcomes against a baseline and counterfactual where feasible.
- Update assumptions and confidence with evidence.

## Boundaries
- Medallio Company OS remains the company strategy and governance source of truth.
- medallio-platform remains the product codebase for customer-facing multi-tenant software.
- This repo is the founder's personal intelligence and proving ground.
- bd_replica_crm remains a Cygnus/reference implementation, not a dependency.
- Power BI displays and explores certified marts; it is not the only home for business logic.
- Correlation is not causation. Recommendations are hypotheses until validated.

## What belongs here
Peru macroeconomic and market indicators; non-sensitive founder operating measures; scenarios and hypotheses; decision, action, outcome, and economic-value records; trust and freshness metadata; and sanitized views explicitly approved for collaboration.

## Success measures
Track from evidence, without inventing values:
- time from question to evidence-backed decision;
- share of material signals with provenance, freshness, and quality status;
- decision-to-outcome measurement coverage;
- verified economic value linked to decisions;
- founder reuse in monthly operating reviews;
- shareable artifacts that pass privacy and provenance review.

## First release
A read-only Peru and Medallio executive brief with source cards, latest values, comparable periods, explicit missingness, aggregate business context, and a decision log. No autonomous action execution.
