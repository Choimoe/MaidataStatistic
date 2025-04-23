from effect.random_delete import random_delete
from parser import Parser

parser = Parser('data\\maimai\\799_QZKAGOREQUIEM\\maidata.txt')


print('\n'.join(random_delete(parser.get_chart_by_level(6)['note_data'], 0.2)))
