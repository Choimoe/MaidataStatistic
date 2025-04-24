import os
import re
import logging
from typing import Callable, Dict, List, Optional
from parser import Parser


class MaiChartMatchResult:
    """Data structure to store matching results for MAI chart files

    Attributes:
        file_path (str): Path to the analyzed chart file
        parser (Parser): Parser object used for analysis
        is_match (bool): Whether the file matched the criteria
        match_details (dict): Detailed validation information
    """

    def __init__(self,
                 file_path: str,
                 parser: Parser,
                 is_match: bool,
                 match_details: Dict):
        """Initialize match result object

        Args:
            file_path (str): Full path of the analyzed file
            parser (Parser): Parser instance used for analysis
            is_match (bool): Matching success status
            match_details (dict): Validation details dictionary
        """
        self.file_path = file_path
        self.parser = parser
        self.is_match = is_match
        self.match_details = match_details


class MaiChartScanner:
    """Tool for scanning directories and analyzing MAI chart files

    Scans specified directories for maidata.txt files and
    provides parsing & validation capabilities through matchers
    """

    def __init__(self,
                 root_folder: str = '.',
                 matcher: Optional[Callable[[str, Parser], Dict]] = None):
        """Initialize scanner with configuration

        Args:
            root_folder (str): Root directory to start scanning (default current dir)
            matcher (Callable): Custom matching function with signature:
                (file_path: str, parser: Parser) -> Dict or None
                Returns match details dict or None if not matched
        """
        self.root_folder = root_folder
        self.matcher = matcher or self.default_matcher
        self.match_results: List[MaiChartMatchResult] = []
        self._setup_logging()

    @staticmethod
    def _setup_logging():
        """Configure logging for the scanner"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    @staticmethod
    def default_matcher(file_path: str, parser: Parser) -> Optional[Dict]:
        """Default validation logic for chart files

        Consider files valid if they have non-empty content

        Args:
            file_path (str): Path to the chart file
            parser (Parser): Parser instance for the file

        Returns:
            dict: Validation details if valid, None otherwise
        """
        raw_content = parser.get_metadata().get('raw_content', '')

        # Check for empty content
        if not raw_content.strip():
            return None

        # Return basic validation info
        return {
            'validation': 'content_exists',
            'content_length': len(raw_content),
            'chart_count': len(parser.get_charts())
        }

    def scan(self) -> bool:
        """Execute the scanning and parsing process

        Performs the following steps:
        1. Recursively finds all maidata.txt files
        2. Processes each file using the configured matcher
        3. Records results in match_results attribute

        Returns:
            bool: True if any files were successfully matched, False otherwise
        """
        files = self._find_chart_files()
        if not files:
            logging.warning("No maidata.txt files found")
            return False

        success_count = 0
        for file_path in files:
            result = self._process_file(file_path)
            if result and result.is_match:
                success_count += 1

        logging.info(f"Processing completed. {success_count}/{len(files)} files matched")
        return success_count > 0

    def _find_chart_files(self) -> List[str]:
        """Recursively search for maidata.txt files in the root folder

        Traverses the directory tree starting from root_folder
        and collects paths to all maidata.txt files found

        Returns:
            List[str]: List of absolute file paths to maidata.txt files
        """
        return [
            os.path.join(root, 'maidata.txt')
            for root, _, files in os.walk(self.root_folder)
            if 'maidata.txt' in files
        ]

    def _process_file(self, file_path: str) -> Optional[MaiChartMatchResult]:
        """Process a single chart file

        Args:
            file_path (str): Absolute path to the maidata.txt file to process

        Returns:
            MaiChartMatchResult or None: Match result object if processing succeeded,
                                        None if an error occurred
        """
        try:
            parser = Parser(file_path)
            # parser.validate()

            # Preserve raw content in metadata
            parser.data['metadata']['raw_content'] = self._read_raw_content(file_path)

            # Execute matching logic
            match_result = self.matcher(file_path, parser)

            # Create result object
            result = MaiChartMatchResult(
                file_path=file_path,
                parser=parser,
                is_match=match_result is not None,
                match_details=match_result or {}
            )

            self.match_results.append(result)

            if result.is_match:
                logging.info(f"Match success: {file_path}")
            else:
                logging.debug(f"Match failed: {file_path}")

            return result

        except Exception as e:
            logging.error(f"File processing failed: {file_path} - {str(e)}")
            return None

    @staticmethod
    def _read_raw_content(file_path: str) -> str:
        """Read raw file content and remove line breaks

        Args:
            file_path (str): Path to the file to read

        Returns:
            str: File content with all newline characters (\n and \r) removed
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().replace('\n', '').replace('\r', '')

    def get_matched_results(self) -> List[MaiChartMatchResult]:
        """Get list of successfully matched results

        Returns:
            List[MaiChartMatchResult]: Filtered list containing only results
                                       where is_match is True
        """
        return [r for r in self.match_results if r.is_match]

    def generate_report(self) -> str:
        """Generate analysis report for matched chart files

        The report includes:
        - File path
        - Chart title
        - Matching details (pattern counts, note counts, etc.)

        Returns:
            str: Formatted report string or "No matches found" message
        """
        matched = self.get_matched_results()
        if not matched:
            return "No matches found"

        report = []
        for result in matched:
            report.append(f"File path: {result.file_path}")
            report.append(f"Title: {result.parser.get_metadata().get('title', 'Unknown')}")

            # Include detailed match information
            if 'pattern_matches' in result.match_details:
                count = len(result.match_details['pattern_matches'])
                report.append(f"Pattern matches: {count}")

            if chart := result.match_details.get('inote_6_data'):
                report.append(f"Difficulty 6 notes: {len(chart['note_data'])}")

            if result.match_details:
                report.append(f"Details: {result.match_details}")

            report.append("")  # Add separator between entries

        return "\n".join(report)