# AIDevOS

Multi-agent system where AI agents (PM, Backend, Frontend, DevOps, QA, Security) collaborate to architect and deploy SaaS applications. Uses Durable Objects as modular microservices.

## What It Does

1. Accepts a product spec or business requirement
2. AI agents discuss and refine the architecture via debate/reflection cycles
3. Generates task breakdowns, architecture docs, and deployment configs
4. Intended to write, test, and deploy code iteratively via a CI/CD pipeline

## Agents

| Agent | Role |
|-------|------|
| PM | Requirements gathering, task breakdown |
| Backend Dev | Backend architecture and code |
| Frontend Dev | UI implementation |
| DevOps | Infrastructure and deployment |
| QA | Testing and validation |
| Security | Vulnerability management |
| UX | User experience design |

Agents are implemented in `src/agents/` using a base agent class with DSPy modules for LLM interaction.

## Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| AI | OpenAI, LangChain, DSPy |
| API | FastAPI + Uvicorn |
| Security | PyJWT, Cryptography, Bandit |
| Architecture | Durable Objects (concept), multi-agent collaboration |

## Project Structure

```
src/
  agents/           # PM, Dev, DevOps, UX, QA, Security agents
  config/           # DSPy configuration
  deployment/       # Deployment logic
  ai_team_collaboration.py
config/
  deployment/       # YAML deployment configs
  durable_objects.json
docs/
  architecture/     # 10+ architecture documents
examples/
  self_modifying_agent.py
projects/           # Generated project artifacts (2 notification-system projects)
```

## Setup

```bash
git clone https://github.com/jmanhype/aidevos.git
cd aidevos
pip install -r requirements.txt
cp .env.example .env
# Edit .env with API keys
```

## Status

Architectural prototype. The documentation is extensive (10+ architecture docs, Claude Code integration guides, agent SOPs) but the actual running system appears incomplete. The `projects/` directory contains 2 generated notification-system projects with JSON artifacts but no deployed code. No tests exist. The frontend plan references React/TypeScript/TailwindCSS but no frontend code is present.

## License

Not specified.
