"""Unit tests for Person 2's analytics tools."""
import pytest
import pandas as pd
import os

# Skip all tests if the Parquet file doesn't exist
PARQUET_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'Electric_Vehicle_Population_Data.parquet')
SKIP_IF_NO_DATA = pytest.mark.skipif(
    not os.path.exists(PARQUET_PATH),
    reason="Parquet data file not found"
)

@SKIP_IF_NO_DATA
class TestAnalyticsTools:
    
    def test_import(self):
        """analytics_tools.py is importable."""
        from scripts.analytics_tools import get_ev_counts_by_county
    
    def test_county_counts_returns_dataframe(self):
        """get_ev_counts_by_county returns a DataFrame."""
        from scripts.analytics_tools import get_ev_counts_by_county
        result = get_ev_counts_by_county(PARQUET_PATH)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
    
    def test_county_counts_has_expected_columns(self):
        """Result has County and ev_count columns."""
        from scripts.analytics_tools import get_ev_counts_by_county
        result = get_ev_counts_by_county(PARQUET_PATH)
        assert "County" in result.columns
        assert "ev_count" in result.columns
    
    def test_county_counts_king_is_top(self):
        """King County should have the most EVs in WA state."""
        from scripts.analytics_tools import get_ev_counts_by_county
        result = get_ev_counts_by_county(PARQUET_PATH)
        assert result.iloc[0]["County"] == "King"
    
    def test_adoption_growth_returns_dataframe(self):
        """get_adoption_growth_rate returns a DataFrame."""
        try:
            from scripts.analytics_tools import get_adoption_growth_rate
            result = get_adoption_growth_rate(PARQUET_PATH)
            assert isinstance(result, pd.DataFrame)
            assert len(result) > 0
        except ImportError:
            pytest.skip("get_adoption_growth_rate not yet created")
    
    def test_growth_rate_has_model_year(self):
        """Result has Model Year column."""
        try:
            from scripts.analytics_tools import get_adoption_growth_rate
            result = get_adoption_growth_rate(PARQUET_PATH)
            assert "Model Year" in result.columns
        except ImportError:
            pytest.skip("get_adoption_growth_rate not yet created")
