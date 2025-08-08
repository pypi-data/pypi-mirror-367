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

"""Streaming ingest client for creating channels to ingest data into Snowflake."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from snowflake.ingest.streaming._python_ffi import (
    StreamingIngestClient as _StreamingIngestClient,
)
from snowflake.ingest.streaming._utils import (
    _rethrow_ffi_errors_as_streaming_ingest_error,
)
from snowflake.ingest.streaming.channel_status import ChannelStatus
from snowflake.ingest.streaming.streaming_ingest_channel import StreamingIngestChannel


class StreamingIngestClient:
    """A client that is the starting point for using the Streaming Ingest client APIs.

    A single client maps to exactly one account/database/schema/pipe in Snowflake; however,
    multiple clients can point to the same account/database/schema/pipe. Each client contains
    information for Snowflake authentication and authorization, and it is used to create one
    or more StreamingIngestChannel instances for data ingestion.

    The client manages the lifecycle of streaming ingest channels and handles the underlying
    communication with Snowflake services for authentication, channel management, and data
    transmission.
    """

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def __init__(
        self,
        client_name: str,
        db_name: str,
        schema_name: str,
        pipe_name: str,
        profile_json: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a StreamingIngestClient instance.

        Creates a new streaming ingest client configured for a specific Snowflake
        account/database/schema/pipe combination. The client will be used to create
        and manage streaming ingest channels for data ingestion operations.

        Args:
            client_name: A unique name to identify this client instance. This name
                is used for tracking and debugging purposes.
            db_name: The name of the Snowflake database where data will be ingested
            schema_name: The name of the schema within the database
            pipe_name: The name of the pipe that will be used for streaming ingestion
            profile_json: Optional path to a JSON file containing connection properties
                and authentication information
            properties: Optional dictionary of connection properties and authentication
                information. Common properties include account, user, private_key, etc.

        Note:
            Either profile_json or properties must be provided for authentication.
            If both are provided, the configuration from profile_json will be merged
            with properties, with properties taking precedence for conflicting keys.

        Raises:
            ValueError: If neither profile_json nor properties are provided, or if
                required authentication information is missing
            StreamingIngestError: If the client initialization fails due to connection or
                authentication errors

        """
        # TODO: Move the property merging logic from ffi layer to wrapper layer
        if properties is not None:
            properties = {k: str(v) for k, v in properties.items()}
        self._client = _StreamingIngestClient(
            client_name, db_name, schema_name, pipe_name, profile_json, properties
        )

    def __del__(self) -> None:
        """Delete the client."""
        if hasattr(self, "_client") and self._client is not None:
            self.close(wait_for_flush=False, timeout_seconds=0)

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def open_channel(
        self, channel_name: str, offset_token: Optional[str] = None
    ) -> Tuple[StreamingIngestChannel, ChannelStatus]:
        """Open a channel with the given name.

        Args:
            channel_name: Name of the channel to open
            offset_token: Optional offset token

        Returns:
            tuple: (StreamingIngestChannel, ChannelStatus)

        Raises:
            StreamingIngestError: If opening the channel fails

        """
        channel, status = self._client.open_channel(channel_name, offset_token)
        wrapped_channel = StreamingIngestChannel(channel, _internal=True)
        wrapped_status = ChannelStatus(
            status.channel_name,
            status.status_code,
            status.latest_committed_offset_token,
        )
        return wrapped_channel, wrapped_status

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def close(
        self, wait_for_flush: bool = True, timeout_seconds: Optional[int] = None
    ) -> None:
        """Close the client.

        Args:
            wait_for_flush: Whether to wait for the flush to complete, defaults to True
            timeout_seconds: Optional timeout in seconds for the flush operation, defaults to 60 seconds

        Raises:
            StreamingIngestError: If closing the client fails
        """
        self._client.close(wait_for_flush, timeout_seconds)

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def is_closed(self) -> bool:
        """Check if the client is closed.

        Raises:
            StreamingIngestError: If checking the client status fails
        """
        return self._client.is_closed()

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def get_latest_committed_offset_tokens(
        self, channel_names: List[str]
    ) -> Dict[str, Optional[str]]:
        """Get the latest committed offset tokens for a list of channels.

        Args:
            channel_names: List of channel names

        Returns:
            Dict[str, Optional[str]]: A dictionary mapping channel names to their latest committed offset tokens.
                Value is None if the channel is brand new or does not exist.

        Raises:
            StreamingIngestError: If getting the latest committed offset tokens fails
        """
        return {
            channel_name: status.latest_committed_offset_token
            for channel_name, status in self.get_channel_statuses(channel_names).items()
        }

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def get_channel_statuses(
        self, channel_names: List[str]
    ) -> Dict[str, ChannelStatus]:
        """Get the statuses of a list of channels.

        Args:
            channel_names: List of channel names

        Returns:
            Dict[str, ChannelStatus]: A dictionary mapping channel names to their statuses.

        Raises:
            StreamingIngestError: If getting the channel statuses fails
        """
        statuses = self._client.get_channel_statuses(channel_names)
        return {
            channel_name: ChannelStatus(
                status.channel_name,
                status.status_code,
                status.latest_committed_offset_token,
            )
            for channel_name, status in statuses.items()
        }

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def drop_channel(self, channel_name: str) -> None:
        """Drop a channel.

        Args:
            channel_name: Name of the channel to drop

        Raises:
            StreamingIngestError: If dropping the channel fails
        """
        self._client.drop_channel(channel_name)

    @_rethrow_ffi_errors_as_streaming_ingest_error
    def initiate_flush(self) -> None:
        """Initiate a flush of the client.

        Raises:
            StreamingIngestError: If initiating the flush fails
        """
        self._client.initiate_flush()

    @property
    def client_name(self) -> str:
        """Get the client name.

        Raises:
            ValueError: If client is already closed
        """
        return self._client.client_name

    @property
    def db_name(self) -> str:
        """Get the database name.

        Raises:
            ValueError: If client is already closed
        """
        return self._client.db_name

    @property
    def schema_name(self) -> str:
        """Get the schema name.

        Raises:
            ValueError: If client is already closed
        """
        return self._client.schema_name

    @property
    def pipe_name(self) -> str:
        """Get the pipe name.

        Raises:
            ValueError: If client is already closed
        """
        return self._client.pipe_name

    def __enter__(self) -> StreamingIngestClient:
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Exit the context manager."""
        self.close()
        return False
