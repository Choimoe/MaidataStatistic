from typing import Optional, Dict

from parser import Parser
from searcher import MaiChartScanner
from effect.pattern import check_song_structure, check_target_pattern


# Example
def custom_matcher(file_path: str, parser: Parser) -> Optional[Dict]:
    for p1 in range(1, 9):
        for p2 in range(1, 9):
            if p1 != p2:
                pattern1 = str(p1)
                pattern2 = str(p2)
                target_pattern = [pattern1, pattern2] * 12
                result = check_song_structure(
                    parser.get_charts(),
                    lambda roots: check_target_pattern(roots, target_pattern)
                )
                if result:
                    return {'reason': f'{pattern1}-{pattern2}: {result}'}
    return None


if __name__ == "__main__":
    scanner = MaiChartScanner(
        root_folder='data/',
        matcher=custom_matcher
    )

    if scanner.scan():
        print("\nReport:")
        print(scanner.generate_report())
    else:
        print("No Match.")
