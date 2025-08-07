from logutil.formatter import encode


def test_encode_already_valid_string():
    """Test encoding a string that already matches allowed characters."""
    valid_str = "valid_string-123.45@example"
    assert encode(valid_str) == valid_str


def test_encode_with_whitespace():
    """Test encoding a string with various whitespace characters."""
    whitespace_str = "hello  world\n\ntest\tstring"
    assert encode(whitespace_str) == '"hello world test string"'


def test_encode_with_double_quotes():
    """Test encoding a string containing double quotes."""
    double_quote_str = 'hello "world" test'
    assert encode(double_quote_str) == "'hello \"world\" test'"


def test_encode_with_single_quotes():
    """Test encoding a string containing single quotes."""
    single_quote_str = "hello 'world' test"
    assert encode(single_quote_str) == "\"hello 'world' test\""


def test_encode_with_both_quotes():
    """Test encoding a string containing both single and double quotes."""
    both_quotes_str = "hello 'world' and \"test\""
    # Should replace double quotes with single quotes
    assert encode(both_quotes_str) == "\"hello 'world' and 'test'\""


def test_encode_non_string_types():
    """Test encoding non-string values which should be JSON serialized."""
    # Integer
    assert encode(42) == "42"

    # Float
    assert encode(3.14) == "3.14"

    # Boolean
    assert encode(True) == "true"

    # None
    assert encode(None) == "null"

    # List
    assert encode(["a", "b", 1]) == '\'["a","b",1]\''

    # Dictionary
    assert encode({"key": "value"}) == '\'{"key":"value"}\''


def test_encode_json_strings():
    """Test encoding strings that are JSON formatted."""
    json_str = '{"data": "value"}'
    # Should be quoted since it contains special characters
    assert encode(json_str) == '\'{"data": "value"}\''


def test_encode_empty_string():
    """Test encoding an empty string."""
    assert encode("") == '""'
