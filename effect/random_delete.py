import re
import random


def process_beat(beat: str, alpha: float) -> str:
    """Process a single beat's notes, removing each note with probability alpha.

    Args:
        beat (str): Input beat string containing notes separated by '/'.
        alpha (float): Probability between 0 and 1 of deleting each note.

    Returns:
        str: Processed beat string with notes removed, or empty string if no notes remain.
    """
    if not beat.strip():
        return ''
    notes = beat.split('/')
    kept_notes = []
    for note in notes:
        if random.random() >= alpha:  # Keep note with probability 1-alpha
            kept_notes.append(note.strip())
    return '/'.join(kept_notes) if kept_notes else ''


def process_notes_part(notes_part: str, alpha: float) -> str:
    """Process a comma-separated sequence of beats.

    Args:
        notes_part (str): String containing beats separated by commas (',').
        alpha (float): Probability of note deletion used in process_beat().

    Returns:
        str: Processed notes_part with each beat processed individually.
    """
    beats = notes_part.split(',')
    processed_beats = []
    for beat in beats:
        processed_beat = process_beat(beat, alpha)
        processed_beats.append(processed_beat)
    return ','.join(processed_beats)


def process_line(line: str, alpha: float) -> str:
    """Process a single line of music chart data.

    Args:
        line (str): Input line containing music notation (header + notes)
        alpha (float): Note deletion probability used in processing notes.

    Returns:
        str: Processed line with notes modified according to alpha.
    """
    # Regular expression to capture header and notes parts
    pattern = re.compile(r'((?:\(\d+\.?\d*\)|\{\d+\})*)([^(){}]*)')
    segments = pattern.findall(line)
    processed_segments = []
    for head, notes_part in segments:
        processed_notes = process_notes_part(notes_part, alpha)
        processed_segments.append(head + processed_notes)
    return ''.join(processed_segments)


def random_delete(chart_lines: list[str], alpha: float) -> list[str]:
    """Randomly delete notes from entire music chart with given probability.

    Args:
        chart_lines (list[str]): List of music chart lines to process
        alpha (float): Probability of deleting each note (0 ≤ α ≤ 1)

    Returns:
        list[str]: Processed chart lines with notes randomly removed
    """
    processed_lines = []
    for line in chart_lines:
        processed_line = process_line(line.strip(), alpha)
        processed_lines.append(processed_line)
    return processed_lines
