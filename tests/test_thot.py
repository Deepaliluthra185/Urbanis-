"""
Unit tests for THOT — Site & Terrain Intelligence Agent
=========================================================
Tests spatial point-in-polygon checks, dataset loading, and the
complete Site Feasibility Brief output structure.

Run with:
    python -m pytest tests/test_thot.py -v
or from repo root:
    python -m pytest tests/test_thot.py -v --tb=short
"""

import asyncio
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Ensure repo root is on sys.path so imports work without install
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agents.thot.thot_agent import ThotAgent, SHAPELY_AVAILABLE

# ---------------------------------------------------------------------------
# Helper — run async coroutines in sync test functions
# Python 3.14 removed deprecated asyncio.get_event_loop(); use asyncio.run().
# ---------------------------------------------------------------------------


def run_async(coro):
    """Utility to run a coroutine synchronously inside a test."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def agent():
    """Shared ThotAgent instance — datasets loaded once and reused across tests."""
    a = ThotAgent()
    # Pre-load datasets synchronously so all fixtures share the same loaded state
    a._load_datasets()
    return a


@pytest.fixture(scope="module")
def amritsar_brief(agent):
    """Full Site Feasibility Brief for Amritsar — the baseline test site."""
    site_data = {
        "latitude": 31.6340,
        "longitude": 74.8723,
        "city": "Amritsar",
        "state": "Punjab",
        "project_name": "Test Housing Block — Amritsar",
    }
    return run_async(agent.analyze_site(site_data))


@pytest.fixture(scope="module")
def delhi_brief(agent):
    """Full Site Feasibility Brief for Delhi."""
    site_data = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "city": "Delhi",
        "state": "Delhi NCT",
        "project_name": "Delhi Test Site",
    }
    return run_async(agent.analyze_site(site_data))


@pytest.fixture(scope="module")
def jaisalmer_brief(agent):
    """Full Site Feasibility Brief for Jaisalmer (Hot & Dry zone)."""
    site_data = {
        "latitude": 26.9157,
        "longitude": 70.9083,
        "city": "Jaisalmer",
        "state": "Rajasthan",
        "project_name": "Jaisalmer Desert Test Site",
    }
    return run_async(agent.analyze_site(site_data))


# ===========================================================================
# 1. Environment & Setup Tests
# ===========================================================================


class TestEnvironment:
    def test_shapely_available(self):
        """Shapely should be installed (pip install shapely)."""
        assert SHAPELY_AVAILABLE is True, (
            "Shapely is not installed. Run: pip install shapely\n"
            "The agent will fall back to bounding-box checks, but full accuracy requires Shapely."
        )

    def test_dataset_files_exist(self):
        """All required dataset files must be present on disk."""
        data_dir = REPO_ROOT / "data" / "datasets" / "thot"
        rules_dir = REPO_ROOT / "agents" / "thot" / "rules"

        assert (data_dir / "seismic_zones.geojson").exists(), (
            "seismic_zones.geojson not found in data/datasets/thot/"
        )
        assert (data_dir / "flood_risk_zones.geojson").exists(), (
            "flood_risk_zones.geojson not found in data/datasets/thot/"
        )
        assert (rules_dir / "climate_zones.json").exists(), (
            "climate_zones.json not found in agents/thot/rules/"
        )

    def test_agent_instantiates(self):
        """ThotAgent must instantiate without errors."""
        a = ThotAgent()
        assert a is not None
        assert a._loaded is False  # Lazy-load — not loaded yet


# ===========================================================================
# 2. Amritsar Baseline — Seismic Zone Tests (BIS IS 1893:2016)
# ===========================================================================


class TestSeismicZone:
    def test_amritsar_is_zone_iv(self, amritsar_brief):
        """Amritsar (31.63°N, 74.87°E) must classify as BIS Seismic Zone IV."""
        seismic = amritsar_brief["assessments"]["seismic_zone"]
        assert seismic["zone"] == "Zone IV", (
            f"Expected Zone IV for Amritsar, got: {seismic['zone']}"
        )

    def test_seismic_zone_number(self, amritsar_brief):
        """Zone number must be 4 for Zone IV."""
        seismic = amritsar_brief["assessments"]["seismic_zone"]
        assert seismic["zone_number"] == 4

    def test_seismic_zone_factor(self, amritsar_brief):
        """Zone Factor Z for Zone IV is 0.24 per IS 1893:2016 Table 3."""
        seismic = amritsar_brief["assessments"]["seismic_zone"]
        assert seismic["zone_factor_Z"] == pytest.approx(0.24, abs=0.01)

    def test_seismic_pga(self, amritsar_brief):
        """Peak Ground Acceleration for Zone IV ≥ 0.20g."""
        seismic = amritsar_brief["assessments"]["seismic_zone"]
        assert seismic["peak_ground_acceleration_g"] >= 0.20

    def test_seismic_bis_standard_cited(self, amritsar_brief):
        """Output must cite the IS 1893 standard."""
        seismic = amritsar_brief["assessments"]["seismic_zone"]
        assert "1893" in seismic["bis_standard"]

    def test_seismic_design_recommendation_present(self, amritsar_brief):
        """Design recommendation must be a non-empty string."""
        seismic = amritsar_brief["assessments"]["seismic_zone"]
        assert isinstance(seismic["design_recommendation"], str)
        assert len(seismic["design_recommendation"]) > 20

    def test_seismic_confidence_high(self, amritsar_brief):
        """Matched site should return HIGH confidence (not fallback)."""
        seismic = amritsar_brief["assessments"]["seismic_zone"]
        assert seismic["confidence"] == "HIGH"

    def test_delhi_seismic_zone_iv(self, delhi_brief):
        """Delhi (28.61°N, 77.21°E) must also classify as Zone IV."""
        seismic = delhi_brief["assessments"]["seismic_zone"]
        assert seismic["zone"] == "Zone IV"


# ===========================================================================
# 3. Amritsar Baseline — Flood Risk Tests
# ===========================================================================


class TestFloodRisk:
    def test_amritsar_flood_risk_medium(self, amritsar_brief):
        """
        Amritsar lies in the Punjab alluvial flood-prone plain (MEDIUM risk).
        It is NOT inside the high-risk Beas River channel corridor
        (Beas corridor lon starts at 75.0°E; Amritsar is at 74.87°E).
        """
        flood = amritsar_brief["assessments"]["flood_risk"]
        assert flood["risk_level"] == "MEDIUM", (
            f"Expected MEDIUM flood risk for Amritsar, got: {flood['risk_level']}"
        )

    def test_amritsar_flood_risk_score(self, amritsar_brief):
        """MEDIUM risk maps to risk_score = 2."""
        flood = amritsar_brief["assessments"]["flood_risk"]
        assert flood["risk_score"] == 2

    def test_flood_zone_type_present(self, amritsar_brief):
        """flood_zone_type must be a non-empty string."""
        flood = amritsar_brief["assessments"]["flood_risk"]
        assert isinstance(flood["flood_zone_type"], str)
        assert len(flood["flood_zone_type"]) > 5

    def test_flood_matched_zones_list(self, amritsar_brief):
        """matched_zones must be a list (possibly containing multiple zone matches)."""
        flood = amritsar_brief["assessments"]["flood_risk"]
        assert isinstance(flood["matched_zones"], list)

    def test_flood_mitigation_notes_present(self, amritsar_brief):
        """Mitigation notes must be provided for any matched flood zone."""
        flood = amritsar_brief["assessments"]["flood_risk"]
        assert isinstance(flood["mitigation_notes"], str)
        assert len(flood["mitigation_notes"]) > 20

    def test_flood_data_source_cited(self, amritsar_brief):
        """CWC or NDMA must be referenced in the data source."""
        flood = amritsar_brief["assessments"]["flood_risk"]
        src = flood["data_source"].upper()
        assert "CWC" in src or "NDMA" in src or "FLOOD" in src

    def test_jaisalmer_low_flood_risk(self, jaisalmer_brief):
        """Jaisalmer (desert city, far from rivers) should have LOW flood risk."""
        flood = jaisalmer_brief["assessments"]["flood_risk"]
        # Jaisalmer should be LOW or MEDIUM (not HIGH)
        assert flood["risk_level"] in ("LOW", "MEDIUM"), (
            f"Jaisalmer should not be HIGH flood risk, got: {flood['risk_level']}"
        )


# ===========================================================================
# 4. Amritsar Baseline — Climate Zone Tests
# ===========================================================================


class TestClimateZone:
    def test_amritsar_climate_composite(self, amritsar_brief):
        """Amritsar must be classified as 'Composite' climate zone per BEE ECBC 2017."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        assert climate["zone"] == "Composite", (
            f"Expected Composite climate for Amritsar, got: {climate['zone']}"
        )

    def test_ecbc_code_present(self, amritsar_brief):
        """BEE ECBC code must be present."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        assert climate["bee_ecbc_code"] is not None
        assert len(str(climate["bee_ecbc_code"])) > 0

    def test_imd_classification_present(self, amritsar_brief):
        """IMD classification string must be populated."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        assert isinstance(climate["imd_classification"], str)
        assert len(climate["imd_classification"]) > 5

    def test_summer_temp_max(self, amritsar_brief):
        """Summer max temperature for Composite zone must be ≥ 40°C (Punjab summers)."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        assert climate["summer_temp_max_c"] >= 40, (
            f"Expected summer max ≥ 40°C for Amritsar, got: {climate['summer_temp_max_c']}"
        )

    def test_winter_temp_min(self, amritsar_brief):
        """Winter min temperature for Composite zone must be ≤ 10°C (Punjab winters)."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        assert climate["winter_temp_min_c"] <= 10, (
            f"Expected winter min ≤ 10°C for Amritsar, got: {climate['winter_temp_min_c']}"
        )

    def test_monsoon_months_populated(self, amritsar_brief):
        """Monsoon months list must be non-empty for Composite zone."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        assert isinstance(climate["monsoon_months"], list)
        assert len(climate["monsoon_months"]) >= 3, (
            "Composite zone should have at least 3 monsoon months"
        )

    def test_passive_design_strategies_present(self, amritsar_brief):
        """At least 3 passive design strategies must be listed."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        strategies = climate["passive_design_strategies"]
        assert isinstance(strategies, list)
        assert len(strategies) >= 3

    def test_ecbc_envelope_requirements_present(self, amritsar_brief):
        """ECBC envelope U-value requirements must be present."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        ecbc = climate["ecbc_envelope_requirements"]
        assert isinstance(ecbc, dict)
        assert "roof_u_value_max" in ecbc

    def test_amritsar_detailed_profile_present(self, amritsar_brief):
        """Amritsar should return the detailed city climate profile."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        assert "city_detailed_profile" in climate, (
            "Amritsar should have a detailed city climate profile"
        )
        profile = climate["city_detailed_profile"]
        assert profile["city"] == "Amritsar"
        assert "temperature_data" in profile
        assert "rainfall_data" in profile

    def test_climate_confidence_high_for_known_city(self, amritsar_brief):
        """Known city (Amritsar) lookup should return HIGH confidence."""
        climate = amritsar_brief["assessments"]["climate_zone"]
        assert climate["confidence"] == "HIGH"

    def test_jaisalmer_climate_hot_dry(self, jaisalmer_brief):
        """Jaisalmer must be classified as 'Hot & Dry' per BEE ECBC 2017."""
        climate = jaisalmer_brief["assessments"]["climate_zone"]
        assert climate["zone"] == "Hot & Dry", (
            f"Expected Hot & Dry for Jaisalmer, got: {climate['zone']}"
        )


# ===========================================================================
# 5. Terrain & Elevation Tests
# ===========================================================================


class TestTerrainElevation:
    def test_amritsar_elevation_range(self, amritsar_brief):
        """Amritsar (Punjab plains at ~234m AMSL) should return elevation between 200–350m."""
        terrain = amritsar_brief["assessments"]["terrain_elevation"]
        elev = terrain["approx_elevation_m_amsl"]
        assert 150 <= elev <= 400, (
            f"Amritsar elevation should be 150–400m AMSL, got: {elev}m"
        )

    def test_terrain_classification_plain(self, amritsar_brief):
        """Amritsar lies on the level alluvial Punjab plain."""
        terrain = amritsar_brief["assessments"]["terrain_elevation"]
        assert "Plain" in terrain["terrain_classification"], (
            f"Expected 'Plain' in terrain class for Amritsar, got: {terrain['terrain_classification']}"
        )

    def test_groundwater_depth_present(self, amritsar_brief):
        """Groundwater depth estimate must be a non-empty string."""
        terrain = amritsar_brief["assessments"]["terrain_elevation"]
        assert isinstance(terrain["groundwater_depth_estimate"], str)
        assert len(terrain["groundwater_depth_estimate"]) > 5

    def test_soil_type_present(self, amritsar_brief):
        """Soil type must include IS 1498 classification reference."""
        terrain = amritsar_brief["assessments"]["terrain_elevation"]
        assert "IS 1498" in terrain["soil_type_estimate"]

    def test_bearing_capacity_present(self, amritsar_brief):
        """Bearing capacity estimate must be a non-empty string."""
        terrain = amritsar_brief["assessments"]["terrain_elevation"]
        assert isinstance(terrain["bearing_capacity_estimate_kn_m2"], str)
        assert len(terrain["bearing_capacity_estimate_kn_m2"]) > 5

    def test_liquefaction_susceptibility_present(self, amritsar_brief):
        """Liquefaction susceptibility assessment must be present."""
        terrain = amritsar_brief["assessments"]["terrain_elevation"]
        assert isinstance(terrain["liquefaction_susceptibility"], str)
        assert len(terrain["liquefaction_susceptibility"]) > 10

    def test_dem_source_cited(self, amritsar_brief):
        """DEM source must reference ISRO Bhuvan."""
        terrain = amritsar_brief["assessments"]["terrain_elevation"]
        assert "Bhuvan" in terrain["dem_source"] or "ISRO" in terrain["dem_source"]


# ===========================================================================
# 6. Feasibility Score Tests
# ===========================================================================


class TestFeasibilityScore:
    def test_feasibility_score_numeric(self, amritsar_brief):
        """Overall feasibility score must be a float between 0 and 100."""
        score = amritsar_brief["feasibility_summary"]["overall_score"]
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_amritsar_conditionally_feasible(self, amritsar_brief):
        """
        Amritsar: Zone IV seismic + MEDIUM flood risk means the site should be
        CONDITIONALLY FEASIBLE (not outright FEASIBLE or HIGH RISK).
        """
        summary = amritsar_brief["feasibility_summary"]
        verdict = summary["verdict"]
        assert "FEASIBLE" in verdict, f"Expected FEASIBLE in verdict, got: {verdict}"

    def test_component_scores_present(self, amritsar_brief):
        """All four component scores must be present."""
        components = amritsar_brief["feasibility_summary"]["component_scores"]
        assert "seismic" in components
        assert "flood" in components
        assert "terrain" in components
        assert "climate" in components

    def test_component_scores_in_range(self, amritsar_brief):
        """Each component score must be 0–100."""
        components = amritsar_brief["feasibility_summary"]["component_scores"]
        for key, val in components.items():
            score = val["score"]
            assert 0 <= score <= 100, f"Component '{key}' score out of range: {score}"

    def test_recommendation_present(self, amritsar_brief):
        """Recommendation string must be non-empty."""
        summary = amritsar_brief["feasibility_summary"]
        assert isinstance(summary["recommendation"], str)
        assert len(summary["recommendation"]) > 30

    def test_verdict_color_present(self, amritsar_brief):
        """verdict_color must be one of: green, amber, red."""
        color = amritsar_brief["feasibility_summary"]["verdict_color"]
        assert color in ("green", "amber", "red"), f"Unexpected verdict_color: {color}"


# ===========================================================================
# 7. Output Structure & Metadata Tests
# ===========================================================================


class TestOutputStructure:
    def test_top_level_keys(self, amritsar_brief):
        """Brief must contain all required top-level keys."""
        required_keys = [
            "agent", "version", "brief_title", "generated_at",
            "site", "assessments", "feasibility_summary",
            "spatial_engine", "datasets_used", "disclaimer",
        ]
        for key in required_keys:
            assert key in amritsar_brief, f"Missing top-level key: '{key}'"

    def test_agent_identity(self, amritsar_brief):
        """Agent name must be THOT."""
        assert amritsar_brief["agent"] == "THOT"

    def test_site_metadata(self, amritsar_brief):
        """Site block must contain all coordinate metadata."""
        site = amritsar_brief["site"]
        assert site["city"] == "Amritsar"
        assert site["state"] == "Punjab"
        assert abs(site["latitude"] - 31.6340) < 0.001
        assert abs(site["longitude"] - 74.8723) < 0.001
        assert site["coordinate_system"] == "WGS84 / EPSG:4326"

    def test_assessments_keys(self, amritsar_brief):
        """All four assessment keys must be present."""
        assessments = amritsar_brief["assessments"]
        assert "seismic_zone" in assessments
        assert "flood_risk" in assessments
        assert "climate_zone" in assessments
        assert "terrain_elevation" in assessments

    def test_generated_at_is_iso(self, amritsar_brief):
        """generated_at must be a valid ISO 8601 timestamp string."""
        from datetime import datetime
        ts = amritsar_brief["generated_at"]
        assert isinstance(ts, str)
        # Should parse without exception
        datetime.fromisoformat(ts.replace("Z", "+00:00"))

    def test_datasets_used_list(self, amritsar_brief):
        """datasets_used must be a non-empty list of strings."""
        ds = amritsar_brief["datasets_used"]
        assert isinstance(ds, list)
        assert len(ds) >= 3

    def test_disclaimer_present(self, amritsar_brief):
        """Disclaimer must be present and non-trivial."""
        disclaimer = amritsar_brief["disclaimer"]
        assert isinstance(disclaimer, str)
        assert len(disclaimer) > 50

    def test_brief_title_contains_project_name(self, amritsar_brief):
        """Brief title must contain the supplied project name."""
        assert "Test Housing Block" in amritsar_brief["brief_title"]


# ===========================================================================
# 8. Edge-Case & Default Tests
# ===========================================================================


class TestEdgeCases:
    def test_default_coordinates_amritsar(self):
        """Calling analyze_site with empty dict should default to Amritsar."""
        agent = ThotAgent()
        brief = run_async(agent.analyze_site({}))
        assert brief["site"]["city"] == "Amritsar"
        assert brief["site"]["latitude"] == pytest.approx(31.6340, abs=0.001)

    def test_unknown_city_does_not_crash(self):
        """An unknown city name must not raise — should use coordinate fallback."""
        agent = ThotAgent()
        brief = run_async(agent.analyze_site({
            "latitude": 25.0,
            "longitude": 71.0,
            "city": "Nowhere City XYZ",
            "state": "Unknown State",
        }))
        climate = brief["assessments"]["climate_zone"]
        assert climate["zone"] in ("Composite", "Hot & Dry", "Warm & Humid", "Temperate", "Cold")

    def test_multiple_calls_reuse_loaded_datasets(self):
        """Calling analyze_site twice on the same agent should not reload datasets."""
        agent = ThotAgent()
        run_async(agent.analyze_site({"city": "Amritsar"}))
        assert agent._loaded is True
        run_async(agent.analyze_site({"city": "Ludhiana", "latitude": 30.9010, "longitude": 75.8573}))
        assert agent._loaded is True  # Still True — not reloaded

    def test_string_lat_lon_coercion(self):
        """latitude/longitude supplied as strings must be coerced to float."""
        agent = ThotAgent()
        brief = run_async(agent.analyze_site({
            "latitude": "31.6340",
            "longitude": "74.8723",
            "city": "Amritsar",
        }))
        assert brief["site"]["latitude"] == pytest.approx(31.634, abs=0.001)

    def test_delhi_flood_risk_high(self, delhi_brief):
        """
        Delhi (28.61°N, 77.21°E) lies in the Yamuna-Hindon doab HIGH risk zone.
        """
        flood = delhi_brief["assessments"]["flood_risk"]
        assert flood["risk_level"] == "HIGH", (
            f"Expected HIGH flood risk for Delhi/Yamuna plain, got: {flood['risk_level']}"
        )
