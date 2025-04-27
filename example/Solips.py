import random
import re
from typing import Optional

from effect.delete import chart_delete
from parser import Parser

break_alpha = 1 - 0.85
alpha = 1 - 0.72
parser = Parser('..\\data\\maimai\\11379_SOLIPS_DX\\maidata.txt')


def custom_processor(note: str) -> Optional[str]:
    if 'b' in note.lower():
        return note if random.random() >= break_alpha else None

    match = re.match(r'\d*(pp|qq|[-><^vpszwVq])', note)

    if match:
        x_part = note[:1]
        y_part = note[1:]

        candidate1 = f"{x_part}$"
        candidate2 = f"{x_part}?{y_part}"

        a = random.random()
        b = random.random()

        if a >= alpha and b >= alpha:
            return note
        elif a >= alpha:
            return candidate1
        elif b >= alpha:
            return candidate2
        else:
            return None

    return note if random.random() >= alpha else None


print('\n'.join(chart_delete(parser.get_chart_by_level(5)['note_data'], note_processor=custom_processor)))
