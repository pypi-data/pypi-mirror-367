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

"""Channel status information returned to users."""

from __future__ import annotations

from typing import Optional


class ChannelStatus:
    """Channel status information returned to users.

    Provides access to channel status information including the channel name,
    status code, and latest committed offset token from Snowflake server.

    """

    def __init__(
        self,
        channel_name: str,
        status_code: str,
        latest_committed_offset_token: Optional[str],
    ):
        """Initialize ChannelStatus.

        Args:
            channel_name: The name of the channel
            status_code: The status code for the channel from Snowflake server
            latest_committed_offset_token: The latest committed offset token for the channel
        """
        self._channel_name = channel_name
        self._status_code = status_code
        self._latest_committed_offset_token = latest_committed_offset_token

    @property
    def channel_name(self) -> str:
        """Get the channel name.

        Returns:
            str: The name of the channel
        """
        return self._channel_name

    @channel_name.setter
    def channel_name(self, value: str) -> None:
        """Set the channel name.

        Args:
            value: The new channel name
        """
        self._channel_name = value

    @property
    def status_code(self) -> str:
        """Get the status code for the channel.

        Returns:
            str: The status code from Snowflake server
        """
        return self._status_code

    @status_code.setter
    def status_code(self, value: str) -> None:
        """Set the status code for the channel.

        Args:
            value: The new status code
        """
        self._status_code = value

    @property
    def latest_committed_offset_token(self) -> Optional[str]:
        """Get the latest committed offset token for the channel.

        Returns:
            Optional[str]: The latest committed offset token, or None if no commits yet
        """
        return self._latest_committed_offset_token

    @latest_committed_offset_token.setter
    def latest_committed_offset_token(self, value: Optional[str]) -> None:
        """Set the latest committed offset token for the channel.

        Args:
            value: The new offset token, or None
        """
        self._latest_committed_offset_token = value

    def __repr__(self) -> str:
        """Return string representation of ChannelStatus."""
        return (
            f"ChannelStatus(channel_name='{self.channel_name}', "
            f"status_code='{self.status_code}', "
            f"latest_committed_offset_token={self.latest_committed_offset_token!r})"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"Channel '{self.channel_name}': {self.status_code}"
