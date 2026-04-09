# AI BIM House Generator

**An AI agent that converts natural language prompts into BIM (IFC) house models using procedural generation.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![IFC4](https://img.shields.io/badge/IFC-4-orange.svg)](https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/)

---

## 🧠 Overview

This project provides a production-ready AI system that:
- **Understands**: Natural language house descriptions (e.g., "casa moderna de 12x8 metros com telhado")
- **Generates**: Industry-standard IFC (Industry Foundation Classes) building models
- **Scales**: Modular architecture with API, CLI, and extensible workers

**Tech Stack:**
- `ifcopenshell` — IFC file creation and geometry
- `LangChain` / `LangGraph` — AI agent orchestration
- `Google Gemini` — LLM for prompt parsing (configurable)
- `FastAPI` + `Pydantic` — REST API with validation
- `NumPy` — 3D transformation matrices

---

## 📦 Project Structure

```
ai-bim-house-generator/
├── agent/
│   ├── planner.py      # Prompt → HousePlan (AI/mock parser)
│   ├── generator.py    # HousePlan → IFC file
│   └── agent.py        # Orchestrator (planner → generator)
├── api/
│   └── main.py         # FastAPI REST API
├── models/
│   └── schema.py       # Pydantic schemas (HousePlan)
├── scripts/
│   └── generate_ifc.py # CLI entrypoint
├── generate_house.py   # IFC geometry helpers (walls, slabs, roofs)
├── agent.py            # Legacy monolithic agent (LangChain + Gemini)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or with uv (recommended)
uv pip install -r requirements.txt
```

### 2. API Usage

```bash
# Start the FastAPI server
uvicorn api.main:app --reload
```

**Generate from prompt:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "casa moderna de 12x8 metros com telhado"}'
```

**Generate from structured plan:**
```bash
curl -X POST "http://localhost:8000/generate/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "width": 10.0,
    "depth": 12.0,
    "wall_height": 3.0,
    "with_roof": true,
    "output_path": "modern_house.ifc"
  }'
```

### 3. CLI Usage

```bash
# From natural language
python scripts/generate_ifc.py "casa de 10x12 metros com telhado"

# With explicit parameters
python scripts/generate_ifc.py --width 10 --depth 12 --roof --output house.ifc

# Interactive mode
python scripts/generate_ifc.py --interactive
```

### 4. Python API

```python
from agent.agent import run_agent
from models.schema import HousePlan

# From prompt
file, summary = run_agent("casa moderna de 12x8 metros")
print(summary)

# From structured plan
plan = HousePlan(width=10, depth=12, with_roof=True)
from agent.agent import run_agent_with_plan
file, summary = run_agent_with_plan(plan)
```

---

## 🏗️ Architecture

### Pipeline Flow

```
User Prompt → Planner → HousePlan → Generator → IFC File
                ↓                        ↓
            (LLM/mock)           (ifcopenshell)
```

1. **Planner** (`agent/planner.py`): Converts natural language → structured `HousePlan` schema
   - MVP: Mock parser with keyword detection
   - Production: LLM integration (Gemini/OpenAI)

2. **Generator** (`agent/generator.py`): Converts `HousePlan` → IFC geometry
   - Creates IFC4 project structure (project → site → building → storey)
   - Generates walls, slabs, roofs using `ifcopenshell.api`

3. **Orchestrator** (`agent/agent.py`): Coordinates planner → generator pipeline

4. **API** (`api/main.py`): FastAPI endpoints for REST access

---

## 🔥 Features

✅ **Natural language to IFC**: "casa de 10x12 metros" → `house.ifc`  
✅ **REST API**: FastAPI with OpenAPI docs at `/docs`  
✅ **CLI**: Interactive and batch modes  
✅ **Pydantic validation**: Type-safe schemas with automatic validation  
✅ **IFC4 compliant**: Industry-standard output (opens in Revit, ArchiCAD, BlenderBIM)  
✅ **Modular design**: Clean separation (planner ↔ generator ↔ API)

---

## 🚧 Roadmap (Production-Ready Extensions)

### Scalability
- [ ] **Task queues**: Redis + Celery for async IFC generation
- [ ] **Job tracking**: `/status/{job_id}` endpoint for long-running jobs
- [ ] **Storage abstraction**: S3-compatible blob storage (local → cloud)
- [ ] **Docker**: `docker-compose` with API + workers + Redis
- [ ] **Observability**: Structured logging, Prometheus metrics, OpenTelemetry tracing

### AI Enhancements
- [ ] **LLM planner**: Replace mock parser with Gemini/OpenAI
- [ ] **Multi-room support**: Parse room descriptions (bedrooms, bathrooms, etc.)
- [ ] **Doors & windows**: Parametric placement from prompts

### Geometry Extensions
- [ ] **Roof types**: Flat, hip, shed (beyond gable)
- [ ] **Stairs**: Multi-storey buildings
- [ ] **Complex shapes**: L-shaped, T-shaped footprints

---

## 📝 Development

### Run Tests

```bash
pytest tests/
```

### Code Style

```bash
ruff check .
ruff format .
```

### Type Checking

```bash
mypy agent/ api/ models/
```

---

## 💡 Example Use Cases

**Portfolio Project Statement:**
> "I built an AI agent that translates natural language into structured BIM models (IFC) using procedural generation and automation pipelines."

**Real-World Applications:**
- Rapid prototyping for architects
- Automated mass housing generation
- BIM model templates for construction firms

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 🤝 Contributing

Contributions welcome! Open an issue or PR to:
- Add new geometry types (doors, windows, stairs)
- Implement LLM planner (Gemini/OpenAI)
- Add async job processing (Celery)
- Improve test coverage

---

## 📚 References

- [ifcopenshell Documentation](https://docs.ifcopenshell.org/)
- [IFC4 Specification](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)