# Agent as Code (AaC)
====================================

Welcome to the Agent as Code (AaC) framework documentation. This guide will help you understand and use the framework to create, build, and deploy AI agents using declarative configuration.

## What is Agent as Code?

Agent as Code (AaC) is a declarative configuration system for AI agents, inspired by Docker and Infrastructure as Code (IaC). It enables developers to define AI agents using simple, version-controlled configuration files.

**Think of it as "Docker for AI agents"** - just like Dockerfile makes it easy to define and build containers, Agentfile makes it easy to define and build AI agents.

## Core Philosophy

- **Declarative**: Define what the agent should do, not how to do it
- **Version Controlled**: Track agent configurations in Git
- **Reusable**: Share and reuse agent configurations
- **Simple**: Easy to understand and modify
- **Portable**: Work across different environments and clouds

## Quick Start

```bash
# Install the framework
pip install agent-as-code

# Create your first agent
agent init my-first-agent

# Build the agent
agent build -t my-first-agent:latest .

# Run the agent
agent run my-first-agent:latest
```

## Documentation Sections

### Core Pages

1. **[Home](https://agent-as-code.myagentregistry.com/)** — Overview and latest updates
2. **[Getting Started](https://agent-as-code.myagentregistry.com/getting-started)** — Prerequisites, installation, quick start, first agent, and deployment options
3. **[Documentation](https://agent-as-code.myagentregistry.com/documentation)** — Full technical documentation hub

### Component Guides

4. **[Agentfile](https://agent-as-code.myagentregistry.com/documentation#agentfile)** — Write and structure your Agentfile
5. **[Parser](https://agent-as-code.myagentregistry.com/documentation#parser)** — Validation and parsing rules
6. **[Builder](https://agent-as-code.myagentregistry.com/documentation#builder)** — Building and packaging agents
7. **[Runtime](https://agent-as-code.myagentregistry.com/documentation#runtime)** — Execution environments

### CLI and Registry

8. **[CLI Reference](https://agent-as-code.myagentregistry.com/cli)** — Commands, options, and workflows
9. **[Registry Guide](https://agent-as-code.myagentregistry.com/registry)** — Remote registry, PAT, versioning, and security

### Examples

10. **[Examples](https://agent-as-code.myagentregistry.com/examples)** — Real-world examples and use cases

## Framework Goals

### Primary Objectives

1. **Simplify AI Agent Development**
   - Reduce complexity of agent creation
   - Provide standardized patterns
   - Enable rapid prototyping

2. **Enable Declarative Configuration**
   - Version-controlled agent definitions
   - Infrastructure as Code principles
   - Reproducible deployments

3. **Facilitate Agent Sharing**
   - Centralized registry for agents
   - Easy distribution and discovery
   - Community-driven development

4. **Support Multiple Runtimes**
   - Docker containerization
   - Kubernetes deployment
   - Cloud-native architectures

### Key Benefits

- **Developer Experience**: Familiar Docker-like commands
- **Portability**: Run agents anywhere
- **Scalability**: Cloud-native micro-service architecture
- **Collaboration**: Share agents through registry
- **Automation**: CI/CD pipeline integration

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agentfile     │───▶│   AaC Parser    │───▶│  Agent Builder  │
│  (Config)       │    │  (Validation)   │    │  (Packaging)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Registry      │◀───│   Agent CLI     │◀───│  Agent Runtime  │
│  (Storage)      │    │  (Commands)     │    │  (Execution)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Getting Help

- **Documentation**: https://agent-as-code.myagentregistry.com/documentation
- **Getting Started**: https://agent-as-code.myagentregistry.com/getting-started
- **Examples**: https://agent-as-code.myagentregistry.com/examples
- **CLI Help**: Run `agent --help` for command reference

## Next Steps

1. Read **[Getting Started](https://agent-as-code.myagentregistry.com/getting-started)**
2. Explore **[Examples](https://agent-as-code.myagentregistry.com/examples)**
3. Review **[CLI Reference](https://agent-as-code.myagentregistry.com/cli#overview)**
4. Create your first agent with `agent init`

---

**Ready to build your first AI agent?** Start with **[Getting Started](https://agent-as-code.myagentregistry.com/getting-started#quick-start)**!
