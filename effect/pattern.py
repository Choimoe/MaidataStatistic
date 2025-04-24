import re
from typing import Callable, Dict, List, Optional, Generator, List, Sequence, TypeVar


def check_song_structure(
        song: List[Dict],
        condition_func: Callable[[Sequence[List[str]]], bool]
) -> List[int]:
    """Checks if any chart in the song meets the specified temporal root note pattern.

    Processes note data into temporal blocks preserving concurrent notes, then applies
    the condition function to detect patterns across time sequences.

    Args:
        song: List of chart dictionaries. Each chart must contain 'note_data' key with
            a list of note strings representing the musical chart.
        condition_func: Function that takes a sequence of root note groups (each group
            represents notes in the same temporal position) and returns a bool.

    Returns:
        list of chart id if any chart satisfies the condition, [] otherwise.
    """
    satisfies_number = []
    for chart in song:
        if not chart['note_data']:
            continue
        temporal_roots = process_chart(chart.get('note_data', []))
        if condition_func(temporal_roots):
            satisfies_number.append(chart['chart_number'])
    return satisfies_number


def process_chart(note_data: List[str]) -> List[List[str]]:
    """Processes raw note data into structured temporal root note groups.

    Args:
        note_data: List of note strings from a chart

    Returns:
        List of root note groups, where each group contains all roots sounding
        at the same temporal position
    """
    return [
        extract_roots(block)
        for block in split_blocks(''.join(note_data))
        if block  # Skip empty blocks
    ]


def split_blocks(notes_str: str) -> List[str]:
    """Splits concatenated note data into individual temporal blocks."""
    return [b.strip() for b in notes_str.split(',') if b.strip()]


def extract_roots(block: str) -> List[str]:
    """Extracts root notes from a single temporal block."""
    cleaned = re.sub(r'\{.*?\}|\(.*?\)', '', block).strip()
    return list(filter(None, (_get_root(n) for n in cleaned.split('/'))))


def _get_root(note: str) -> Optional[str]:
    """Extracts root note from an individual note string."""
    if not note:
        return None
    # Handle special multi-character roots (A-E series)
    if note[0] in {'A', 'B', 'C', 'D', 'E'} and len(note) >= 2:
        return f"{note[0]}{note[1]}"
    return note[0]


T = TypeVar('T')


def sliding_window(sequence: Sequence[T], window_size: int) -> Generator[Sequence[T], None, None]:
    """
    Generates sliding windows of specified size over the input sequence.

    Args:
        sequence: Input sequence to process
        window_size: Number of elements in each window

    Yields:
        Consecutive subsequences of specified window size

    Example:
        > > > list(sliding_window([1,2,3,4,5], 3))
        [[1,2,3], [2,3,4], [3,4,5]]
    """
    for i in range(len(sequence) - window_size + 1):
        yield sequence[i:i + window_size]


def check_target_pattern(temporal_roots: Sequence[List[str]], target_pattern: Sequence[str]) -> bool:
    """
    Detects consecutive target pattern across temporal positions.

    Args:
        temporal_roots: Sequence of root note groups, where each group
            represents notes in a temporal position
        target_pattern: Sequence of target note
            Example: ['1', '8', '1', '8', '1', '8', '1', '8']

    Returns:
        True if pattern is found in any N-consecutive-position window
    """

    # Early exit if not enough temporal positions
    if len(temporal_roots) < len(target_pattern):
        return False

    # Check each window of consecutive temporal positions
    for time_window in sliding_window(temporal_roots, len(target_pattern)):
        # Verify each position contains the required root(s)
        if all(
                # Check if target note exists in current time slot
                any(note == target for note in time_slot)
                for time_slot, target in zip(time_window, target_pattern)
        ):
            return True
    return False


# Usage Example
if __name__ == "__main__":
    # Test case with temporal alternation in concurrent notes
    test_song = [{'chart_number': 1, 'level': '', 'description': '', 'note_data': []}, {'chart_number': 2, 'level': '5', 'description': '-', 'note_data': ['(173){1},', '{2}3,3,', '{2}2,2,', '{2}1,1,', '{2}8,7,', '{2}6,6,', '{2}7,7,', '{2}8,8,', '{2}1,2,', '{2}3,3,', '{2}2,2,', '{2}1,1,', '{2}8,7,', '{2}6,6,', '{2}5,5,', '{2}4,3,', '{4}2,2,2,,', '{4}8,8,8,,', '{4},7,,6,', '{4}1,1,1,,', '{4},2,,3,', '{4}6,7,8,8,', '{4}1,2,3,,', '{4},2,,2,', '{4}1,8,1/8,,', '{4}8,8,8,,', '{4},7,,6,', '{4}1,1,1,,', '{4},2,,3,', '{4}6,7,8,8,', '{4}1,2,3,,', '{4},2,,2,', '{4}1,8,1/8,,', '{1}7-2[2:1],', '{4},2,,1,', '{1}8-5[2:1],', '{4},5,,4,', '{1}3-6[2:1],', '{4},6,,7,', '{1}8-5[2:1],', '{4},6,,7,', '{2}8,8,', '{4}8,7,7,,', '{2}1,1,', '{4}1,2,3,,', '{2}7,7,', '{4}6,5,4,,', '{2}2,2,', '{4}3,4,5,,', '{4}7,6,6b,,', '{4}2,3,3b,,', '{4}7,6,6b,,', '{4}1,1,2,2,', '{4}3/6,3/6,3/6,,', '{4}8,8,8,,', '{4},7,,6,', '{4}1,1,1,,', '{4},2,,3,', '{4}6,7,8,8,', '{4}1,2,3,,', '{4},2,,2,', '{4}1,8,1/8,,', '{4}8,8,8,,', '{4},7,,6,', '{4}1,1,1,,', '{4},2,,3,', '{4}6,7,8,8,', '{4}1,2,3,,', '{4}2,2,7,7,', '{4}1/7,8,1/8,,', '{1},', '{1},', '{1},']}, {'chart_number': 3, 'level': '7', 'description': '-', 'note_data': ['(173){1},', '{2}3,2,', '{2}1,8,', '{2}7,6,', '{2}5,5,', '{2}6,7,', '{2}8,1,', '{2}2,3,', '{2}4,4,', '{2}7,6,', '{2}5,4,', '{2}3,2,', '{2}1,1,', '{2}2,1,', '{2}8,7,', '{1}6<2[2:1],', '{4}1,8,2/7,,', '{4}7,8,2,1,', '{4}7,8,7,1/8,', '{4}5,7,4,2,', '{4}1,2,3,1/8,', '{4}2,3,4,5,', '{4}6,6,7,8,', '{4}7h[2:1],,,3,', '{4}1,8,2/7,,', '{4}7,8,2,1,', '{4}7,8,7,1/8,', '{4}5,7,4,2,', '{4}1,2,3,1/8,', '{4}3,2,1,8,', '{4}7,7,6,5,', '{1}5-8[2:1],', '{4}7/8,1/8,1/2,,', '{4}2/7,8,1,8,', '{4}2/6,7,8,7,', '{4}3/7,2,1,2,', '{4}3/6,5,4,5,', '{4}2/7,8,1,8,', '{4}1/8,7,2,7,', '{4}7h[4:3],2,2,2,', '{4}3,6,2,2/7,', '{4}1h[4:1],2,8h[4:1],7,', '{4}3,7h[4:1],6,,', '{1}4h[4:3],', '{1}2>5[2:1],', '{4}6,5,6,5,', '{4}3,4,3,4,', '{4}2h[2:1],,3,3,', '{4}6,7,8,,', '{1}8-5[2:1],', '{384},4-1[384:191]/5-8[384:191],,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,', '{384}7,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,6,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,7>2[384:193],', '{1},', '{4}1,7,2b/7b,,', '{4}7,8,2,1,', '{4}7,8,7,1/8,', '{4}5,7,4,2,', '{4}1,2,1,1/8,', '{4}2,3,4,5,', '{4}6,6,7,8,', '{4}7h[2:1],,,3,', '{4}1,8,2/7,,', '{4}7,8,2,1,', '{4}7,8,7,1/8,', '{4}5,7,4,2,', '{4}1,2,1,1/8,', '{4}3,2,1,8,', '{4}7,7,6,5,', '{1}5-8[2:1],', '{4}2/7,2/6,3/6,1b/8b,', '{1},', '{1},', '{1},']}, {'chart_number': 4, 'level': '8', 'description': '-', 'note_data': ['(173){1},', '{4}1,1,2,2,', '{4}3,3,4,5,', '{4}8,8,7,7,', '{4}6,6,5,4,', '{4}2,2,3,3,', '{4}4,4,5,6,', '{4}7,7,6,6,', '{4}5,5,4,3,', '{4}1,7,5,3,', '{4}1,7,5,3,', '{4}8,2,4,6,', '{4}8,2,4,6,', '{4}1,6,3,8,', '{4}5,2,7,4,', '{4}8,3,6,1,', '{4}4,2/7,1b/4,,', '{8}8,,7,,1,,2,2,', '{8},8,,7,7,,1b,,', '{8}3,,2,,1,,1,6,', '{8},7,,8,8,,1b,,', '{4}4h[4:1],3h[4:1],2h[4:1],1h[4:1],', '{4}8h[4:1],7h[4:1],6h[4:1],5h[4:1],', '{8}3,,,6,,,5-1[2:1],,', '{1},', '{8}1,,2,,8,,7,7,', '{8},1,,2,2,,8,,', '{8}6,,7,,8,,8,3,', '{8},2,,1/7,2/8,,,,', '{4}4h[4:1],6h[4:1],2h[4:1],8h[4:1],', '{4}1h[4:1],7h[4:1],3h[4:1],5h[4:1],', '{4}8h[4:1],2,4h[4:1],6,', '{1}8-4[2:1],', '{8}6,5,,5,,5,6,,', '{8}3,4,,4,,4,3,4,', '{8},4,,5,,6,,7,', '{8},6,,5,,4,,3,', '{8}3,4,,4,,4,3,,', '{8}6,5,,5,,5,6,5,', '{8},5,,4,,3,,2,', '{8},3,,4,,5,,6,', '{4}7h[4:1],6,2h[4:1],3,', '{4}7-2[4:1],6,,3,', '{4}2h[4:1],3,7h[4:1],6,', '{4}2-7[4:1],3,,6,', '{8}3,3,3,,6,6,6,,', '{2}2-5[4:1],7-4[4:1],', '{4}1,2,6,5,', '{8}8,,7,,3,,4,2,', '{8}2-5[2:1],2,,,,,,7,', '{8}7-4[2:1],7,,,,,,,', '{8}1,2,1,2,8,7,8,7>2[4:1],', '{8},,,3<6[4:1],,,,7-3[4:1],', '{8},,,,,2,2,2,', '{8}1,,2,,8,,7,7,', '{8},1,,2,2,,8b,,', '{8}6,,7,,8,,8,3,', '{8},2,,1,1,,8b,,', '{4}5h[4:1],6h[4:1],7h[4:1],8h[4:1],', '{4}1h[4:1],2h[4:1],3h[4:1],4h[4:1],', '{8}6,,,3,,,4-8[2:1],,', '{1},', '{8}8,,7,,1,,2,2,', '{8},8,,7,7,,1,,', '{8}3,,2,,1,,1,6,', '{8},7,,2/8,1/7,,,,', '{4}5h[4:1],3h[4:1],7h[4:1],1h[4:1],', '{4}8h[4:1],2h[4:1],6h[4:1],4h[4:1],', '{4}1h[4:1],7,5h[4:1],3,', '{4}1,2/7h[2:1],6,2,', '{1}8-5[2:1],', '{1},', '{1},']}, {'chart_number': 5, 'level': '9+', 'description': '-', 'note_data': ['(173){1},', '{4}1h[1:2],2,5,8,', '{4}3,6,7,2,', '{4}8h[1:2],7,4,1,', '{4}6,3,2,7,', '{4}4h[1:2],3,8,5,', '{4}2,7,5,3,', '{4}5h[1:2],6,1,4,', '{4}7,2,4,6-2[2:1],', '{4},1,8,7/8>3[2:1],', '{4}6,5,4,3/2-7[2:1],', '{4},8,1,2/1<6[2:1],', '{4}3,4,5,6/7-2[2:1],', '{4},1,8,7/8>3[2:1],', '{4}6,5,4,5-8[2:1],', '{1},', '{4}2/6,3/7,1b/5b,,', '{8}2/6,,4/8,,2/7,,3h[8:3],2,', '{8},5,,8,1,1,1b,,', '{8}5h[4:1]/6,,3,,1h[2:1]/2,,8,8,', '{8},7,,6,5,5,5b,,', '{4}1/5,4/8,3/7,2/6,', '{8}1/5,,3/7,,1/5,,8,8,', '{8}8,,,1,,5,4-7[8:1],,', '{4}5-2[8:1],3-8[8:1],6-1[8:1],,', '{8}2/6,,4/8,,2/7,,3h[8:3],2,', '{8},5,,8,1,1,1b,,', '{8}5h[2:1]/6,,3,,1h[2:1],,8,8,', '{8},7,,6,5,5,5b,,', '{4}1/5,4/8,3/7,2/6,', '{8}1/5,,3/7,,1/5,,8,8,', '{8}8,,,3/6,,3,2/3,,', '{8}7,,6/7,,3,4,3,4,', '{8}4,5-1[8:1],,,,8,7,8,', '{8}8,1-4[8:1],,,,5,5,6,', '{8},6,,6,,7,6,7,', '{8},8,,8,,8,1,8,', '{8}7,6-2[8:1],,,,1,8,1,', '{8}1,2-7[8:1],,,,6,6,5,', '{8},5,,5,,4,5,4-7[8:1],', '{8},2-5[8:1],,8-4[8:1],,1-5[8:1],,,', '{8}1,1,1,,7,7,7,,', '{8}3,3,3,,5,5,5,,', '{8}2,2,2,,8,8,8,1,', '{8},2/6,,4/8,,1,1,,', '{8}3,2,3,2,4,3,4,3,', '{8},7,7,,1/5,,3/7,,', '{8}6,6,6,,4,4,4,,', '{8}5,5,5,2,1/2,,1/8,,', '{4}6-1[8:1],2-5[8:1],,,', '{4}8-3[8:1],4-7[8:1],,,', '{4}1-4[8:1],5-8[8:1],,1,', '{4}7<4[8:1],8>3[8:1],1-4[8:1],5-8[2:1],', '{1},', '{8}2b/6b,,4b/8b,,2b/7b,,3h[8:3],2,', '{8},5,,8,1,1,1b,,', '{8}5h[2:1]/6,,3,,1h[2:1],,8,8,', '{8},7,,6,5,5,5b,,', '{4}1/5,4/8,3/7,2/6,', '{8}1/5,,3/7,,1/5,,8,8,', '{8}8,,,1,,5,4-7[8:1],,', '{4}5-2[8:1],3-8[8:1],6-1[8:1],,', '{8}2/6,,4/8,,2/7,,3h[8:3],2,', '{8},5,,8,1,1,1b,,', '{8}5h[2:1]/6,,3,,1h[2:1],,8,8,', '{8},7,,6,5,5,5b,,', '{4}1/5b,4/8b,3/7b,2/6b,', '{8}1/5b,,3/7b,,1/5b,,8,8,', '{4}8,1/8,3,2/3,', '{8}4/5,,6/7,,3,4,3,4,', '{1},', '{1},', '{1},']}, {'chart_number': 6, 'level': '', 'description': '', 'note_data': []}]

    target_pattern = ['1', '8', '1', '8', '1', '8', '1', '8']

    result = check_song_structure(
        test_song,
        lambda roots: check_target_pattern(roots, target_pattern)
    )

    print(result)  # True
import re
from typing import Callable, Dict, List, Optional, Generator, List, Sequence, TypeVar


def check_song_structure(
        song: List[Dict],
        condition_func: Callable[[Sequence[List[str]]], bool]
) -> List[int]:
    """Checks if any chart in the song meets the specified temporal root note pattern.

    Processes note data into temporal blocks preserving concurrent notes, then applies
    the condition function to detect patterns across time sequences.

    Args:
        song: List of chart dictionaries. Each chart must contain 'note_data' key with
            a list of note strings representing the musical chart.
        condition_func: Function that takes a sequence of root note groups (each group
            represents notes in the same temporal position) and returns a bool.

    Returns:
        list of chart id if any chart satisfies the condition, [] otherwise.
    """
    satisfies_number = []
    for chart in song:
        if not chart['note_data']:
            continue
        temporal_roots = process_chart(chart.get('note_data', []))
        if condition_func(temporal_roots):
            satisfies_number.append(chart['chart_number'])
    return satisfies_number


def process_chart(note_data: List[str]) -> List[List[str]]:
    """Processes raw note data into structured temporal root note groups.

    Args:
        note_data: List of note strings from a chart

    Returns:
        List of root note groups, where each group contains all roots sounding
        at the same temporal position
    """
    return [
        extract_roots(block)
        for block in split_blocks(''.join(note_data))
        if block  # Skip empty blocks
    ]


def split_blocks(notes_str: str) -> List[str]:
    """Splits concatenated note data into individual temporal blocks."""
    return [b.strip() for b in notes_str.split(',') if b.strip()]


def extract_roots(block: str) -> List[str]:
    """Extracts root notes from a single temporal block."""
    cleaned = re.sub(r'\{.*?\}|\(.*?\)', '', block).strip()
    return list(filter(None, (_get_root(n) for n in cleaned.split('/'))))


def _get_root(note: str) -> Optional[str]:
    """Extracts root note from an individual note string."""
    if not note:
        return None
    # Handle special multi-character roots (A-E series)
    if note[0] in {'A', 'B', 'C', 'D', 'E'} and len(note) >= 2:
        return f"{note[0]}{note[1]}"
    return note[0]


T = TypeVar('T')


def sliding_window(sequence: Sequence[T], window_size: int) -> Generator[Sequence[T], None, None]:
    """
    Generates sliding windows of specified size over the input sequence.

    Args:
        sequence: Input sequence to process
        window_size: Number of elements in each window

    Yields:
        Consecutive subsequences of specified window size

    Example:
        > > > list(sliding_window([1,2,3,4,5], 3))
        [[1,2,3], [2,3,4], [3,4,5]]
    """
    for i in range(len(sequence) - window_size + 1):
        yield sequence[i:i + window_size]


def check_target_pattern(temporal_roots: Sequence[List[str]], target_pattern: Sequence[str]) -> bool:
    """
    Detects consecutive target pattern across temporal positions.

    Args:
        temporal_roots: Sequence of root note groups, where each group
            represents notes in a temporal position
        target_pattern: Sequence of target note
            Example: ['1', '8', '1', '8', '1', '8', '1', '8']

    Returns:
        True if pattern is found in any N-consecutive-position window
    """

    # Early exit if not enough temporal positions
    if len(temporal_roots) < len(target_pattern):
        return False

    # Check each window of consecutive temporal positions
    for time_window in sliding_window(temporal_roots, len(target_pattern)):
        # Verify each position contains the required root(s)
        if all(
                # Check if target note exists in current time slot
                any(note == target for note in time_slot)
                for time_slot, target in zip(time_window, target_pattern)
        ):
            return True
    return False


# Usage Example
if __name__ == "__main__":
    # Test case with temporal alternation in concurrent notes
    test_song = [{'chart_number': 1, 'level': '', 'description': '', 'note_data': []}, {'chart_number': 2, 'level': '5', 'description': '-', 'note_data': ['(173){1},', '{2}3,3,', '{2}2,2,', '{2}1,1,', '{2}8,7,', '{2}6,6,', '{2}7,7,', '{2}8,8,', '{2}1,2,', '{2}3,3,', '{2}2,2,', '{2}1,1,', '{2}8,7,', '{2}6,6,', '{2}5,5,', '{2}4,3,', '{4}2,2,2,,', '{4}8,8,8,,', '{4},7,,6,', '{4}1,1,1,,', '{4},2,,3,', '{4}6,7,8,8,', '{4}1,2,3,,', '{4},2,,2,', '{4}1,8,1/8,,', '{4}8,8,8,,', '{4},7,,6,', '{4}1,1,1,,', '{4},2,,3,', '{4}6,7,8,8,', '{4}1,2,3,,', '{4},2,,2,', '{4}1,8,1/8,,', '{1}7-2[2:1],', '{4},2,,1,', '{1}8-5[2:1],', '{4},5,,4,', '{1}3-6[2:1],', '{4},6,,7,', '{1}8-5[2:1],', '{4},6,,7,', '{2}8,8,', '{4}8,7,7,,', '{2}1,1,', '{4}1,2,3,,', '{2}7,7,', '{4}6,5,4,,', '{2}2,2,', '{4}3,4,5,,', '{4}7,6,6b,,', '{4}2,3,3b,,', '{4}7,6,6b,,', '{4}1,1,2,2,', '{4}3/6,3/6,3/6,,', '{4}8,8,8,,', '{4},7,,6,', '{4}1,1,1,,', '{4},2,,3,', '{4}6,7,8,8,', '{4}1,2,3,,', '{4},2,,2,', '{4}1,8,1/8,,', '{4}8,8,8,,', '{4},7,,6,', '{4}1,1,1,,', '{4},2,,3,', '{4}6,7,8,8,', '{4}1,2,3,,', '{4}2,2,7,7,', '{4}1/7,8,1/8,,', '{1},', '{1},', '{1},']}, {'chart_number': 3, 'level': '7', 'description': '-', 'note_data': ['(173){1},', '{2}3,2,', '{2}1,8,', '{2}7,6,', '{2}5,5,', '{2}6,7,', '{2}8,1,', '{2}2,3,', '{2}4,4,', '{2}7,6,', '{2}5,4,', '{2}3,2,', '{2}1,1,', '{2}2,1,', '{2}8,7,', '{1}6<2[2:1],', '{4}1,8,2/7,,', '{4}7,8,2,1,', '{4}7,8,7,1/8,', '{4}5,7,4,2,', '{4}1,2,3,1/8,', '{4}2,3,4,5,', '{4}6,6,7,8,', '{4}7h[2:1],,,3,', '{4}1,8,2/7,,', '{4}7,8,2,1,', '{4}7,8,7,1/8,', '{4}5,7,4,2,', '{4}1,2,3,1/8,', '{4}3,2,1,8,', '{4}7,7,6,5,', '{1}5-8[2:1],', '{4}7/8,1/8,1/2,,', '{4}2/7,8,1,8,', '{4}2/6,7,8,7,', '{4}3/7,2,1,2,', '{4}3/6,5,4,5,', '{4}2/7,8,1,8,', '{4}1/8,7,2,7,', '{4}7h[4:3],2,2,2,', '{4}3,6,2,2/7,', '{4}1h[4:1],2,8h[4:1],7,', '{4}3,7h[4:1],6,,', '{1}4h[4:3],', '{1}2>5[2:1],', '{4}6,5,6,5,', '{4}3,4,3,4,', '{4}2h[2:1],,3,3,', '{4}6,7,8,,', '{1}8-5[2:1],', '{384},4-1[384:191]/5-8[384:191],,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,', '{384}7,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,6,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,7>2[384:193],', '{1},', '{4}1,7,2b/7b,,', '{4}7,8,2,1,', '{4}7,8,7,1/8,', '{4}5,7,4,2,', '{4}1,2,1,1/8,', '{4}2,3,4,5,', '{4}6,6,7,8,', '{4}7h[2:1],,,3,', '{4}1,8,2/7,,', '{4}7,8,2,1,', '{4}7,8,7,1/8,', '{4}5,7,4,2,', '{4}1,2,1,1/8,', '{4}3,2,1,8,', '{4}7,7,6,5,', '{1}5-8[2:1],', '{4}2/7,2/6,3/6,1b/8b,', '{1},', '{1},', '{1},']}, {'chart_number': 4, 'level': '8', 'description': '-', 'note_data': ['(173){1},', '{4}1,1,2,2,', '{4}3,3,4,5,', '{4}8,8,7,7,', '{4}6,6,5,4,', '{4}2,2,3,3,', '{4}4,4,5,6,', '{4}7,7,6,6,', '{4}5,5,4,3,', '{4}1,7,5,3,', '{4}1,7,5,3,', '{4}8,2,4,6,', '{4}8,2,4,6,', '{4}1,6,3,8,', '{4}5,2,7,4,', '{4}8,3,6,1,', '{4}4,2/7,1b/4,,', '{8}8,,7,,1,,2,2,', '{8},8,,7,7,,1b,,', '{8}3,,2,,1,,1,6,', '{8},7,,8,8,,1b,,', '{4}4h[4:1],3h[4:1],2h[4:1],1h[4:1],', '{4}8h[4:1],7h[4:1],6h[4:1],5h[4:1],', '{8}3,,,6,,,5-1[2:1],,', '{1},', '{8}1,,2,,8,,7,7,', '{8},1,,2,2,,8,,', '{8}6,,7,,8,,8,3,', '{8},2,,1/7,2/8,,,,', '{4}4h[4:1],6h[4:1],2h[4:1],8h[4:1],', '{4}1h[4:1],7h[4:1],3h[4:1],5h[4:1],', '{4}8h[4:1],2,4h[4:1],6,', '{1}8-4[2:1],', '{8}6,5,,5,,5,6,,', '{8}3,4,,4,,4,3,4,', '{8},4,,5,,6,,7,', '{8},6,,5,,4,,3,', '{8}3,4,,4,,4,3,,', '{8}6,5,,5,,5,6,5,', '{8},5,,4,,3,,2,', '{8},3,,4,,5,,6,', '{4}7h[4:1],6,2h[4:1],3,', '{4}7-2[4:1],6,,3,', '{4}2h[4:1],3,7h[4:1],6,', '{4}2-7[4:1],3,,6,', '{8}3,3,3,,6,6,6,,', '{2}2-5[4:1],7-4[4:1],', '{4}1,2,6,5,', '{8}8,,7,,3,,4,2,', '{8}2-5[2:1],2,,,,,,7,', '{8}7-4[2:1],7,,,,,,,', '{8}1,2,1,2,8,7,8,7>2[4:1],', '{8},,,3<6[4:1],,,,7-3[4:1],', '{8},,,,,2,2,2,', '{8}1,,2,,8,,7,7,', '{8},1,,2,2,,8b,,', '{8}6,,7,,8,,8,3,', '{8},2,,1,1,,8b,,', '{4}5h[4:1],6h[4:1],7h[4:1],8h[4:1],', '{4}1h[4:1],2h[4:1],3h[4:1],4h[4:1],', '{8}6,,,3,,,4-8[2:1],,', '{1},', '{8}8,,7,,1,,2,2,', '{8},8,,7,7,,1,,', '{8}3,,2,,1,,1,6,', '{8},7,,2/8,1/7,,,,', '{4}5h[4:1],3h[4:1],7h[4:1],1h[4:1],', '{4}8h[4:1],2h[4:1],6h[4:1],4h[4:1],', '{4}1h[4:1],7,5h[4:1],3,', '{4}1,2/7h[2:1],6,2,', '{1}8-5[2:1],', '{1},', '{1},']}, {'chart_number': 5, 'level': '9+', 'description': '-', 'note_data': ['(173){1},', '{4}1h[1:2],2,5,8,', '{4}3,6,7,2,', '{4}8h[1:2],7,4,1,', '{4}6,3,2,7,', '{4}4h[1:2],3,8,5,', '{4}2,7,5,3,', '{4}5h[1:2],6,1,4,', '{4}7,2,4,6-2[2:1],', '{4},1,8,7/8>3[2:1],', '{4}6,5,4,3/2-7[2:1],', '{4},8,1,2/1<6[2:1],', '{4}3,4,5,6/7-2[2:1],', '{4},1,8,7/8>3[2:1],', '{4}6,5,4,5-8[2:1],', '{1},', '{4}2/6,3/7,1b/5b,,', '{8}2/6,,4/8,,2/7,,3h[8:3],2,', '{8},5,,8,1,1,1b,,', '{8}5h[4:1]/6,,3,,1h[2:1]/2,,8,8,', '{8},7,,6,5,5,5b,,', '{4}1/5,4/8,3/7,2/6,', '{8}1/5,,3/7,,1/5,,8,8,', '{8}8,,,1,,5,4-7[8:1],,', '{4}5-2[8:1],3-8[8:1],6-1[8:1],,', '{8}2/6,,4/8,,2/7,,3h[8:3],2,', '{8},5,,8,1,1,1b,,', '{8}5h[2:1]/6,,3,,1h[2:1],,8,8,', '{8},7,,6,5,5,5b,,', '{4}1/5,4/8,3/7,2/6,', '{8}1/5,,3/7,,1/5,,8,8,', '{8}8,,,3/6,,3,2/3,,', '{8}7,,6/7,,3,4,3,4,', '{8}4,5-1[8:1],,,,8,7,8,', '{8}8,1-4[8:1],,,,5,5,6,', '{8},6,,6,,7,6,7,', '{8},8,,8,,8,1,8,', '{8}7,6-2[8:1],,,,1,8,1,', '{8}1,2-7[8:1],,,,6,6,5,', '{8},5,,5,,4,5,4-7[8:1],', '{8},2-5[8:1],,8-4[8:1],,1-5[8:1],,,', '{8}1,1,1,,7,7,7,,', '{8}3,3,3,,5,5,5,,', '{8}2,2,2,,8,8,8,1,', '{8},2/6,,4/8,,1,1,,', '{8}3,2,3,2,4,3,4,3,', '{8},7,7,,1/5,,3/7,,', '{8}6,6,6,,4,4,4,,', '{8}5,5,5,2,1/2,,1/8,,', '{4}6-1[8:1],2-5[8:1],,,', '{4}8-3[8:1],4-7[8:1],,,', '{4}1-4[8:1],5-8[8:1],,1,', '{4}7<4[8:1],8>3[8:1],1-4[8:1],5-8[2:1],', '{1},', '{8}2b/6b,,4b/8b,,2b/7b,,3h[8:3],2,', '{8},5,,8,1,1,1b,,', '{8}5h[2:1]/6,,3,,1h[2:1],,8,8,', '{8},7,,6,5,5,5b,,', '{4}1/5,4/8,3/7,2/6,', '{8}1/5,,3/7,,1/5,,8,8,', '{8}8,,,1,,5,4-7[8:1],,', '{4}5-2[8:1],3-8[8:1],6-1[8:1],,', '{8}2/6,,4/8,,2/7,,3h[8:3],2,', '{8},5,,8,1,1,1b,,', '{8}5h[2:1]/6,,3,,1h[2:1],,8,8,', '{8},7,,6,5,5,5b,,', '{4}1/5b,4/8b,3/7b,2/6b,', '{8}1/5b,,3/7b,,1/5b,,8,8,', '{4}8,1/8,3,2/3,', '{8}4/5,,6/7,,3,4,3,4,', '{1},', '{1},', '{1},']}, {'chart_number': 6, 'level': '', 'description': '', 'note_data': []}]

    target_pattern = ['1', '8', '1', '8', '1', '8', '1', '8']

    result = check_song_structure(
        test_song,
        lambda roots: check_target_pattern(roots, target_pattern)
    )

    print(result)
