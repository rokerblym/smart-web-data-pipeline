from app.services.analyzer import heuristic_analysis

def test_heuristic_analysis_shape():
    result = heuristic_analysis(
        "Python FastAPI PostgreSQL backend development. Python APIs are useful for backend services."
    )
    assert "summary" in result
    assert "keywords" in result
    assert isinstance(result["keywords"], list)
    assert result["sentiment"] == "neutral"
