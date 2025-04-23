import logging


class Parser:
    """
    Parser for Mai-chart files (.maidata.txt)
    """

    def __init__(self, file_path, encoding='utf-8'):
        self.file_path = file_path
        self.encoding = encoding
        self.data = {
            'metadata': {},
            'charts': []
        }
        self._parse()

    def _parse(self):
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                lines = f.read().splitlines()
        except Exception as e:
            logging.error(f"File read error: {str(e)}")
            return

        self._parse_metadata(lines)
        self._build_charts()

    def _parse_metadata(self, lines):
        inote_buffer = []
        current_inote_key = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('&'):
                if current_inote_key:
                    self._save_inote(current_inote_key, inote_buffer)
                    current_inote_key = None
                    inote_buffer = []

                key, sep, value = line[1:].partition('=')
                if key.startswith('inote_'):
                    current_inote_key = key
                else:
                    self.data['metadata'][key] = value.strip() if value else ''
            elif line == 'E' and current_inote_key:
                self._save_inote(current_inote_key, inote_buffer)
                current_inote_key = None
                inote_buffer = []
            elif current_inote_key:
                inote_buffer.append(line.strip())

        # Handle trailing inote data
        if current_inote_key:
            self._save_inote(current_inote_key, inote_buffer)

    def _save_inote(self, key, content):
        self.data['metadata'][key] = [line for line in content if line]

    def _build_charts(self):
        chart_numbers = self._get_chart_numbers()

        for chart_num in chart_numbers:
            lv_key = f'lv_{chart_num}'
            des_key = f'des_{chart_num}'
            inote_key = f'inote_{chart_num}'

            _chart = {
                'chart_number': chart_num,
                'level': self.data['metadata'].get(lv_key, ''),
                'description': self.data['metadata'].get(des_key, ''),
                'note_data': self.data['metadata'].get(inote_key, [])
            }
            self.data['charts'].append(_chart)

    def _get_chart_numbers(self):
        chart_numbers = set()
        for key in self.data['metadata']:
            prefix, _, num_part = key.partition('_')
            if prefix in ('lv', 'des', 'inote') and num_part.isdigit():
                chart_numbers.add(int(num_part))
        return sorted(chart_numbers)

    def get_metadata(self):
        return self.data['metadata']

    def get_charts(self):
        return self.data['charts']

    def get_chart_by_level(self, chart_num):
        for _chart in self.data['charts']:
            if _chart['chart_number'] == chart_num:
                return _chart
        return None

    def validate(self):
        required_fields = ['title', 'des']
        for field in required_fields:
            if field not in self.data['metadata']:
                logging.warning(f"Missing required field: {field}")

        for _chart in self.data['charts']:
            if not _chart['note_data']:
                logging.warning(f"Chart {_chart['chart_number']} has no note data")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python parser.py <file_path>")
        sys.exit(1)

    parser = Parser(sys.argv[1])

    parser.validate()

    print("Title:", parser.get_metadata().get('title', 'N/A'))
    print("BPM:", parser.get_metadata().get('wholebpm', 'N/A'))

    # Iterate through charts
    for chart in parser.get_charts():
        print(f"\nChart {chart['chart_number']}: ")
        print(f"  Level: {chart['level']}")
        print(f"  Description: {chart['description']}")
        print(f"  Note lines: {len(chart['note_data'])}")
        print("  First 3 notes:")
        print("\n".join(chart['note_data'][:3]))
