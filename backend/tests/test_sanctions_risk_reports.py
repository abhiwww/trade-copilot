from app.services.document_forensics import DocumentForensicsEngine
from app.services.risk_engine import RiskEngine
from app.services.report_generator import ReportGenerator
from app.services.sanctions_engine import SanctionsScreeningEngine


def test_sanctions_screening_flags_known_entity():
    engine = SanctionsScreeningEngine()
    result = engine.screen_entity("ABC TRADING LTD", "India")
    assert result["status"] in {"MATCH", "POSSIBLE_MATCH"}


def test_forensics_detects_metadata_anomaly():
    engine = DocumentForensicsEngine()
    result = engine.analyze_document({
        "filename": "invoice.pdf",
        "metadata": {"author": "unknown", "modification_date": "2020-01-01"},
        "text": "Invoice total USD 5000.00",
        "hash": "abc123",
    })
    assert any(signal["category"] == "metadata" for signal in result["signals"])


def test_risk_engine_calculates_overall_score():
    engine = RiskEngine()
    scores = {
        "document": 40,
        "regulatory": 60,
        "sanctions": 90,
        "financial": 55,
        "shipment": 25,
        "integrity": 70,
        "party": 45,
        "data_quality": 35,
    }
    result = engine.calculate(scores)
    assert result["overall_score"] > 0
    assert result["risk_level"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def test_report_generation_creates_file():
    generator = ReportGenerator()
    report = generator.generate_report(
        case_id="CASE-001",
        title="Trade Compliance Review",
        findings=[{"title": "Mismatch", "severity": "HIGH"}],
        risk={"overall_score": 76, "risk_level": "HIGH"},
    )
    assert report["status"] == "generated"
    assert report["path"].endswith(".md")
