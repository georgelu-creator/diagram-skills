# Data flow

## Use when

Show where data originates, how it is transported and transformed, where it is stored, who consumes it, and which feedback signals return. Avoid quantitative values that belong in a chart.

## Input fields

- producers and source formats
- ingestion protocols and cadence
- validation, privacy, and schema contracts
- transformations and enrichment
- streaming and batch stores
- model/service consumers
- retention, lineage, and feedback

## Fixed layout

Use `LR`: sources → ingestion → quality → compute/store → model/service → experience. Keep stream and batch paths parallel. Use groups for sources, ingestion, compute/storage, and serving. Mark event delivery `async`.

## Visual rules

Use cylinders only for durable stores, not every data-bearing component. Edge labels should name the artifact or contract (`events`, `features`, `context`). Use `spectrum` or `blueprint`.

## Example prompt

```text
Create a data-flow diagram for a real-time recommendation platform. Include app events, CDC/API ingestion, schema and PII checks, streaming features, lakehouse history, model inference, recommendation API, and outcome feedback. Keep stream and batch paths visually parallel, Chinese-first with English technical subtitles, spectrum theme, strict DiagramSpec output.
```
