import os
import json
import pytest
from training.benchmark_loader import load_local_benchmark, get_benchmark_stats
from execution.pytest_runner import run_tests_in_sandbox

def test_dataset_files_exist():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    full_path = os.path.join(root, "data", "problems_full.json")
    train_path = os.path.join(root, "data", "train.json")
    val_path = os.path.join(root, "data", "val.json")
    test_path = os.path.join(root, "data", "test.json")

    assert os.path.exists(full_path), "problems_full.json missing"
    assert os.path.exists(train_path), "train.json missing"
    assert os.path.exists(val_path), "val.json missing"
    assert os.path.exists(test_path), "test.json missing"

def test_dataset_splits_and_stratification():
    full = load_local_benchmark(split="all")
    train = load_local_benchmark(split="train")
    val = load_local_benchmark(split="val")
    test = load_local_benchmark(split="test")

    assert len(full) == 229
    assert len(train) == 160
    assert len(val) == 35
    assert len(test) == 34

    # Check zero overlap
    train_ids = {p["task_id"] for p in train}
    val_ids = {p["task_id"] for p in val}
    test_ids = {p["task_id"] for p in test}

    assert train_ids.isdisjoint(val_ids)
    assert train_ids.isdisjoint(test_ids)
    assert val_ids.isdisjoint(test_ids)
    assert train_ids | val_ids | test_ids == {p["task_id"] for p in full}

    # Verify all splits have Easy, Medium, and Hard
    for split_data in [train, val, test]:
        stats = get_benchmark_stats(split_data)
        assert stats["difficulties"].get("Easy", 0) >= 1
        assert stats["difficulties"].get("Medium", 0) >= 1
        assert stats["difficulties"].get("Hard", 0) >= 1

def test_problem_schema_completeness():
    required_keys = [
        "task_id", "prompt", "canonical_solution", "test", "entry_point",
        "difficulty", "category", "constraints", "expected_output",
        "edge_cases", "common_errors", "test_cases"
    ]
    full = load_local_benchmark(split="all")
    valid_difficulties = {"Easy", "Medium", "Hard"}
    valid_categories = {
        "Arrays", "Strings", "Searching & Sorting", "Dynamic Programming",
        "Trees & Graphs", "Data Structures", "Math", "Recursion", "General Programming"
    }

    for prob in full:
        for k in required_keys:
            assert k in prob, f"Missing key '{k}' in {prob.get('task_id')}"
        assert prob["difficulty"] in valid_difficulties, f"Invalid difficulty: {prob['difficulty']}"
        assert prob["category"] in valid_categories, f"Invalid category: {prob['category']}"
        assert len(prob["test_cases"]) >= 1, f"Insufficient test cases in {prob['task_id']}"
        assert len(prob["edge_cases"]) >= 1, f"Insufficient edge cases in {prob['task_id']}"
        assert prob["entry_point"] in prob["canonical_solution"], f"Entry point mismatch in canonical_solution for {prob['task_id']}"

def test_failure_oriented_fields_in_benchmark():
    full = load_local_benchmark(split="all")
    buggy_subset = [p for p in full if p.get("has_buggy_solution") or p.get("buggy_solution")]
    assert len(buggy_subset) == 95
    for p in buggy_subset:
        assert p.get("buggy_solution"), f"Missing buggy_solution in {p['task_id']}"
        assert p.get("error_type"), f"Missing error_type in {p['task_id']}"
        assert p.get("buggy_error"), f"Missing buggy_error in {p['task_id']}"
        assert p.get("repair_hint"), f"Missing repair_hint in {p['task_id']}"
        assert p.get("repaired_solution"), f"Missing repaired_solution in {p['task_id']}"

# Reference implementations for all 20 problems to verify test_code correctness
REFERENCE_SOLUTIONS = {
    "is_palindrome": """
def is_palindrome(s: str) -> bool:
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]
""",
    "valid_anagram": """
from collections import Counter
def valid_anagram(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)
""",
    "length_of_longest_substring": """
def length_of_longest_substring(s: str) -> int:
    char_map = {}
    left = 0
    max_len = 0
    for right, c in enumerate(s):
        if c in char_map and char_map[c] >= left:
            left = char_map[c] + 1
        char_map[c] = right
        max_len = max(max_len, right - left + 1)
    return max_len
""",
    "compress_string": """
def compress_string(s: str) -> str:
    if not s:
        return ""
    result = []
    i = 0
    while i < len(s):
        c = s[i]
        count = 0
        while i < len(s) and s[i] == c:
            count += 1
            i += 1
        result.append(f"{c}{count}")
    return "".join(result)
""",
    "two_sum": """
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
""",
    "move_zeroes": """
def move_zeroes(nums: list[int]) -> list[int]:
    res = [x for x in nums if x != 0]
    res.extend([0] * (len(nums) - len(res)))
    return res
""",
    "max_subarray_sum": """
def max_subarray_sum(nums: list[int]) -> int:
    max_sum = current_sum = nums[0]
    for x in nums[1:]:
        current_sum = max(x, current_sum + x)
        max_sum = max(max_sum, current_sum)
    return max_sum
""",
    "max_area": """
def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_val = 0
    while left < right:
        max_val = max(max_val, min(height[left], height[right]) * (right - left))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_val
""",
    "merge_intervals": """
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for cur in intervals[1:]:
        prev = merged[-1]
        if cur[0] <= prev[1]:
            prev[1] = max(prev[1], cur[1])
        else:
            merged.append(cur)
    return merged
""",
    "trap_rain_water": """
def trap_rain_water(height: list[int]) -> int:
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    return water
""",
    "is_prime": """
def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
""",
    "fibonacci": """
def fibonacci(n: int) -> int:
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
""",
    "trailing_zeroes": """
def trailing_zeroes(n: int) -> int:
    count = 0
    while n >= 5:
        count += n // 5
        n //= 5
    return count
""",
    "binary_search": """
def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""",
    "search_rotated_array": """
def search_rotated_array(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
""",
    "median_of_two_sorted_arrays": """
def median_of_two_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    merged = sorted(nums1 + nums2)
    n = len(merged)
    if n % 2 == 1:
        return float(merged[n // 2])
    return (merged[n // 2 - 1] + merged[n // 2]) / 2.0
""",
    "valid_parentheses": """
def valid_parentheses(s: str) -> bool:
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in pairs.values():
            stack.append(char)
        elif char in pairs:
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return len(stack) == 0
""",
    "daily_temperatures": """
def daily_temperatures(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    ans = [0] * n
    stack = []
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            prev_idx = stack.pop()
            ans[prev_idx] = i - prev_idx
        stack.append(i)
    return ans
""",
    "climb_stairs": """
def climb_stairs(n: int) -> int:
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b
""",
    "coin_change": """
def coin_change(coins: list[int], amount: int) -> int:
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
"""
}

def test_all_problems_pass_with_reference_solutions():
    full = load_local_benchmark(split="all", source="custom")[:20]
    for prob in full:
        fn_name = prob["entry_point"]
        ref_code = prob.get("canonical_solution") or REFERENCE_SOLUTIONS.get(fn_name)
        assert ref_code is not None, f"Missing reference solution for {fn_name}"
        res = run_tests_in_sandbox(code=ref_code, test_code=prob["test"], timeout=5.0, entry_point=fn_name)
        assert res.passed is True, f"Problem {prob['task_id']} ({fn_name}) failed reference tests: {res.stderr or res.stdout}"
