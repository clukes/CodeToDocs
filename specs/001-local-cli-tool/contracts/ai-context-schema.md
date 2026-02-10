# Contract: AI Context YAML Schema

**Location**: `.codetodocs/templates/ai_context.yaml` (template)  
**Output**: `{output_dir}/ai/{component}.yaml` (generated)

## Why YAML over JSON

- ~40-60% fewer tokens (no quoted keys, no commas, no braces)
- Supports inline comments for additional context
- Agents parse YAML equally well as JSON
- Aligns with the config format (`.codetodocs/config.yaml`)

## Schema Definition

```yaml
_codetodocs:
  component: "<component name>"
  generated: "<ISO 8601 timestamp>"
  schema_version: "2.0"

component:
  name: "<component name>"
  purpose: "<1-3 sentence description>"
  languages: [<primary languages>]
  entry_points: [<main entry file paths>]

integration:
  upstream:
    - service: "<service name>"
      protocol: "HTTP | gRPC | queue | event | database"
      description: "<what this component receives>"
  downstream:
    - service: "<service name>"
      protocol: "HTTP | gRPC | queue | event | database"
      description: "<what this component sends>"
  events_published:
    - "<topic>: <PayloadType> — <when and why>"
  events_consumed:
    - "<topic>: <PayloadType> — <what happens on receipt>"
  data_ownership: [<entities this component owns>]
  flows:
    - "<flow-name>: <role> (step N of M)"

modules:
  - path: "<relative directory path>"
    purpose: "<what this module does>"
    exports: [<key public symbols>]

api:
  functions:
    - name: "<function name>"
      signature: "<full signature in source language>"
      description: "<what it does>"
  classes:
    - name: "<class name>"
      description: "<class purpose>"
      methods:
        - "<methodName(args) -> Return — what it does>"

types:
  - name: "<type name>"
    definition: "<type definition in source language>"

configuration:
  files: [<config file paths>]
  env_vars:
    - "<VAR_NAME>: <type>, <required|optional>, <default> — <what it controls>"

dependencies:
  internal: [<component names>]
  external:
    - "<package-name> <version> — <why it is used>"
```

## Design Principles

- **Compact one-liners** for methods, events, env vars, and dependencies — avoid nested objects where a string suffices
- **No metrics section** — LOC counts and file counts don't help agents understand code
- **No parameters/returns objects** — the `signature` field already encodes this information
- **5-20 modules max** — logical groupings, not per-file entries
- **Under 150 lines target** — for a typical component

## Field Constraints

| Field | Required | Notes |
|-------|----------|-------|
| `_codetodocs` | Yes | Metadata block. `schema_version` is `"2.0"`. |
| `component` | Yes | All sub-fields required. |
| `integration` | No | Omit entirely for standalone tools with no service dependencies. |
| `modules` | Yes | At least one module. Use repo root as single module for flat projects. |
| `api.functions` | No | Empty array if no public functions. |
| `api.classes` | No | Empty array if no classes. |
| `types` | No | Empty array if no notable types. |
| `configuration` | No | Omit if no user-facing config. |
| `dependencies` | Yes | Both `internal` and `external` required (may be empty). |

## Versioning

- `schema_version` follows semver: MAJOR for breaking changes, MINOR for additive fields
- Consumers should check `schema_version` and handle unknown fields gracefully
- Version `2.0` (YAML format) replaces version `1.0` (JSON format)
