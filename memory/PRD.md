# UrbanisAI — Product Requirements Document

## Original Problem Statement
Web app "UrbanisAI": an AI-driven platform to plan, validate, and cost modular, sustainable housing projects. Professional monochrome architectural design with status-only accent colors (green=compliant, red=veto, amber=pending). Core flows: Dashboard, Site Validation (Leaflet map + deterministic flood/ecology veto), Design & Costing (drag-and-drop modular canvas + live cost/carbon), AI Formulation (6 sequential agents), Local Sourcing directory, Project Summary/Export (PDF). 4-step progress indicator.

## User Choices
- LLM: Gemini 3.1 Pro (via Emergent Universal Key, model `gemini-3.1-pro-preview`)
- Map: Leaflet + OpenStreetMap tiles
- Auth: JWT email/password (Bearer token in localStorage)
- PDF: client-side (jsPDF)
- Scope: build everything

## Architecture
- **Backend** (FastAPI + MongoDB, `/app/backend`): `server.py` (routes), `auth.py` (JWT+bcrypt), `agents.py` (LLM helper), `seed_data.py` (grounded materials/modules/regulations/suppliers + `compute_totals`).
- **Frontend** (React + Tailwind + shadcn, `/app/frontend/src`): AuthContext, ProjectContext, HeaderNav + StepIndicator, pages: Login, Dashboard, SiteValidation (Leaflet + turf), DesignCosting (HTML5 DnD grid + recharts), AiFormulation (6 agents), LocalSourcing, ProjectSummary (jsPDF).
- Data grounding: KAEL (citations), CRONOS (costs), TERRA (suppliers) return structured data; THOT/IRIS/LYRA use live Gemini.

## User Personas
- Architects, municipal planners, developers taking a site from raw data to submission-ready plan.

## Core Requirements (static)
- Deterministic hard-veto on flood/protected-land intersection (turf.booleanIntersects).
- Live cost + embodied-carbon recalculation on module/material change.
- Six-agent workflow with data-gap flagging naming responsible institution.
- Persist project state (site polygon, design, agent outputs) per user in MongoDB.

## Implemented (2026-06)
- Full JWT auth (seeded admin admin@urbanis.ai / urbanis2025), register/login/me.
- Dashboard with stat cards, New Project modal, quick-launch presets, project list + delete.
- Site Validation: Leaflet draw + presets, geodesic area/perimeter, flood/protected overlays, deterministic veto/approve banners, proceed gating.
- Design & Costing: drag-and-drop grid, materials DB, live totals, carbon-vs-benchmark + cost bar charts, per-module + bulk material swap.
- AI Formulation: 6 agents (THOT/IRIS/LYRA live Gemini; KAEL/CRONOS/TERRA grounded), run-all sequence, data-gap notices.
- Local Sourcing directory with radius/type filters + Connect toast.
- Project Summary with consolidated data + client-side PDF dossier export.
- Tested: 22/22 backend, all frontend flows pass (iteration_1).

## Backlog / Remaining (prioritized)
- P1: Editable polygon (drag vertices) and real geocoding search on the map.
- P2: Persist agent streaming logs; multi-user project sharing/roles.
- P2: Server-side PDF with embedded map snapshot; richer isometric 3D canvas.
