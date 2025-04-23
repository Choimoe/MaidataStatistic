from typing import Optional

from effect.delete import chart_delete
from parser import Parser


def custom_processor(note: str) -> Optional[str]:
    return note if 'b' not in note else None


parser = Parser('data\\maimai\\799_QZKAGOREQUIEM\\maidata.txt')


# print('\n'.join(chart_delete(parser.get_chart_by_level(6)['note_data'], 0.5)))
print('\n'.join(chart_delete(parser.get_chart_by_level(6)['note_data'], note_processor=custom_processor)))
