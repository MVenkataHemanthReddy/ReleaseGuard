"""
Safe JUnit XML parser for ReleaseGuard.

Uses defusedxml to prevent XML vulnerabilities (DTD, entity expansion, billion laughs).
Supports standard JUnit XML format from pytest, surefire, and other test runners.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from defusedxml import ElementTree as ET
from defusedxml.common import EntitiesForbidden

logger = logging.getLogger(__name__)


@dataclass
class ParsedTestCase:
    """Represents a single parsed test case."""
    classname: str
    name: str
    status: str  # passed, failed, skipped, error, xfail, xpass
    duration: float = 0.0
    message: str = ''
    output: str = ''
    traceback: str = ''
    properties: dict = field(default_factory=dict)


@dataclass
class ParsedTestSuite:
    """Represents a test suite (collection of test cases)."""
    name: str
    test_cases: list[ParsedTestCase] = field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    total_duration: float = 0.0
    timestamp: Optional[str] = None
    hostname: str = ''
    properties: dict = field(default_factory=dict)


@dataclass
class ParsedJUnitResult:
    """Complete parsed JUnit XML result."""
    test_suites: list[ParsedTestSuite] = field(default_factory=list)
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    total_duration: float = 0.0


class JUnitParserError(Exception):
    """Raised when JUnit XML parsing fails."""
    pass


def parse_junit_xml(xml_content: str, max_size_mb: int = 10) -> ParsedJUnitResult:
    """
    Parse JUnit XML content safely.

    Args:
        xml_content: Raw XML string
        max_size_mb: Maximum allowed XML size in MB

    Returns:
        ParsedJUnitResult with all test suites and aggregated metrics

    Raises:
        JUnitParserError: If XML is invalid, too large, or contains forbidden constructs
    """
    # Size check
    size_bytes = len(xml_content.encode('utf-8'))
    max_bytes = max_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise JUnitParserError(f'XML size {size_bytes} bytes exceeds limit of {max_bytes} bytes')

    if not xml_content.strip():
        raise JUnitParserError('Empty XML content')

    try:
        # Parse with defusedxml - blocks DTD, external entities, entity expansion
        root = ET.fromstring(xml_content)
    except EntitiesForbidden as e:
        logger.warning('XML entity expansion blocked: %s', e)
        raise JUnitParserError('XML contains forbidden entity references')
    except ET.ParseError as e:
        logger.warning('XML parse error: %s', e)
        raise JUnitParserError(f'Invalid XML: {e}')
    except Exception as e:
        logger.exception('Unexpected XML parsing error')
        raise JUnitParserError(f'Parsing failed: {e}')

    # Handle both <testsuites> (multiple suites) and single <testsuite> root
    testsuite_elements = []
    if root.tag == 'testsuites':
        # Find all testsuite elements recursively (handles nested)
        testsuite_elements = list(root.findall('.//testsuite'))
    elif root.tag == 'testsuite':
        testsuite_elements = [root]
    else:
        # Try to find testsuite elements anywhere
        testsuite_elements = root.findall('.//testsuite')
        if not testsuite_elements:
            raise JUnitParserError('No <testsuite> elements found in XML')

    result = ParsedJUnitResult()

    for ts_elem in testsuite_elements:
        suite = _parse_testsuite(ts_elem)
        result.test_suites.append(suite)

        # Aggregate totals
        result.total_tests += suite.total_tests
        result.passed_tests += suite.passed_tests
        result.failed_tests += suite.failed_tests
        result.skipped_tests += suite.skipped_tests
        result.error_tests += suite.error_tests
        result.total_duration += suite.total_duration

    return result


def _parse_testsuite(ts_elem: ET.Element) -> ParsedTestSuite:
    """Parse a single <testsuite> element."""
    suite = ParsedTestSuite(
        name=ts_elem.get('name', 'unknown'),
        timestamp=ts_elem.get('timestamp'),
        hostname=ts_elem.get('hostname', ''),
    )

    # Parse properties if present
    props_elem = ts_elem.find('properties')
    if props_elem is not None:
        for prop in props_elem.findall('property'):
            name = prop.get('name')
            value = prop.get('value', '')
            if name:
                suite.properties[name] = value

    # Parse test cases
    for tc_elem in ts_elem.findall('testcase'):
        test_case = _parse_testcase(tc_elem)
        suite.test_cases.append(test_case)

        # Update suite counters
        suite.total_tests += 1
        suite.total_duration += test_case.duration

        if test_case.status == 'passed':
            suite.passed_tests += 1
        elif test_case.status == 'failed':
            suite.failed_tests += 1
        elif test_case.status == 'skipped':
            suite.skipped_tests += 1
        elif test_case.status == 'error':
            suite.error_tests += 1
        # xfail/xpass counted as passed/failed respectively for totals

    return suite


def _parse_testcase(tc_elem: ET.Element) -> ParsedTestCase:
    """Parse a single <testcase> element."""
    classname = tc_elem.get('classname', '')
    name = tc_elem.get('name', '')
    duration = float(tc_elem.get('time', '0') or '0')

    # Default to passed unless failure/error/skipped found
    status = 'passed'
    message = ''
    output = ''
    traceback = ''
    properties = {}

    # Check for result elements (failure, error, skipped, system-out, system-err)
    for child in tc_elem:
        tag = child.tag
        text = child.text or ''

        if tag == 'failure':
            status = 'failed'
            message = child.get('message', '')
            traceback = text
        elif tag == 'error':
            status = 'error'
            message = child.get('message', '')
            traceback = text
        elif tag == 'skipped':
            status = 'skipped'
            message = child.get('message', '')
        elif tag == 'system-out':
            output += f'STDOUT:\n{text}\n'
        elif tag == 'system-err':
            output += f'STDERR:\n{text}\n'

    # Check for properties
    props_elem = tc_elem.find('properties')
    if props_elem is not None:
        for prop in props_elem.findall('property'):
            p_name = prop.get('name')
            p_value = prop.get('value', '')
            if p_name:
                properties[p_name] = p_value

    # Handle xfail/xpass (pytest specific)
    # xfail=true means "this test is expected to fail"
    # - If it passed: XPASS (unexpectedly passed)
    # - If it failed: XFAIL (expectedly failed)
    if properties.get('xfail') == 'true':
        if status == 'passed':
            status = 'xpass'
        elif status in ('failed', 'error'):
            status = 'xfail'

    return ParsedTestCase(
        classname=classname,
        name=name,
        status=status,
        duration=duration,
        message=message,
        output=output,
        traceback=traceback,
        properties=properties,
    )


def validate_junit_xml(xml_content: str) -> tuple[bool, str]:
    """
    Quick validation without full parsing.

    Returns:
        (is_valid, error_message)
    """
    try:
        # Quick size check
        if len(xml_content) > 50 * 1024 * 1024:  # 50MB hard limit
            return False, 'XML exceeds 50MB limit'

        # Try to parse root only
        root = ET.fromstring(xml_content)

        # Check for testsuite elements
        if root.tag == 'testsuites':
            has_suite = len(root.findall('testsuite')) > 0
        elif root.tag == 'testsuite':
            has_suite = True
        else:
            has_suite = len(root.findall('.//testsuite')) > 0

        if not has_suite:
            return False, 'No testsuite elements found'

        return True, ''

    except EntitiesForbidden:
        return False, 'Forbidden entity references'
    except ET.ParseError as e:
        return False, f'XML parse error: {e}'
    except Exception as e:
        return False, f'Validation error: {e}'


# --- Fingerprinting utilities ---

import hashlib
import re

def generate_test_fingerprint(classname: str, name: str, traceback: str = '') -> str:
    """
    Generate deterministic fingerprint for a test case.

    Used for error grouping and cross-release comparison.
    Based on test identifier + normalized traceback.
    """
    # Normalize traceback: remove file paths, line numbers, variable values
    normalized_tb = normalize_traceback(traceback)

    # Create fingerprint source
    source = f'{classname}.{name}|{normalized_tb}'
    return hashlib.sha256(source.encode()).hexdigest()[:32]


def normalize_traceback(traceback: str) -> str:
    """
    Normalize traceback for fingerprinting.

    - Remove file paths (keep only filename)
    - Remove line numbers
    - Remove memory addresses
    - Normalize variable values
    """
    if not traceback:
        return ''

    lines = traceback.split('\n')
    normalized = []

    for line in lines:
        # Step 1: Extract and protect file paths in quoted strings
        file_paths = []
        def extract_file_paths(match):
            content = match.group(1)
            # Check if it looks like a file path (contains / or \ and ends with .py)
            if ('/' in content or '\\' in content) and content.endswith('.py'):
                filename = content.split('/')[-1].split('\\')[-1]
                file_paths.append(filename)
                return f'__FILE_PATH_{len(file_paths)-1}__'
            return match.group(0)

        line = re.sub(r'"([^"]*)"', extract_file_paths, line)
        line = re.sub(r"'([^']*)'", extract_file_paths, line)

        # Step 2: Normalize remaining string values
        line = re.sub(r'"[^"]*"', '"..."', line)
        line = re.sub(r"'[^']*'", "'...'", line)

        # Step 3: Restore protected file paths (just the filename)
        for i, filename in enumerate(file_paths):
            line = line.replace(f'__FILE_PATH_{i}__', filename)

        # Step 4: Remove file path prefixes if any remain (e.g., File "test_math.py")
        line = re.sub(r'File\s+"([^"]+\.py)"', r'File "\1"', line)
        line = re.sub(r"File\s+'([^']+\.py)'", r"File '\1'", line)

        # Step 5: Remove line numbers: line 123
        line = re.sub(r',\s*line\s+\d+', '', line)
        line = re.sub(r':\d+:', ':', line)

        # Step 6: Remove memory addresses
        line = re.sub(r'0x[0-9a-fA-F]+', '0x...', line)

        # Step 7: Remove specific values in common patterns
        line = re.sub(r'= \d+', '= N', line)
        line = re.sub(r'= 0x[0-9a-fA-F]+', '= 0x...', line)

        normalized.append(line)

    return '\n'.join(normalized)