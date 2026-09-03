import pytest
from retrieval.vector_store import knowledge_store

def test_vector_store_search():
    res = knowledge_store.search("palindrome string center", top_k=1)
    assert "palindrome" in res.lower() or "string" in res.lower()

def test_vector_store_fallback():
    res = knowledge_store.search("unknown query with xyz random terms", top_k=1)
    assert len(res) > 0
