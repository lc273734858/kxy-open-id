"""
Test script for 64-bit integer support.

This script tests the custom JSON encoder to ensure large integers
are properly serialized as strings to prevent precision loss in JavaScript.
"""

from app.utils.json_response import safe_int_encoder, MAX_SAFE_INTEGER, MIN_SAFE_INTEGER
from app.models.database import SegmentResponse


def test_safe_int_encoder():
    """Test safe integer encoding"""
    print("Testing safe_int_encoder...\n")

    # Test 1: Small integers (should remain as integers)
    test_cases_remain_int = [
        0,
        1,
        -1,
        1000,
        -1000,
        MAX_SAFE_INTEGER,
        MIN_SAFE_INTEGER,
    ]

    print("1. Small integers (should remain as int):")
    for value in test_cases_remain_int:
        result = safe_int_encoder(value)
        assert isinstance(result, int), f"Expected int, got {type(result)} for value {value}"
        print(f"   ✓ {value} -> {result} (type: {type(result).__name__})")

    # Test 2: Large integers (should convert to strings)
    test_cases_to_string = [
        MAX_SAFE_INTEGER + 1,
        MIN_SAFE_INTEGER - 1,
        9223372036854775807,  # 2^63 - 1 (max BIGINT)
        -9223372036854775808,  # -2^63 (min BIGINT)
        10000000000000000,
        -10000000000000000,
    ]

    print("\n2. Large integers (should convert to string):")
    for value in test_cases_to_string:
        result = safe_int_encoder(value)
        assert isinstance(result, str), f"Expected str, got {type(result)} for value {value}"
        assert result == str(value), f"String mismatch: {result} != {str(value)}"
        print(f"   ✓ {value} -> \"{result}\" (type: {type(result).__name__})")

    # Test 3: Dictionary with mixed values
    print("\n3. Dictionary with mixed values:")
    test_dict = {
        "small_int": 1000,
        "large_int": 10000000000000000,
        "negative_large": -10000000000000000,
        "string": "test",
        "nested": {
            "int": 2000,
            "big": 20000000000000000
        }
    }
    result = safe_int_encoder(test_dict)
    assert result["small_int"] == 1000
    assert result["large_int"] == "10000000000000000"
    assert result["negative_large"] == "-10000000000000000"
    assert result["string"] == "test"
    assert result["nested"]["int"] == 2000
    assert result["nested"]["big"] == "20000000000000000"
    print(f"   ✓ Dictionary encoded correctly:")
    print(f"     {result}")

    # Test 4: List with mixed values
    print("\n4. List with mixed values:")
    test_list = [100, 10000000000000000, -10000000000000000, "test"]
    result = safe_int_encoder(test_list)
    assert result[0] == 100
    assert result[1] == "10000000000000000"
    assert result[2] == "-10000000000000000"
    assert result[3] == "test"
    print(f"   ✓ List encoded correctly:")
    print(f"     {result}")

    # Test 5: Pydantic model (SegmentResponse)
    print("\n5. Pydantic model (SegmentResponse):")

    # Small range
    segment_small = SegmentResponse(start=1000, end=11000)
    result = safe_int_encoder(segment_small)
    assert result["start"] == 1000
    assert result["end"] == 11000
    print(f"   ✓ Small range: {result}")

    # Large range
    segment_large = SegmentResponse(
        start=9007199254740992,
        end=10007199254740991
    )
    result = safe_int_encoder(segment_large)
    assert result["start"] == "9007199254740992"
    assert result["end"] == "10007199254740991"
    print(f"   ✓ Large range: {result}")

    print("\n✅ All tests passed!")


def test_json_response_render():
    """Test JSONResponse rendering"""
    print("\n" + "="*60)
    print("Testing JSONResponse.render()...\n")

    from app.utils.json_response import JSONResponse
    import json

    # Test 1: Small integers
    print("1. Response with small integers:")
    content = {
        "code": 0,
        "msg": "Success",
        "data": {
            "start": 1000,
            "end": 11000
        }
    }
    response = JSONResponse(content=content)
    rendered = response.render(content)
    decoded = json.loads(rendered)
    assert decoded["data"]["start"] == 1000
    assert decoded["data"]["end"] == 11000
    print(f"   ✓ {rendered.decode('utf-8')}")

    # Test 2: Large integers
    print("\n2. Response with large integers:")
    content = {
        "code": 0,
        "msg": "Success",
        "data": {
            "start": 9007199254740992,
            "end": 10007199254740991
        }
    }
    response = JSONResponse(content=content)
    rendered = response.render(content)
    decoded = json.loads(rendered)
    assert decoded["data"]["start"] == "9007199254740992"
    assert decoded["data"]["end"] == "10007199254740991"
    print(f"   ✓ {rendered.decode('utf-8')}")

    print("\n✅ All JSONResponse tests passed!")


if __name__ == "__main__":
    print("="*60)
    print("64-bit Integer Support Test Suite")
    print("="*60)
    print(f"\nJavaScript safe integer range:")
    print(f"  MIN: {MIN_SAFE_INTEGER:,}")
    print(f"  MAX: {MAX_SAFE_INTEGER:,}")
    print(f"\nPython BIGINT range (signed 64-bit):")
    print(f"  MIN: -9,223,372,036,854,775,808")
    print(f"  MAX:  9,223,372,036,854,775,807")
    print("="*60 + "\n")

    test_safe_int_encoder()
    test_json_response_render()

    print("\n" + "="*60)
    print("All tests completed successfully! ✅")
    print("="*60)
