# Infrastructure And Platform Knowledge

## Scope

Infrastructure, cloud architecture, platform engineering, identity, self-hosting, homelabs, reliability, and operational automation.

## Default position

Prefer simple, auditable, low-ops platforms with clear ownership boundaries over clever shared systems that only a small number of people can maintain.

## Heuristics

- isolate blast radius before optimizing elegance
- standardize identity and access early
- prefer boring deployment paths over fragile customization
- treat observability, backups, and rollback as part of the design, not follow-up work
- document the operating model, not just the topology

## Preferred patterns

- infrastructure as code for repeatable environments
- environment isolation with clear state boundaries
- Git-based change control for infra and platform configuration
- standard platform templates or golden paths for repeatable delivery
- explicit service ownership and operational handoff notes

## Anti-patterns

- one giant Terraform state for unrelated systems
- manually configured production infrastructure with no audit trail
- hidden dependencies between environments
- platform teams acting as ticket-taking bottlenecks instead of productized enablers
- identity managed separately in every application without lifecycle controls

## Questions to answer with your own preferences

- which cloud and self-hosted tradeoffs do you prefer
- when do you allow Kubernetes versus simpler deployment targets
- which identity stack is your default
- what backup and disaster-recovery standards are non-negotiable

## Example Q&A

### Question

How should platform teams reduce friction without becoming a gatekeeper team?

### Preferred answer

Build paved roads rather than bespoke services. Provide a small number of default deployment patterns, codified IAM models, standard observability, and self-service documentation. Measure success by how often teams can ship without opening a platform ticket.
