# System topology

## Use when

Explain runtime services, network or trust zones, dependencies, queues, storage, observability, redundancy, or failover. Use system architecture for conceptual responsibilities and product layers.

## Input fields

- clients and entry network
- regions, zones, clusters, or trust boundaries
- runtime services and replicas
- synchronous and asynchronous dependencies
- stores, queues, and caches
- telemetry and control planes
- failure and failover behavior

## Fixed layout

Use `LR`: clients/edge → service plane → data plane → operations. Keep synchronous and asynchronous paths distinct. Use groups for real zones or planes, not aesthetic columns. For multi-region systems, make each region a separate view if the overview becomes dense.

## Visual rules

Use `blueprint` by default. `external` marks boundaries, `agent` active orchestrators, `database` durable systems. Use `async` for queues/events and label cross-zone links. Do not imply redundancy unless supplied.

## Example prompt

```text
Create a system-topology diagram for a highly available AI API. Include clients, global gateway, Agent API, async workers, primary store, event bus, telemetry hub, and explicit sync/async paths. Group edge, service, data, and observability planes. Use blueprint theme, bilingual labels, VisualSpec JSON, strict validation.
```
