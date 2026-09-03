import os
import json
import urllib.request
from typing import List, Dict

HUMANEVAL_URL = "https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz"

def load_local_benchmark() -> List[Dict[str, str]]:
    """
    Loads benchmark problems from local examples or generates standard programming problems.
    """
    sample_path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_requirements.json")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    # Default set of algorithmic benchmark problems
    return [
        {
            "id": "prob_001",
            "requirement": "Write a python function `is_palindrome(s: str) -> bool` that returns True if a given string is a palindrome, ignoring casing and non-alphanumeric characters, and False otherwise.",
            "test_code": "assert is_palindrome('A man, a plan, a canal: Panama') == True\nassert is_palindrome('race a car') == False\nassert is_palindrome('') == True\nassert is_palindrome('0P') == False\nassert is_palindrome('ab_a') == True"
        },
        {
            "id": "prob_002",
            "requirement": "Write a python function `two_sum(nums: list[int], target: int) -> list[int]` that returns the 0-based indices of the two numbers such that they add up to target. Assume exactly one solution exists.",
            "test_code": "assert two_sum([2, 7, 11, 15], 9) == [0, 1]\nassert two_sum([3, 2, 4], 6) == [1, 2]\nassert two_sum([3, 3], 6) == [0, 1]"
        },
        {
            "id": "prob_003",
            "requirement": "Write a python function `valid_parentheses(s: str) -> bool` that checks if the input string containing characters '(', ')', '{', '}', '[' and ']' is valid.",
            "test_code": "assert valid_parentheses('()') == True\nassert valid_parentheses('()[]{}') == True\nassert valid_parentheses('(]') == False\nassert valid_parentheses('([)]') == False\nassert valid_parentheses('{[]}') == True\nassert valid_parentheses('') == True"
        },
        {
            "id": "prob_004",
            "requirement": "Write a python function `max_subarray_sum(nums: list[int]) -> int` that finds the contiguous subarray with the largest sum and returns its sum.",
            "test_code": "assert max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6\nassert max_subarray_sum([1]) == 1\nassert max_subarray_sum([5, 4, -1, 7, 8]) == 23\nassert max_subarray_sum([-1, -2, -3]) == -1"
        },
        {
            "id": "prob_005",
            "requirement": "Write a python function `length_of_longest_substring(s: str) -> int` that finds the length of the longest substring without repeating characters.",
            "test_code": "assert length_of_longest_substring('abcabcbb') == 3\nassert length_of_longest_substring('bbbbb') == 1\nassert length_of_longest_substring('pwwkew') == 3\nassert length_of_longest_substring('') == 0"
        }
    ]

if __name__ == "__main__":
    problems = load_local_benchmark()
    print(f"Loaded {len(problems)} benchmark problems successfully.")
