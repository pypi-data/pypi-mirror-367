# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Internal utilities for the streaming ingest package."""

import json
from functools import wraps

from snowflake.ingest.streaming.streaming_ingest_error import StreamingIngestError


def _copy_exception_context(new_error: Exception, original_error: Exception) -> None:
    """Copy relevant context from original exception to new exception.

    This preserves important debugging information while allowing for clean
    exception replacement.

    Args:
        new_error: The new exception to copy context to
        original_error: The original exception to copy context from
    """
    if (
        hasattr(original_error, "__traceback__")
        and original_error.__traceback__ is not None
    ):
        new_error.__traceback__ = original_error.__traceback__

    if hasattr(original_error, "__cause__") and original_error.__cause__ is not None:
        new_error.__cause__ = original_error.__cause__

    if (
        hasattr(original_error, "__context__")
        and original_error.__context__ is not None
    ):
        new_error.__context__ = original_error.__context__


def _rethrow_ffi_errors_as_streaming_ingest_error(func):
    """Decorator to catch RuntimeError from FFI calls and rethrow as StreamingIngestError.

    This decorator handles the conversion of RuntimeError exceptions (typically
    from Rust FFI calls) into StreamingIngestError exceptions with proper
    error categorization and messaging, while preserving the original error location
    and context by copying relevant exception attributes.

    The RuntimeError message from the Rust FFI is expected to be in JSON format:
    {"code_name": "ErrorType", "message": "Error description"}

    Args:
        func: The function to wrap with FFI error handling

    Returns:
        The wrapped function that converts FFI RuntimeError to StreamingIngestError
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            try:
                error_data = json.loads(str(e))
                code_name = error_data.get("code_name", "Unknown")
                message = error_data.get("message", str(e))

                new_error = StreamingIngestError(code_name, message)
                _copy_exception_context(new_error, e)
                raise new_error from None
            except (json.JSONDecodeError, KeyError):
                # Fallback: re-raise original error if JSON parsing fails
                raise e

    return wrapper
