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

"""Streaming ingest error for handling errors that are specific to the streaming ingest client."""


class StreamingIngestError(Exception):
    """A class for all streaming ingest errors."""

    def __init__(self, code_name: str, message: str):
        """Initialize the StreamingIngestError.

        Args:
            code_name: The code name of the error
            message: The message of the error
        """
        super().__init__(message)
        self.code_name = code_name
        self.message = message

    def __str__(self) -> str:
        """Return the string representation of the StreamingIngestError."""
        return f"{self.code_name}: {self.message}"

    def __repr__(self) -> str:
        """Return the string representation of the StreamingIngestError."""
        return f"{self.__class__.__name__}(code_name={self.code_name!r}, message={self.message!r})"

    def __eq__(self, other: object) -> bool:
        """Check if the StreamingIngestError is equal to another object."""
        if not isinstance(other, StreamingIngestError):
            return False
        return self.code_name == other.code_name and self.message == other.message
