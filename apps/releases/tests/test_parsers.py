"""
Tests for JUnit XML parser.
"""

import pytest
from apps.releases.parsers import (
    parse_junit_xml,
    validate_junit_xml,
    generate_test_fingerprint,
    normalize_traceback,
    JUnitParserError,
)


# ==================== Fixtures ====================

@pytest.fixture
def simple_junit_xml():
    """Simple valid JUnit XML with one test suite."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="pytest" tests="3" failures="1" errors="0" skipped="1" time="1.5">
  <testcase classname="test_math" name="test_add" time="0.1"/>
  <testcase classname="test_math" name="test_subtract" time="0.2">
    <failure message="AssertionError">Expected 5, got 4</failure>
  </testcase>
  <testcase classname="test_math" name="test_multiply" time="0.1">
    <skipped message="Skipped on CI"/>
  </testcase>
</testsuite>'''


@pytest.fixture
def multi_suite_junit_xml():
    """JUnit XML with multiple test suites (testsuites root)."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="unit" tests="2" failures="0" time="0.5">
    <testcase classname="test_a" name="test_one" time="0.2"/>
    <testcase classname="test_a" name="test_two" time="0.3"/>
  </testsuite>
  <testsuite name="integration" tests="1" failures="1" time="2.0">
    <testcase classname="test_b" name="test_api" time="2.0">
      <error message="ConnectionError">Connection refused</error>
    </testcase>
  </testsuite>
</testsuites>'''


@pytest.fixture
def junit_with_properties():
    """JUnit XML with properties at suite and test case level."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="with_props" tests="1" time="0.1">
  <properties>
    <property name="os" value="linux"/>
    <property name="python" value="3.12"/>
  </properties>
  <testcase classname="test_config" name="test_env" time="0.1">
    <properties>
      <property name="env" value="staging"/>
    </properties>
  </testcase>
</testsuite>'''


@pytest.fixture
def junit_with_output():
    """JUnit XML with system-out and system-err."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="with_output" tests="1" time="0.1">
  <testcase classname="test_io" name="test_print" time="0.1">
    <system-out>Hello stdout</system-out>
    <system-err>Warning: deprecated</system-err>
  </testcase>
</testsuite>'''


@pytest.fixture
def junit_with_xfail():
    """JUnit XML with pytest xfail/xpass markers."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="xfail" tests="2" time="0.2">
  <testcase classname="test_flaky" name="test_known_fail" time="0.1">
    <properties>
      <property name="xfail" value="true"/>
      <property name="xfail_reason" value="Known bug #123"/>
    </properties>
  </testcase>
  <testcase classname="test_flaky" name="test_unexpected_pass" time="0.1">
    <failure message="XPASS">Unexpectedly passed</failure>
    <properties>
      <property name="xfail" value="true"/>
    </properties>
  </testcase>
</testsuite>'''


# ==================== Parser Tests ====================

class TestParseJUnitXml:
    """Tests for parse_junit_xml function."""

    def test_parse_simple_xml(self, simple_junit_xml):
        result = parse_junit_xml(simple_junit_xml)

        assert result.total_tests == 3
        assert result.passed_tests == 1
        assert result.failed_tests == 1
        assert result.skipped_tests == 1
        assert result.error_tests == 0
        assert abs(result.total_duration - 0.4) < 0.01  # 0.1 + 0.2 + 0.1

        # Check test suites
        assert len(result.test_suites) == 1
        suite = result.test_suites[0]
        assert suite.name == 'pytest'
        assert len(suite.test_cases) == 3

    def test_parse_multi_suite(self, multi_suite_junit_xml):
        result = parse_junit_xml(multi_suite_junit_xml)

        assert result.total_tests == 3
        assert result.passed_tests == 2
        assert result.failed_tests == 0
        assert result.error_tests == 1
        assert len(result.test_suites) == 2

        # Check first suite
        unit = result.test_suites[0]
        assert unit.name == 'unit'
        assert unit.passed_tests == 2

        # Check second suite
        integration = result.test_suites[1]
        assert integration.name == 'integration'
        assert integration.error_tests == 1

    def test_parse_with_properties(self, junit_with_properties):
        result = parse_junit_xml(junit_with_properties)

        suite = result.test_suites[0]
        assert suite.properties == {'os': 'linux', 'python': '3.12'}

        tc = suite.test_cases[0]
        assert tc.properties == {'env': 'staging'}

    def test_parse_with_output(self, junit_with_output):
        result = parse_junit_xml(junit_with_output)

        tc = result.test_suites[0].test_cases[0]
        assert 'STDOUT:\nHello stdout\n' in tc.output
        assert 'STDERR:\nWarning: deprecated\n' in tc.output

    def test_parse_xfail_xpass(self, junit_with_xfail):
        result = parse_junit_xml(junit_with_xfail)

        suite = result.test_suites[0]
        tc1 = suite.test_cases[0]  # xpass (passed but marked xfail=true -> unexpectedly passed)
        tc2 = suite.test_cases[1]  # xfail (failed and marked xfail=true -> expected failure)

        # tc1: no failure element, so passed + xfail=true -> xpass
        assert tc1.status == 'xpass'
        # tc2: has failure element + xfail=true -> xfail
        assert tc2.status == 'xfail'

    def test_test_case_details(self, simple_junit_xml):
        result = parse_junit_xml(simple_junit_xml)
        tc = result.test_suites[0].test_cases[1]  # The failed one

        assert tc.classname == 'test_math'
        assert tc.name == 'test_subtract'
        assert tc.status == 'failed'
        assert tc.message == 'AssertionError'
        assert 'Expected 5, got 4' in tc.traceback

    def test_empty_xml_raises(self):
        with pytest.raises(JUnitParserError, match='Empty XML'):
            parse_junit_xml('')

    def test_invalid_xml_raises(self):
        with pytest.raises(JUnitParserError, match='Invalid XML'):
            parse_junit_xml('<not>valid</xml>')

    def test_size_limit(self):
        large_xml = '<testsuite name="x" tests="1"><testcase name="t"/></testsuite>' * 10000
        with pytest.raises(JUnitParserError, match='exceeds limit'):
            parse_junit_xml(large_xml, max_size_mb=0.001)  # Tiny limit


class TestValidateJUnitXml:
    """Tests for validate_junit_xml function."""

    def test_valid_xml(self, simple_junit_xml):
        is_valid, error = validate_junit_xml(simple_junit_xml)
        assert is_valid is True
        assert error == ''

    def test_invalid_xml(self):
        is_valid, error = validate_junit_xml('not xml')
        assert is_valid is False
        assert 'XML parse error' in error

    def test_no_testsuite(self):
        xml = '<root><child/></root>'
        is_valid, error = validate_junit_xml(xml)
        assert is_valid is False
        assert 'No testsuite elements found' in error


# ==================== Fingerprinting Tests ====================

class TestFingerprinting:
    """Tests for test fingerprint generation."""

    def test_same_test_same_fingerprint(self):
        fp1 = generate_test_fingerprint('test_math', 'test_add', '')
        fp2 = generate_test_fingerprint('test_math', 'test_add', '')
        assert fp1 == fp2

    def test_different_test_different_fingerprint(self):
        fp1 = generate_test_fingerprint('test_math', 'test_add', '')
        fp2 = generate_test_fingerprint('test_math', 'test_subtract', '')
        assert fp1 != fp2

    def test_traceback_normalization(self):
        tb1 = 'File "/home/user/project/test_math.py", line 10, in test_add\n    assert add(2, 3) == 5'
        tb2 = 'File "/different/path/test_math.py", line 99, in test_add\n    assert add(2, 3) == 5'

        fp1 = generate_test_fingerprint('test_math', 'test_add', tb1)
        fp2 = generate_test_fingerprint('test_math', 'test_add', tb2)

        # Should be same after normalization (path and line number removed)
        assert fp1 == fp2

    def test_traceback_with_variable_values(self):
        tb1 = 'assert result == "expected_value"'
        tb2 = 'assert result == "different_value"'

        fp1 = generate_test_fingerprint('test_x', 'test_y', tb1)
        fp2 = generate_test_fingerprint('test_x', 'test_y', tb2)

        # Variable values should be normalized
        assert fp1 == fp2


class TestNormalizeTraceback:
    """Tests for traceback normalization."""

    def test_removes_file_paths(self):
        tb = 'File "/home/user/project/tests/test_math.py", line 10'
        normalized = normalize_traceback(tb)
        assert '/home/user/project/' not in normalized
        assert 'test_math.py' in normalized

    def test_removes_line_numbers(self):
        tb = 'File "test.py", line 10, in func\n    assert x == 5'
        normalized = normalize_traceback(tb)
        assert 'line 10' not in normalized

    def test_removes_memory_addresses(self):
        tb = 'Object at 0x7f8b1c0d2e30'
        normalized = normalize_traceback(tb)
        assert '0x...' in normalized

    def test_normalizes_string_values(self):
        tb = 'assert name == "john_doe"'
        normalized = normalize_traceback(tb)
        assert '"..."' in normalized

    def test_normalizes_numeric_values(self):
        tb = 'assert count == 42'
        normalized = normalize_traceback(tb)
        assert '= N' in normalized


# ==================== Edge Cases ====================

class TestEdgeCases:
    """Edge case tests."""

    def test_missing_time_attribute(self):
        xml = '''<testsuite name="x" tests="1"><testcase name="t"/></testsuite>'''
        result = parse_junit_xml(xml)
        assert result.test_suites[0].test_cases[0].duration == 0.0

    def test_missing_classname(self):
        xml = '''<testsuite name="x" tests="1"><testcase name="t"/></testsuite>'''
        result = parse_junit_xml(xml)
        assert result.test_suites[0].test_cases[0].classname == ''

    def test_nested_testsuites(self):
        """Test deeply nested testsuite elements."""
        xml = '''<testsuites><testsuite name="a"><testsuite name="b"><testcase name="t"/></testsuite></testsuite></testsuites>'''
        result = parse_junit_xml(xml)
        # Should find nested testsuite
        assert result.total_tests >= 1

    def test_unicode_content(self):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="unicode" tests="1" time="0.1">
  <testcase classname="test" name="test_中文" time="0.1">
    <failure message="失败">错误信息: 变量值为 "测试"</failure>
  </testcase>
</testsuite>'''
        result = parse_junit_xml(xml)
        assert result.total_tests == 1
        tc = result.test_suites[0].test_cases[0]
        assert tc.name == 'test_中文'
        assert '错误信息' in tc.traceback


# Run with: pytest apps/releases/tests/test_parsers.py -v