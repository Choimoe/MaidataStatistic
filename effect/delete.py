import re
import random
from typing import Callable, Optional


def process_beat(
        beat: str,
        note_processor: Callable[[str], Optional[str]]
) -> str:
    """Process a single beat's notes using custom processing function.

    Args:
        beat: Input beat string containing notes separated by '/'
        note_processor: Function that takes a note and returns:
            - str: processed note to keep
            - None: indicate to delete the note
            - Empty string: will be treated as deletion

    Returns:
        Processed beat string with notes modified
    """
    if not beat.strip():
        return ''

    notes = beat.split('/')
    kept_notes = []

    for note in notes:
        processed = note_processor(note.strip())
        if processed is not None and processed != '':
            kept_notes.append(processed)

    return '/'.join(kept_notes) if kept_notes else ''


def process_notes_part(
    notes_part: str,
    note_processor: Callable[[str], Optional[str]]
) -> str:
    """Process a comma-separated sequence of beats.

    Args:
        notes_part (str): String containing beats separated by commas (',').
        note_processor: Function that takes a note deletion

    Returns:
        str: Processed notes_part with each beat processed individually.
    """
    beats = notes_part.split(',')
    return ','.join(
        process_beat(beat, note_processor)
        for beat in beats
    )


def process_line(
    line: str,
    note_processor: Callable[[str], Optional[str]]
) -> str:
    """Process a single line of music chart data.

    Args:
        line (str): Input line containing music notation (header + notes)
        note_processor: Function that takes a note deletion

    Returns:
        str: Processed line with notes modified according to alpha.
    """
    # Regular expression to capture header and notes parts
    pattern = re.compile(r'((?:\(\d+\.?\d*\)|\{\d+\})*)([^(){}]*)')
    return ''.join(
        head + process_notes_part(notes_part, note_processor)
        for head, notes_part in pattern.findall(line)
    )


def chart_delete(
    chart_lines: list[str],
    alpha: float = 0,
    *,
    note_processor: Optional[Callable[[str], Optional[str]]] = None
) -> list[str]:
    """Randomly delete notes from entire music chart with given probability or custom processing.

    Args:
        chart_lines: List of music chart lines
        alpha: Default deletion probability (0-1)
        note_processor: Optional custom processor function.
            If provided, alpha is ignored.

    Returns:
        Processed chart lines
    """

    def default_processor(note: str) -> Optional[str]:
        return note if random.random() >= alpha else None

    processor = note_processor or default_processor

    return [
        process_line(line.strip(), processor)
        for line in chart_lines
    ]
