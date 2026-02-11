<!-- Template: Product Documentation -->
<!-- Audience: Product managers and stakeholders -->
<!-- Instructions: Replace placeholder text with generated content based on source code analysis -->

# {component} — Product Documentation

## Purpose

Describe what this component provides to users and the problem it solves. Focus on the user-facing value proposition, not internal implementation details.

## System Role

Explain this component's role in the overall product workflow in plain language:
- What triggers this component to act (e.g., "Runs when a new order is placed")
- What this component produces or enables for downstream steps
- Which user-visible processes this component is part of — list **all** of them, as a single service often participates in multiple business processes (e.g., order placement, returns, inventory sync)

## Features

List the capabilities this component offers. For each feature, briefly describe what users can do and why it matters.

- **Feature name** — What it does and the user benefit.

## Business Rules

Document validation rules, constraints, and policies enforced by the code. Include:

- Input validation and accepted value ranges
- Access control or authorization rules
- Rate limits, quotas, or usage constraints
- Data integrity rules and invariants

## User Impact

Describe how recent changes affect end users. Cover:

- New capabilities or changed behaviors
- Migration steps required (if any)
- Breaking changes and workarounds
- Deprecations and removal timelines

## Configuration / Policies

List user-facing configuration options, their defaults, and tunable behaviors. For each option, note:

- Option name and purpose
- Default value
- Accepted values or range
- Effect on component behavior
