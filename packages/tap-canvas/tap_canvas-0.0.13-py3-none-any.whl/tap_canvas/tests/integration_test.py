"""Integration tests using environment variables."""

import os
import pytest
from tap_canvas.tap import TapCanvas


def get_config_from_env():
    """Get configuration from environment variables."""
    return {
        "api_key": os.getenv("TAP_CANVAS_API_KEY"),
        "base_url": os.getenv("TAP_CANVAS_BASE_URL"),
        "record_limit": int(os.getenv("TAP_CANVAS_RECORD_LIMIT", "0")) or None,
    }


@pytest.fixture
def config():
    """Config fixture from environment."""
    config = get_config_from_env()
    if not config["api_key"] or not config["base_url"]:
        pytest.skip("Environment variables TAP_CANVAS_API_KEY and TAP_CANVAS_BASE_URL required for integration tests")
    return config


def test_tap_can_connect(config):
    """Test that the tap can connect to Canvas API."""
    tap = TapCanvas(config=config)
    
    streams = tap.discover_streams()
    assert len(streams) > 0, "Should discover at least one stream"
    
    test_stream = None
    for stream in streams:
        if stream.name in ["courses", "users", "terms"]:
            test_stream = stream
            break
    
    assert test_stream is not None, "Should find a testable stream"
    
    records = []
    try:
        for record in test_stream.get_records(context=None):
            records.append(record)
            break  
    except Exception as e:
        pytest.fail(f"Failed to connect to Canvas API: {e}")
    
    print(f"Successfully connected to Canvas API via stream '{test_stream.name}'")


def test_record_limit_functionality(config):
    """Test that record limiting works with real API calls."""
    test_config = config.copy()
    test_config["record_limit"] = 3
    
    tap = TapCanvas(config=test_config)
    streams = tap.discover_streams()
    
    test_stream = None
    for stream in streams:
        if stream.name in ["courses", "users", "terms"]:
            test_stream = stream
            break
    
    assert test_stream is not None, "Should find a testable stream"
    
    records = list(test_stream.get_records(context=None))
    
    assert len(records) <= 3, f"Should return at most 3 records, got {len(records)}"
    
    print(f"Record limit test passed: got {len(records)} records (limit was 3)")


def test_no_record_limit(config):
    """Test behavior without record limit."""
    test_config = config.copy()
    test_config.pop("record_limit", None)
    
    tap = TapCanvas(config=test_config)
    streams = tap.discover_streams()
    
    test_stream = None
    for stream in streams:
        if stream.name in ["courses", "users", "terms"]:
            test_stream = stream
            break
    
    assert test_stream is not None, "Should find a testable stream"
    
    records = []
    count = 0
    for record in test_stream.get_records(context=None):
        records.append(record)
        count += 1
        if count >= 5:  
            break
    
    print(f"No limit test: successfully retrieved {len(records)} records without artificial limiting")


@pytest.mark.parametrize("limit", [1, 2, 5])
def test_various_record_limits(config, limit):
    """Test various record limit values."""
    test_config = config.copy()
    test_config["record_limit"] = limit
    
    tap = TapCanvas(config=test_config)
    streams = tap.discover_streams()
    
    test_stream = None
    for stream in streams:
        if stream.name in ["courses", "users", "terms"]:
            test_stream = stream
            break
    
    if test_stream is None:
        pytest.skip("No suitable test stream found")
    
    records = list(test_stream.get_records(context=None))
    
    assert len(records) <= limit, f"Should return at most {limit} records, got {len(records)}"
    
    print(f"Limit {limit}: got {len(records)} records")


if __name__ == "__main__":
    config = get_config_from_env()
    if config["api_key"] and config["base_url"]:
        print("Testing connection...")
        test_tap_can_connect(config)
        print("Testing record limit...")
        test_record_limit_functionality(config)
        print("All tests passed!")
    else:
        print("Set TAP_CANVAS_API_KEY and TAP_CANVAS_BASE_URL environment variables to run tests")