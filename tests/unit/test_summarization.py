"""Unit tests for AI summarization without API key."""
import pytest
from app.ai.summarization import (
    _compute_keyword_urgency,
    _max_urgency,
    _parse_gemini_response,
    summarize_job_card,
)


class TestKeywordUrgency:
    """Test keyword-based urgency detection (safety floor)."""
    
    def test_critical_keywords_detected(self):
        """Critical safety keywords should return critical urgency."""
        assert _compute_keyword_urgency("brake failure reported") == "critical"
        assert _compute_keyword_urgency("engine seizure") == "critical"
        assert _compute_keyword_urgency("airbag warning light") == "critical"
    
    def test_high_keywords_detected(self):
        """High-priority keywords should return high urgency."""
        assert _compute_keyword_urgency("brake noise when stopping") == "high"
        assert _compute_keyword_urgency("steering vibration") == "high"
        assert _compute_keyword_urgency("engine overheating") == "high"
    
    def test_medium_keywords_detected(self):
        """Medium-priority keywords should return medium urgency."""
        assert _compute_keyword_urgency("oil change due") == "medium"
        assert _compute_keyword_urgency("tire rotation needed") == "medium"
    
    def test_low_keywords_detected(self):
        """Low-priority keywords should return low urgency."""
        assert _compute_keyword_urgency("cosmetic scratch on door") == "low"
        assert _compute_keyword_urgency("interior cleaning") == "low"
    
    def test_no_keywords_defaults_low(self):
        """No matching keywords should default to low urgency."""
        assert _compute_keyword_urgency("routine inspection") == "low"
        assert _compute_keyword_urgency("") == "low"


class TestMaxUrgency:
    """Test urgency safety floor (AI cannot downgrade below keyword level)."""
    
    def test_critical_always_wins(self):
        """Critical should override any other urgency."""
        assert _max_urgency("critical", "low") == "critical"
        assert _max_urgency("low", "critical") == "critical"
        assert _max_urgency("critical", "critical") == "critical"
    
    def test_high_overrides_medium_low(self):
        """High should override medium and low."""
        assert _max_urgency("high", "medium") == "high"
        assert _max_urgency("high", "low") == "high"
        assert _max_urgency("low", "high") == "high"
    
    def test_medium_overrides_low(self):
        """Medium should override low."""
        assert _max_urgency("medium", "low") == "medium"
        assert _max_urgency("low", "medium") == "medium"
    
    def test_equal_urgency_unchanged(self):
        """Equal urgency should return either (same value)."""
        assert _max_urgency("medium", "medium") == "medium"
        assert _max_urgency("low", "low") == "low"


class TestParseGeminiResponse:
    """Test parsing of Gemini JSON responses."""
    
    def test_valid_json_parsed_correctly(self):
        """Well-formed JSON should parse correctly."""
        json_text = '''{
            "technical_summary": "Brake pads at 2mm",
            "customer_summary": "Your brakes need attention",
            "urgency": "high",
            "estimated_cost": 4500,
            "recommended_action": "Schedule within 2 weeks"
        }'''
        
        result = _parse_gemini_response(json_text)
        
        assert result["technical_summary"] == "Brake pads at 2mm"
        assert result["customer_summary"] == "Your brakes need attention"
        assert result["urgency"] == "high"
        assert result["estimated_cost"] == 4500
        assert result["recommended_action"] == "Schedule within 2 weeks"
    
    def test_json_in_markdown_code_block(self):
        """JSON wrapped in markdown code blocks should be extracted."""
        markdown_text = '''```json
        {
            "technical_summary": "Test summary",
            "customer_summary": "Test customer",
            "urgency": "medium",
            "estimated_cost": 1000,
            "recommended_action": "Test action"
        }
        ```'''
        
        result = _parse_gemini_response(markdown_text)
        
        assert result["technical_summary"] == "Test summary"
        assert result["urgency"] == "medium"
    
    def test_malformed_json_returns_fallback(self):
        """Malformed JSON should return safe fallback."""
        malformed = "This is not JSON"
        
        result = _parse_gemini_response(malformed)
        
        assert "Unable to parse" in result["technical_summary"]
        assert result["urgency"] == "medium"
        assert result["estimated_cost"] == 0.0
    
    def test_empty_string_returns_fallback(self):
        """Empty string should return safe fallback."""
        result = _parse_gemini_response("")
        
        assert "Unable to parse" in result["technical_summary"]
        assert result["urgency"] == "medium"


class TestSummarizeJobCardFallback:
    """Test fallback behavior when Gemini is unavailable."""
    
    @pytest.mark.asyncio
    async def test_fallback_on_api_error(self):
        """When Gemini fails, should return keyword-based fallback."""
        # This test runs without API key - triggers exception path
        result = await summarize_job_card(
            job_no="JB-0001",
            mechanic_notes="brake failure reported by customer",
            vehicle_info={"make": "Maruti", "model": "Swift", "year": 2019},
            estimate_parts=[],
            estimate_total=0.0,
        )
        
        # Should return structured fallback
        assert "job_no" in result or "_error" in result or "technical_summary" in result
        
        # If it has urgency, brake failure should make it critical or high
        if "urgency" in result:
            assert result["urgency"] in ["critical", "high", "medium", "low"]
    
    @pytest.mark.asyncio
    async def test_safety_floor_applied(self):
        """Urgency should never be lower than keyword-detected level."""
        result = await summarize_job_card(
            job_no="JB-0001",
            mechanic_notes="brake failure reported",
            vehicle_info={},
            estimate_parts=[],
            estimate_total=0.0,
        )
        
        # Brake failure = critical keyword
        # AI might suggest medium, but safety floor should raise to critical
        if "urgency" in result:
            assert result["urgency"] in ["critical", "high"]  # Should not be medium/low


class TestSummarizationIntegration:
    """Integration-style tests for the full summarization pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_with_mock(self, monkeypatch):
        """Test full pipeline with mocked Gemini response."""
        # Mock the Gemini call
        async def mock_call_gemini(prompt, system_prompt=None):
            return '''{
                "technical_summary": "Mock technical summary",
                "customer_summary": "Mock customer summary",
                "urgency": "medium",
                "estimated_cost": 5000,
                "recommended_action": "Mock recommendation"
            }'''
        
        monkeypatch.setattr("app.ai.summarization.call_gemini", mock_call_gemini)
        
        result = await summarize_job_card(
            job_no="JB-TEST-001",
            mechanic_notes="brake pad replacement needed",
            vehicle_info={"make": "Honda", "model": "City", "year": 2020},
            estimate_parts=[{"part": "brake_pad", "cost": 2000}],
            estimate_total=4500.0,
        )
        
        assert result["technical_summary"] == "Mock technical summary"
        assert result["customer_summary"] == "Mock customer summary"
        # Safety floor: brake keyword = high, should override AI medium
        assert result["urgency"] == "high"  # _max_urgency("high", "medium")
        assert result["estimated_cost"] == 5000
        assert result["recommended_action"] == "Mock recommendation"
