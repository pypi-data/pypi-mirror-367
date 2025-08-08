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

"""Streaming ingest channel for appending data into Snowflake tables."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import msgspec

from snowflake.ingest.streaming._python_ffi import (
    StreamingIngestChannel as _StreamingIngestChannel,
)
from snowflake.ingest.streaming._utils import (
    _rethrow_ffi_errors_as_streaming_ingest_error,
)
from snowflake.ingest.streaming.channel_status import ChannelStatus


class StreamingIngestChannel:
    """A channel for streaming data ingestion into Snowflake using the Snowflake Ingest SDK.

    The channel is used to ingest data into Snowflake tables in a streaming fashion. Each channel
    is associated with a specific account/database/schema/pipe combination and is created by calling
    StreamingIngestClient.open_channel() and closed by calling StreamingIngestChannel.close().

    The channel provides methods for appending single rows or batches of rows into Snowflake,
    with support for offset tokens to track ingestion progress and enable replay capabilities
    in case of failures.

    Note:
        This class should not be instantiated directly. Use StreamingIngestClient.open_channel()
        to create channel instances.

    """

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def __init__(self, channel: _StreamingIngestChannel, *, _internal: bool = False):
        """Initialize a StreamingIngestChannel instance.

        This constructor creates a Python wrapper around the underlying Rust StreamingIngestChannel
        implementation, providing a convenient Python interface for streaming data ingestion
        operations into Snowflake.

        Args:
            channel: The underlying Rust StreamingIngestChannel instance that handles the
                actual streaming ingest operations
            _internal: Internal parameter used to prevent direct instantiation of this class.
                This parameter must be set to True when creating instances internally.

        Note:
            This class should not be instantiated directly by users. Instead, use
            StreamingIngestClient.open_channel() to create channel instances, which will
            handle the proper initialization and setup of the streaming ingest channel.

        Raises:
            ValueError: If instantiated directly without the _internal parameter set to True,
                indicating improper direct instantiation

        """
        if not _internal:
            raise ValueError(
                "StreamingIngestChannel cannot be instantiated directly. "
                "Use StreamingIngestClient.open_channel() instead."
            )
        self._channel = channel
        self._serializer = msgspec.json.Encoder()

    def __del__(self) -> None:
        """Delete the channel."""
        if self._channel is not None:
            self.close()

    def append_row(
        self,
        row: Dict[str, Any],
        offset_token: Optional[str] = None,
    ) -> None:
        """Append a single row into the channel.

        Args:
            row: Dictionary representing the row data to append with keys as column names and values as column values. Values can be of the following types:
                - None: null values
                - bool: boolean values (True, False)
                - int: integer values
                - float: floating-point values
                - str: string values
                - bytes: byte strings
                - bytearray: mutable byte arrays
                - tuple: tuples of values
                - list: lists of values
                - dict: nested dictionaries
                - set: sets of values
                - frozenset: immutable sets of values
                - datetime.datetime: datetime objects
                - datetime.date: date objects
                - datetime.time: time objects
                - decimal.Decimal: decimal values for precise numeric operations
            offset_token: Optional offset token, used to track the ingestion progress and replay
                ingestion in case of failures. It could be null if user don't plan on replaying or
                can't replay.

        Raises:
            ValueError, TypeError: If the row cannot be serialized to JSON
            StreamingIngestError: If the row appending fails

        """
        self.append_rows([row], offset_token, offset_token)

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def append_rows(
        self,
        rows: List[Dict[str, Any]],
        start_offset_token: Optional[str] = None,
        end_offset_token: Optional[str] = None,
    ) -> None:
        """Append multiple rows into the channel.

        Args:
            rows: List of dictionaries representing the row data to append. Each dictionary's values can be of the following types:
                - None: null values
                - bool: boolean values (True, False)
                - int: integer values
                - float: floating-point values
                - str: string values
                - bytes: byte strings
                - bytearray: mutable byte arrays
                - tuple: tuples of values
                - list: lists of values
                - dict: nested dictionaries
                - set: sets of values
                - frozenset: immutable sets of values
                - datetime.datetime: datetime objects
                - datetime.date: date objects
                - datetime.time: time objects
                - decimal.Decimal: decimal values for precise numeric operations
            start_offset_token: Optional start offset token of the batch/row-set.
            end_offset_token: Optional end offset token of the batch/row-set.

        Raises:
            ValueError, TypeError: If the rows cannot be serialized to JSON
            StreamingIngestError: If the rows appending fails

        """
        try:
            json_bytes = self._serializer.encode_lines(rows)
        except Exception as e:
            raise ValueError(f"Failed to serialize rows to JSON: {e}") from e

        self._channel.append_rows(
            json_bytes, len(rows), start_offset_token, end_offset_token
        )

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def get_latest_committed_offset_token(self) -> Optional[str]:
        """Get the latest committed offset token for the channel.

        Returns:
            Optional[str]: The latest committed offset token for the channel, or None if the channel is brand new.

        Raises:
            StreamingIngestError: If getting the latest committed offset token fails
        """
        return self._channel.get_channel_status().latest_committed_offset_token

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def get_channel_status(self) -> ChannelStatus:
        """Get the status of the channel.

        Returns:
            ChannelStatus: The status of the channel.

        Raises:
            StreamingIngestError: If getting the channel status fails
        """
        status = self._channel.get_channel_status()
        return ChannelStatus(
            status.channel_name,
            status.status_code,
            status.latest_committed_offset_token,
        )

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def close(
        self,
        drop: bool = False,
        wait_for_flush: bool = True,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """Close the channel.

        Args:
            drop: Whether to drop the channel, defaults to False
            wait_for_flush: Whether to wait for the flush to complete. Default is True.
            timeout_seconds: The timeout in seconds for the flush, None means no timeout. Default is None.

        Raises:
            StreamingIngestError: If closing the channel fails
        """
        self._channel.close(drop, wait_for_flush, timeout_seconds)

    def is_closed(self) -> bool:
        """Check if the channel is closed.

        Returns:
            bool: True if the channel is closed, False otherwise
        """
        return self._channel.is_closed()

    @property
    def db_name(self) -> str:
        """Get the database name.

        Raises:
            ValueError: If channel is already closed
        """
        return self._channel.db_name

    @property
    def channel_name(self) -> str:
        """Get the channel name.

        Raises:
            ValueError: If channel is already closed
        """
        return self._channel.channel_name

    @property
    def schema_name(self) -> str:
        """Get the schema name.

        Raises:
            ValueError: If channel is already closed
        """
        return self._channel.schema_name

    @property
    def pipe_name(self) -> str:
        """Get the pipe name.

        Raises:
            ValueError: If channel is already closed
        """
        return self._channel.pipe_name

    def __enter__(self) -> StreamingIngestChannel:
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Exit the context manager."""
        self.close()
        return False
