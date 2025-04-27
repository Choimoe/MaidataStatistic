from typing import Optional

from parser import Parser


import re
import random
from typing import Callable, Optional

L = 0.4  # Lower bound of the range
R = 1.3  # Upper bound of the range


def generate_hs_string():
    """
    Generates a string in the format "<HS*x>", where x is a random float
    within the global range [L, R], following a normal distribution.

    Returns:
        str: A string in the format "<HS*x>", where x is a random float.
    """
    mean = 1.0
    std_dev = (R - L) / 2

    while True:
        x = random.gauss(mean, std_dev)
        if L <= x <= R:
            break

    x = round(x, 2)
    result = f"<HS*{x}>"
    return result


def process_beat(
        beat: str,
        note_processor: Callable[[str], Optional[str]]
) -> str:
    if not beat.strip():
        return ''

    notes = beat.split('/')
    kept_notes = []

    for note in notes:
        processed = note_processor(note.strip())
        if processed is not None and processed != '':
            kept_notes.append(processed)

    return (generate_hs_string() if kept_notes else '') + ('/'.join(kept_notes) if kept_notes else '')


def process_notes_part(
    notes_part: str,
    note_processor: Callable[[str], Optional[str]]
) -> str:
    beats = notes_part.split(',')
    return ','.join(
        process_beat(beat, note_processor)
        for beat in beats
    )


def process_line(
    line: str,
    note_processor: Callable[[str], Optional[str]]
) -> str:
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

    def default_processor(note: str) -> Optional[str]:
        return note if random.random() >= alpha else None

    processor = note_processor or default_processor

    return [
        process_line(line.strip(), processor)
        for line in chart_lines
    ]


def custom_processor(note: str) -> Optional[str]:
    return note


parser = Parser('..\\data\\ゲームバラエティ\\689_CREDITS\\maidata.txt')

print('\n'.join(chart_delete(parser.get_chart_by_level(4)['note_data'], note_processor=custom_processor)))
