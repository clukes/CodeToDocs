# Contract: AI Context JSON Schema

**Location**: `.codetodocs/templates/ai_context.json` (template)  
**Output**: `{output_dir}/ai/{component}.json` (generated)

## Schema Definition

```json
{
  "_codetodocs": {
    "component": "<string: component name>",
    "generated": "<string: ISO 8601 timestamp>",
    "schema_version": "1.0"
  },
  "component": {
    "name": "<string: component name>",
    "purpose": "<string: 1-3 sentence description of what this component does>",
    "languages": ["<string: primary language>"],
    "entry_points": ["<string: main entry file paths>"]
  },
  "modules": [
    {
      "name": "<string: module identifier>",
      "path": "<string: relative directory/file path>",
      "description": "<string: what this module does>",
      "role": "<string: 'core' | 'integration' | 'infrastructure'>"
    }
  ],
  "api": {
    "functions": [
      {
        "name": "<string: function name>",
        "module": "<string: parent module name>",
        "signature": "<string: full signature in source language>",
        "description": "<string: what it does>",
        "parameters": [
          {
            "name": "<string>",
            "type": "<string>",
            "optional": "<boolean>",
            "description": "<string>"
          }
        ],
        "returns": {
          "type": "<string>",
          "description": "<string>"
        }
      }
    ],
    "classes": [
      {
        "name": "<string: class name>",
        "module": "<string: parent module name>",
        "description": "<string: class purpose>",
        "methods": [
          {
            "name": "<string: method name>",
            "signature": "<string: full signature>",
            "description": "<string: what it does>"
          }
        ]
      }
    ]
  },
  "types": [
    {
      "name": "<string: type name>",
      "definition": "<string: type definition in source language syntax>",
      "description": "<string: what this type represents>"
    }
  ],
  "configuration": {
    "description": "<string: how configuration is provided>",
    "variables": [
      {
        "name": "<string: config key or env var>",
        "type": "<string: data type>",
        "required": "<boolean>",
        "default": "<any: default value if not required>",
        "description": "<string: what it controls>"
      }
    ]
  },
  "dependencies": {
    "internal": ["<string: internal component/package names>"],
    "external": [
      {
        "name": "<string: package name>",
        "version": "<string: version constraint>",
        "purpose": "<string: why it's used>"
      }
    ]
  },
  "metrics": {
    "files": "<number: total source files>",
    "lines_of_code": "<number: approximate LOC>",
    "public_api_surface": "<number: count of public functions/methods/classes>",
    "internal_dependencies": "<number: count of internal deps>",
    "external_dependencies": "<number: count of external deps>",
    "complexity_rating": "<string: 'low' | 'moderate' | 'high' | 'very_high'>"
  }
}
```

## Field Constraints

| Field | Required | Notes |
|-------|----------|-------|
| `_codetodocs` | Yes | Metadata block. `schema_version` starts at `"1.0"`. |
| `component` | Yes | All sub-fields required. |
| `modules` | Yes | At least one module. Use repo root as single module for flat projects. |
| `api.functions` | No | Empty array if no public functions. |
| `api.classes` | No | Empty array if no classes. |
| `types` | No | Empty array if no notable types. |
| `configuration` | No | Omit `variables` array if no config. |
| `dependencies` | Yes | Both `internal` and `external` arrays required (may be empty). |
| `metrics` | Yes | All fields required. `complexity_rating` is agent-assessed. |

## Versioning

- `schema_version` follows semver: MAJOR for breaking changes, MINOR for additive fields
- Consumers should check `schema_version` and handle unknown fields gracefully
