"""
Custom JSON response handler for safe serialization of large integers.

JavaScript's Number type can only safely represent integers up to 2^53-1 (9007199254740991).
For 64-bit integers that exceed this range, we convert them to strings to prevent precision loss.
"""

import json
from typing import Any
from fastapi.responses import JSONResponse as FastAPIJSONResponse
from fastapi.encoders import jsonable_encoder

# JavaScript's safe integer range
MAX_SAFE_INTEGER = 9007199254740991  # 2^53 - 1
MIN_SAFE_INTEGER = -9007199254740991  # -(2^53 - 1)


def safe_int_encoder(obj: Any) -> Any:
    """
    Recursively encode integers that exceed JavaScript's safe integer range as strings.

    Args:
        obj: Object to encode

    Returns:
        Encoded object with large integers converted to strings
    """
    if isinstance(obj, int):
        if obj > MAX_SAFE_INTEGER or obj < MIN_SAFE_INTEGER:
            return str(obj)
        return obj
    elif isinstance(obj, dict):
        return {key: safe_int_encoder(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_int_encoder(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle Pydantic models and other objects with __dict__
        return safe_int_encoder(jsonable_encoder(obj))
    return obj


class JSONResponse(FastAPIJSONResponse):
    """
    Custom JSONResponse that safely handles 64-bit integers.

    This response class automatically converts integers that exceed JavaScript's
    safe integer range to strings, preventing precision loss on the frontend.
    """

    def render(self, content: Any) -> bytes:
        """
        Render content to JSON bytes with safe integer encoding.

        Args:
            content: Content to render

        Returns:
            JSON bytes with large integers as strings
        """
        safe_content = safe_int_encoder(content)
        return json.dumps(
            safe_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
