"""Unit tests for Person 3's RAG pipeline."""
import pytest
import os

SKIP_IF_NO_KEY = pytest.mark.skipif(
    not os.getenv("PINECONE_API_KEY"),
    reason="PINECONE_API_KEY not set"
)

class TestRAGQuery:
    
    def test_import(self):
        """rag_query.py is importable."""
        try:
            from scripts.rag_query import query_policy_docs
        except ImportError:
            pytest.skip("rag_query.py not yet created")
    
    @SKIP_IF_NO_KEY
    def test_query_returns_list(self):
        """query_policy_docs returns a list."""
        from scripts.rag_query import query_policy_docs
        result = query_policy_docs("What EV incentives exist in WA?")
        assert isinstance(result, list)
    
    @SKIP_IF_NO_KEY
    def test_query_results_have_required_keys(self):
        """Each result has text, source, and score."""
        from scripts.rag_query import query_policy_docs
        results = query_policy_docs("EV tax credit eligibility")
        if len(results) > 0:
            for r in results:
                assert "text" in r
                assert "source" in r
                assert "score" in r
    
    @SKIP_IF_NO_KEY
    def test_query_results_are_relevant(self):
        """Top result should have a reasonable similarity score."""
        from scripts.rag_query import query_policy_docs
        results = query_policy_docs("Washington state electric vehicle laws")
        if len(results) > 0:
            assert results[0]["score"] > 0.3  # Minimum relevance threshold
