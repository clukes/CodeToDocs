<!-- Template: Technical Documentation -->
<!-- Audience: Engineers and developers -->
<!-- Instructions: Replace placeholder text with generated content based on source code analysis -->

# {component} — Technical Documentation

## Purpose

Describe what this component does, its role in the larger system, and the core problem it solves. Include the component's primary responsibilities and boundaries.

## System Context

Describe where this component fits in the overall system:
- **Upstream services/triggers**: What invokes or sends data to this component (HTTP requests, queue messages, cron, etc.)
- **Downstream services/outputs**: What this component calls, publishes, or writes to
- **Data ownership**: What data/state this component owns vs. reads from other services
- **End-to-end flows**: List **each** business process this component participates in and its role in each. A single service often spans multiple flows (e.g., "Step 3 of order fulfillment: validates inventory" AND "Step 1 of returns processing: checks eligibility"). Document all of them.

Include a simple flow or sequence description per flow showing how this component connects to its neighbors.

## Architecture

Provide a high-level overview of the component's design. Cover:
- Key design patterns used (e.g., MVC, event-driven, layered)
- Data flow through the component
- Directory/module structure and organization
- Important architectural decisions and their rationale

## Setup / Installation

List prerequisites and step-by-step instructions to set up the component for development:
- Required tools and versions
- Installation commands
- Environment setup
- Initial configuration steps

## Running

Explain how to run, build, test, and deploy the component:
- Development mode commands
- Build/compile steps
- Test execution
- Deployment procedures

## Configuration

Document all configuration options:
- Configuration files and their locations
- Environment variables
- Default values and overrides
- Required vs. optional settings

## Edge Cases

Document known limitations and boundary conditions:
- Error scenarios and how they are handled
- Performance limitations or constraints
- Known issues or workarounds
- Input validation boundaries

## Dependencies

List all dependencies:
- Internal dependencies (other components/services in the system) — note the communication protocol (HTTP, gRPC, queue, database, etc.)
- External dependencies (third-party packages) with version constraints
- Infrastructure dependencies (databases, message brokers, caches, etc.)
- System-level requirements

## Key APIs

List the public interface of this component:
- Exported functions and their signatures
- Classes and their public methods
- HTTP endpoints (if applicable) — include method, path, request/response schemas
- Event hooks or callbacks
- Events published and consumed (topic/queue names, payload schemas)
- Include parameter types, return types, and brief descriptions
