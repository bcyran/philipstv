from typing import List

from pydantic import Field

from .base import APIObject


class ChannelID(APIObject):
    """Model of a channel change request."""

    ccid: int
    """ID of the channel."""


class ChannelShort(ChannelID):
    """Model of a channel definition in current channel response."""

    preset: str
    """Number by which the channel is available on the TV."""
    name: str
    """Name of the channel."""


class Channel(ChannelShort):
    """Model of a channel definition in channels list response."""

    onid: int
    """Original Network ID."""
    tsid: int
    """Transport Stream ID."""
    sid: int
    """Service ID."""
    service_type: str = Field(alias="serviceType")
    """Service type."""
    type: str
    """Channel type."""
    logo_version: int = Field(alias="logoVersion")
    """Channel logo version."""


class ChannelListID(APIObject):
    """Model of a channels list definition in channel change request."""

    id: str = "allcab"
    """ID of the channel list."""


class ChannelList(ChannelListID):
    """Model of a channels list definition in channels list response."""

    version: str
    """Channel list version."""


class CurrentChannel(APIObject):
    """Model of a current channel response."""

    channel: ChannelShort
    """Current channel definition."""
    channel_list: ChannelList = Field(alias="channelList")
    """Current channel list definition."""


class SetChannel(APIObject):
    """Model of a channel change request."""

    channel: ChannelID
    """Definition of a channel to change to."""
    channel_list: ChannelListID = Field(default_factory=ChannelListID, alias="channelList")
    """Definition of a list this channel is on."""


class AllChannels(APIObject):
    """Model of all channels list response."""

    version: int
    """List version."""
    id: str
    """List ID."""
    list_type: str = Field(alias="listType")
    """List type."""
    medium: str
    """TV reception medium."""
    operator: str
    """TC operator name."""
    install_country: str = Field(alias="installCountry")
    """Country the TV service is installed in."""
    channel: List[Channel] = Field(alias="Channel")
    """List of channel definitions."""
