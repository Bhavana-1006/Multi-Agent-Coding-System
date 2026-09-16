"""
Curated realistic, failure-oriented bug specifications for OpenAI HumanEval problems (HumanEval/0 to HumanEval/29).
Each entry provides:
- bug: function body containing realistic logic, boundary, off-by-one, type, or algorithm bug
- error_type: categories of error (logical_error, off_by_one, type_error, boundary_error, etc.)
- buggy_error: descriptive error expectation
- repair_hint: pedagogical guidance for automated repair agents
"""

from typing import Dict, Any

HUMANEVAL_CURATED_BUGS: Dict[str, Dict[str, Any]] = {
    'HumanEval/0': {
        'bug': '''    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold / 2:
                    return True
    return False''',
        'error_type': ['logical_error', 'boundary_error'],
        'buggy_error': 'AssertionError: Fails when elements are closer than threshold but not threshold / 2',
        'repair_hint': 'Check distance < threshold directly without halving threshold.'
    },
    'HumanEval/1': {
        'bug': '''    result = []
    current_string = []
    current_depth = 0
    for c in paren_string:
        if c == '(':
            current_depth += 1
            current_string.append(c)
        elif c == ')':
            current_depth -= 1
            current_string.append(c)
            if current_depth == 1:
                result.append(''.join(current_string))
                current_string = []
    return result''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Emits group at depth 1 instead of depth 0',
        'repair_hint': 'Flush current_string when current_depth returns to 0.'
    },
    'HumanEval/2': {
        'bug': '''    return float(int(number))''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Returns integer part instead of fractional/decimal part',
        'repair_hint': 'Return number % 1.0 or number - int(number).'
    },
    'HumanEval/3': {
        'bug': '''    balance = 0
    for op in operations:
        balance += op
        if balance <= 0:
            return True
    return False''',
        'error_type': ['boundary_error'],
        'buggy_error': 'AssertionError: Treats zero balance as strictly below zero',
        'repair_hint': 'Condition should be balance < 0, not balance <= 0.'
    },
    'HumanEval/4': {
        'bug': '''    mean = sum(numbers) / len(numbers)
    return sum(abs(x - mean) for x in numbers)''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Sums absolute deviations without dividing by N to compute mean',
        'repair_hint': 'Divide the total deviation sum by len(numbers).'
    },
    'HumanEval/5': {
        'bug': '''    if not numbers:
        return []
    result = []
    for n in numbers:
        result.append(n)
        result.append(delimeter)
    return result''',
        'error_type': ['off_by_one'],
        'buggy_error': 'AssertionError: Appends trailing delimiter after the last element',
        'repair_hint': 'Do not append delimiter after the final number.'
    },
    'HumanEval/6': {
        'bug': '''    return [1] * len(paren_string.split())''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Returns static depth 1 for all parenthesized groups',
        'repair_hint': 'Track maximum nesting depth per group dynamically.'
    },
    'HumanEval/7': {
        'bug': '''    return [x for x in strings if substring not in x]''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Inverted filter condition: excludes substring matches',
        'repair_hint': 'Use if substring in x instead of not in.'
    },
    'HumanEval/8': {
        'bug': '''    s = 0
    p = 0
    for x in numbers:
        s += x
        p *= x
    return s, p''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Multiplicative identity initialized to 0 instead of 1',
        'repair_hint': 'Initialize product variable p to 1.'
    },
    'HumanEval/9': {
        'bug': '''    return [numbers[0]] * len(numbers) if numbers else []''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Repeats first element instead of calculating prefix maximums',
        'repair_hint': 'Maintain running maximum as you iterate through the list.'
    },
    'HumanEval/10': {
        'bug': '''    if not string:
        return ""
    return string + string[::-1]''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Duplicates existing palindromic suffix',
        'repair_hint': 'Find the longest palindromic postfix and only append the reverse of the prefix before it.'
    },
    'HumanEval/11': {
        'bug': '''    return "".join("1" if x == "1" or y == "1" else "0" for x, y in zip(a, b))''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Performs bitwise OR instead of bitwise XOR',
        'repair_hint': 'XOR returns 1 only when x != y.'
    },
    'HumanEval/12': {
        'bug': '''    if not strings:
        return None
    res = strings[0]
    for s in strings:
        if len(s) >= len(res):
            res = s
    return res''',
        'error_type': ['boundary_error'],
        'buggy_error': 'AssertionError: Returns last longest string instead of first on ties',
        'repair_hint': 'Use strict inequality len(s) > len(res) to preserve the first occurrence.'
    },
    'HumanEval/13': {
        'bug': '''    return abs(a - b)''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Computes difference instead of greatest common divisor',
        'repair_hint': 'Use Euclidean algorithm while b: a, b = b, a % b.'
    },
    'HumanEval/14': {
        'bug': '''    return [string[:i] for i in range(2, len(string) + 1)]''',
        'error_type': ['off_by_one', 'boundary_error'],
        'buggy_error': 'AssertionError: Omits length-1 prefix string[:1]',
        'repair_hint': 'Range should start at 1: range(1, len(string) + 1).'
    },
    'HumanEval/15': {
        'bug': '''    return " ".join(str(i) for i in range(1, n))''',
        'error_type': ['off_by_one', 'boundary_error'],
        'buggy_error': 'AssertionError: Omits 0 at start and n at end',
        'repair_hint': 'Range should be range(n + 1).'
    },
    'HumanEval/16': {
        'bug': '''    return len(set(string))''',
        'error_type': ['case_sensitivity_error'],
        'buggy_error': 'AssertionError: Treats uppercase and lowercase characters as distinct',
        'repair_hint': 'Normalize string to lowercase with string.lower() before creating set.'
    },
    'HumanEval/17': {
        'bug': '''    note_map = {'o': 4, 'o|': 2, '.|': 0}
    return [note_map.get(x, 0) for x in music_string.split(' ') if x]''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Treats quarter note as 0 beats instead of 1 beat',
        'repair_hint': 'Map .| to 1 beat in note_map.'
    },
    'HumanEval/18': {
        'bug': '''    return string.count(substring)''',
        'error_type': ['edge_case_error', 'logical_error'],
        'buggy_error': 'AssertionError: Standard str.count misses overlapping occurrences like aaa in aaaa',
        'repair_hint': 'Iterate through all slice indices string[i:i+len(substring)] to count overlapping matches.'
    },
    'HumanEval/19': {
        'bug': '''    return " ".join(sorted(numbers.split()))''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Sorts alphabetically rather than by numerical word value',
        'repair_hint': 'Sort using key=lambda w: value_map[w].'
    },
    'HumanEval/20': {
        'bug': '''    res = None
    min_diff = float("inf")
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            diff = abs(numbers[i] - numbers[j])
            if diff < min_diff:
                min_diff = diff
                res = (numbers[i], numbers[j])
    return res''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Returns pair in discovery order instead of sorted order',
        'repair_hint': 'Return tuple sorted: (min(a, b), max(a, b)).'
    },
    'HumanEval/21': {
        'bug': '''    max_num = max(numbers)
    return [x / max_num for x in numbers]''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Divides by max instead of rescaling (x - min) / (max - min)',
        'repair_hint': 'Subtract min(numbers) from x and divide by range max - min.'
    },
    'HumanEval/22': {
        'bug': '''    return [x for x in values if isinstance(x, (int, float))]''',
        'error_type': ['type_error'],
        'buggy_error': 'AssertionError: Includes float values instead of filtering strictly to integers',
        'repair_hint': 'Filter strictly with type(x) == int to exclude floats and bools.'
    },
    'HumanEval/23': {
        'bug': '''    return len(string) - 1 if string else 0''',
        'error_type': ['off_by_one'],
        'buggy_error': 'AssertionError: Returns len(string) - 1 on non-empty strings',
        'repair_hint': 'Return len(string) directly.'
    },
    'HumanEval/24': {
        'bug': '''    return n // 2''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Returns n // 2 without verifying divisibility',
        'repair_hint': 'Find largest i < n such that n % i == 0.'
    },
    'HumanEval/25': {
        'bug': '''    import math
    factors = []
    i = 2
    while i <= int(math.isqrt(n)):
        if n % i == 0:
            factors.append(i)
            n //= i
        i += 1
    if n > 1:
        factors.append(n)
    return factors''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Advances factor counter without dividing repeated factors',
        'repair_hint': 'Use while n % i == 0 to capture multiple multiplicity factors.'
    },
    'HumanEval/26': {
        'bug': '''    return list(dict.fromkeys(numbers))''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Keeps first occurrence of duplicates instead of removing all elements occurring > 1 times',
        'repair_hint': 'Count occurrences with Counter and filter for count == 1.'
    },
    'HumanEval/27': {
        'bug': '''    return string.lower()''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Converts entire string to lowercase instead of swapping case',
        'repair_hint': 'Use string.swapcase().'
    },
    'HumanEval/28': {
        'bug': '''    return ", ".join(strings)''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Joins strings with comma delimiter instead of empty string',
        'repair_hint': 'Use "".join(strings).'
    },
    'HumanEval/29': {
        'bug': '''    return [x for x in strings if not x.startswith(prefix)]''',
        'error_type': ['logical_error'],
        'buggy_error': 'AssertionError: Inverts prefix condition: excludes matching strings',
        'repair_hint': 'Use if x.startswith(prefix) without negation.'
    }
}
