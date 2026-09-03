import os
from typing import List, Dict

class CodeKnowledgeStore:
    def __init__(self):
        self.documents = [
            {
                "topic": "palindrome & string algorithms",
                "content": "For longest palindromic substring: expand around center in O(N^2) time and O(1) space, or Manacher's algorithm in O(N) time. Always check string length 0 and 1."
            },
            {
                "topic": "dynamic programming & memoization",
                "content": "Use functools.lru_cache(None) for top-down memoization in Python, or initialize 2D DP table dp = [[0]*(m+1) for _ in range(n+1)]."
            },
            {
                "topic": "binary search",
                "content": "Standard binary search template: left, right = 0, len(arr) - 1. While left <= right: mid = (left + right) // 2. Handle off-by-one boundary checks carefully."
            },
            {
                "topic": "graph traversal & BFS / DFS",
                "content": "Use collections.deque for BFS queues: queue.popleft(). Use set() for visited nodes to prevent cycles in graphs."
            },
            {
                "topic": "pytest unit testing patterns",
                "content": "Standard pytest function format: def test_feature(): assert func(input) == expected. Use pytest.raises(ValueError) for exception testing."
            },
            {
                "topic": "two pointers & sliding window",
                "content": "For subarray/substring problems: left = 0, maintain a frequency map (collections.Counter), expand right pointer and contract left when condition invalidates."
            },
            {
                "topic": "sorting and custom comparator",
                "content": "In Python, sorted(items, key=lambda x: (x[0], -x[1])) handles multi-level sorting. Use functools.cmp_to_key for legacy cmp functions."
            }
        ]
        
    def search(self, query: str, top_k: int = 2) -> str:
        """
        Keyword and similarity search over the knowledge base.
        """
        query_words = set(query.lower().split())
        scored_docs = []
        for doc in self.documents:
            doc_words = set((doc["topic"] + " " + doc["content"]).lower().split())
            overlap = len(query_words.intersection(doc_words))
            scored_docs.append((overlap, doc["content"]))
            
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_results = [doc[1] for doc in scored_docs[:top_k] if doc[0] > 0]
        
        if not top_results:
            top_results = [self.documents[0]["content"]]
            
        return "\n\n".join(top_results)

# Global store instance
knowledge_store = CodeKnowledgeStore()
