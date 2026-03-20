# Contributing to Agent-Cite

## Adding Citation Patterns

Edit `templates/evidence-protocol.yaml` to add new citation formats:

```yaml
citation_patterns:
  - "[source: {path}:{line}]"
  - "[ref: {identifier}]"      # your custom format
```

## Adding a CLI Adapter

1. Create a directory in `adapters/<your-cli>/`
2. Wrap the prompts from `prompts/` in your CLI's native format
3. Update `install.sh` to detect and install your adapter

## Modifying Violation Types

Violation types are defined in `references/violation-types.md` and enforced by the `citation-scanner` agent. To add a new type:

1. Define it in `references/violation-types.md`
2. Add detection logic to `.claude/agents/citation-scanner.md`
3. Add fix logic to `.claude/agents/citation-fixer.md`
4. Update the evidence-audit skill to include the new type
5. Update `references/evidence-protocol-spec.md`

## Extending the Report

The evidence-report skill produces project-wide metrics. To add new metrics:

1. Define the metric in `.claude/skills/evidence-report/SKILL.md`
2. Add it to the report template
3. Update `templates/evidence-protocol.yaml` if thresholds are configurable
