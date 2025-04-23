# 使用示例 --------------------------------------------------
from typing import Optional, Dict

from parser import Parser
from searcher import MaiChartScanner


# Example
def custom_matcher(file_path: str, parser: Parser) -> Optional[Dict]:
    if any(chart['level'] == '13' for chart in parser.get_charts()):
        return {'reason': 'include lv 13 chart'}

    if int(parser.get_metadata().get('wholebpm', 0)) > 200:
        return {'reason': 'high BPM'}

    return None


if __name__ == "__main__":
    scanner = MaiChartScanner(
        root_folder='data/宴会場',
        matcher=custom_matcher
    )

    if scanner.scan():
        print("\nReport:")
        print(scanner.generate_report())
    else:
        print("No Match.")
