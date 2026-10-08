"""Grounded structured data for UrbanisAI — materials, modules, regulations, suppliers.
Numbers here are the single source of truth for CRONOS/KAEL/TERRA (no LLM hallucination)."""

TRADITIONAL_BENCHMARK_CARBON = 350  # kg CO2e/m2 for standard reinforced concrete build

MODULES = [
    {"id": "bedroom", "name": "Bedroom Module", "area": 18, "base_cost": 8000, "icon": "bed-double"},
    {"id": "kitchen", "name": "Kitchen Module", "area": 14, "base_cost": 12000, "icon": "cooking-pot"},
    {"id": "bathroom", "name": "Bathroom Module", "area": 8, "base_cost": 9000, "icon": "bath"},
    {"id": "living", "name": "Living Module", "area": 24, "base_cost": 10000, "icon": "sofa"},
    {"id": "solar_roof", "name": "Solar Roof", "area": 20, "base_cost": 15000, "icon": "sun"},
    {"id": "green_roof", "name": "Green Roof", "area": 20, "base_cost": 11000, "icon": "trees"},
]

# Structural / wall materials. cost = EUR/m2, carbon = kg CO2e/m2 (A1-A5 cradle-to-gate)
MATERIALS = [
    {"id": "clt", "name": "Cross-Laminated Timber", "cost_per_m2": 420, "carbon_per_m2": 40, "cert": "FSC"},
    {"id": "geopolymer", "name": "Low-Carbon Geopolymer Concrete", "cost_per_m2": 380, "carbon_per_m2": 180, "cert": "EPD EN 15804"},
    {"id": "recycled_steel", "name": "Recycled Steel", "cost_per_m2": 510, "carbon_per_m2": 260, "cert": "Cradle-to-Cradle"},
    {"id": "straw_bale", "name": "Straw-Bale Insulation", "cost_per_m2": 190, "carbon_per_m2": -20, "cert": "Biogenic"},
    {"id": "ceb", "name": "Compressed Earth Block", "cost_per_m2": 210, "carbon_per_m2": 60, "cert": "Local Sourced"},
    {"id": "bamboo", "name": "Engineered Bamboo", "cost_per_m2": 250, "carbon_per_m2": 30, "cert": "FSC"},
]

# KAEL regulatory citations — grounded, each tagged hierarchy level + date
REGULATIONS = [
    {"code": "ISO 37120:2018", "level": "International Standard", "date": "2018-07-01",
     "title": "Sustainable cities — Indicators for urban services and quality of life",
     "summary": "Baseline density, housing and quality-of-life indicators applied to the parcel context."},
    {"code": "IBC 2024 §1004", "level": "National Code", "date": "2024-01-01",
     "title": "Occupant Load & Means of Egress",
     "summary": "Minimum egress width and occupant-load calculations for multi-unit residential modules."},
    {"code": "Eurocode 5 (EN 1995-1-2)", "level": "National Code", "date": "2020-11-15",
     "title": "Design of Timber Structures — Fire",
     "summary": "Timber construction height caps and 60-min fire resistance for CLT and engineered bamboo modules.",
     "materials": ["clt", "bamboo"]},
    {"code": "EN 15804+A2", "level": "International Standard", "date": "2019-10-01",
     "title": "Environmental Product Declarations — Core Rules",
     "summary": "Embodied-carbon declaration methodology used for the project carbon balance sheet."},
    {"code": "Municipal Bylaw MB-14.2", "level": "Municipal Bylaw", "date": "2023-03-20",
     "title": "Residential Setback & Height Envelope",
     "summary": "Minimum 4m front setback, 3m side setbacks, max 12m building height in R2 residential zones."},
    {"code": "Municipal Bylaw MB-22.7", "level": "Municipal Bylaw", "date": "2022-09-05",
     "title": "Flood Resilience & Protected Ecology",
     "summary": "Absolute prohibition of habitable construction within designated 100-year flood zones and protected ecological reserves."},
    {"code": "EN 1990 (Eurocode 0)", "level": "National Code", "date": "2021-04-01",
     "title": "Basis of Structural Design",
     "summary": "Safety factors and load combinations for factory-assembled modular foundations."},
]

# TERRA suppliers directory (mock but structured)
SUPPLIERS = [
    {"id": "apex_timber", "name": "Apex Timber Prefab", "specialty": "Off-site CLT module fabrication",
     "location": "Bengaluru, India", "distance_km": 22, "materials": ["clt", "bamboo"], "cert": "FSC",
     "delivery": "Feasible — 6 week lead", "availability": "In production capacity",
     "contact": "logistics@apextimber.example", "type": "Fabricator",
     "image": "https://images.unsplash.com/photo-1570470836811-78ef04bb23d3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHxhcmNoaXRlY3QlMjBlbmdpbmVlciUyMHBvcnRyYWl0fGVufDB8fHx8MTc4OTQ2MzQ1Mnww&ixlib=rb-4.1.0&q=85"},
    {"id": "nordic_grid", "name": "Nordic Grid Architecture", "specialty": "Sustainable modular housing design",
     "location": "Pune, India", "distance_km": 41, "materials": ["clt", "straw_bale", "ceb"], "cert": "GRIHA Certified",
     "delivery": "Design consult — remote + on-site", "availability": "Available Q3",
     "contact": "studio@nordicgrid.example", "type": "Architect",
     "image": "https://images.unsplash.com/photo-1575282366139-d605e098a825?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHw0fHxhcmNoaXRlY3QlMjBlbmdpbmVlciUyMHBvcnRyYWl0fGVufDB8fHx8MTc4OTQ2MzQ1Mnww&ixlib=rb-4.1.0&q=85"},
    {"id": "bioconcrete", "name": "BioConcrete & Moduli", "specialty": "Low-carbon geopolymer & earth blocks",
     "location": "Navi Mumbai, India", "distance_km": 19, "materials": ["geopolymer", "ceb"], "cert": "EPD EN 15804",
     "delivery": "Feasible — 3 week lead", "availability": "Immediate",
     "contact": "orders@bioconcrete.example", "type": "Material Producer",
     "image": "https://images.unsplash.com/photo-1621905252472-943afaa20e20?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwzfHxhcmNoaXRlY3QlMjBlbmdpbmVlciUyMHBvcnRyYWl0fGVufDB8fHx8MTc4OTQ2MzQ1Mnww&ixlib=rb-4.1.0&q=85"},
    {"id": "circular_steel", "name": "Circular Steel Works", "specialty": "Recycled structural steel frames",
     "location": "Hyderabad, India", "distance_km": 27, "materials": ["recycled_steel"], "cert": "GreenPro Certified",
     "delivery": "Feasible — 5 week lead", "availability": "Limited capacity",
     "contact": "sales@circularsteel.example", "type": "Material Producer",
     "image": "https://images.unsplash.com/photo-1762335799387-da7889c2b657?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NTN8MHwxfHNlYXJjaHwyfHx1cmJhbiUyMHNpdGUlMjBibHVlcHJpbnQlMjBhZXJpYWx8ZW58MHx8fHwxNzg5NDYzNDQ4fDA&ixlib=rb-4.1.0&q=85"},
    {"id": "hempworks", "name": "HempWorks Insulation Co.", "specialty": "Straw-bale & biogenic insulation",
     "location": "Delhi NCR, India", "distance_km": 24, "materials": ["straw_bale"], "cert": "Biogenic",
     "delivery": "Feasible — 2 week lead", "availability": "Immediate",
     "contact": "hello@hempworks.example", "type": "Material Producer",
     "image": "https://images.unsplash.com/photo-1488972685288-c3fd157d7c7a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2MjJ8MHwxfHNlYXJjaHwxfHxtb2R1bGFyJTIwYXJjaGl0ZWN0dXJlJTIwYnVpbGRpbmclMjBmYWNhZGV8ZW58MHx8fHwxNzg5NDYzNDQ4fDA&ixlib=rb-4.1.0&q=85"},
]


def material_by_id(mid):
    return next((m for m in MATERIALS if m["id"] == mid), None)


def compute_totals(modules):
    """modules: list of {module_id, material}. Returns grounded totals."""
    total_cost = 0.0
    total_carbon = 0.0
    total_area = 0.0
    breakdown = []
    for m in modules:
        mod = next((x for x in MODULES if x["id"] == m.get("module_id")), None)
        mat = material_by_id(m.get("material"))
        if not mod or not mat:
            continue
        cost = mod["base_cost"] + mod["area"] * mat["cost_per_m2"]
        carbon = mod["area"] * mat["carbon_per_m2"]
        total_cost += cost
        total_carbon += carbon
        total_area += mod["area"]
        breakdown.append({
            "module": mod["name"], "material": mat["name"], "area": mod["area"],
            "cost": round(cost, 2), "carbon": round(carbon, 2),
        })
    benchmark = round(total_area * TRADITIONAL_BENCHMARK_CARBON, 2)
    return {
        "total_cost": round(total_cost, 2),
        "total_carbon": round(total_carbon, 2),
        "floor_area": round(total_area, 2),
        "units": len(breakdown),
        "benchmark_carbon": benchmark,
        "carbon_saving_pct": round((1 - (total_carbon / benchmark)) * 100, 1) if benchmark > 0 else 0,
        "breakdown": breakdown,
    }
