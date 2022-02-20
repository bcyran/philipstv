from typing import List

from pydantic import Field

from ._base import APIObject


class ChannelID(APIObject):
    ccid: int


class ChannelShort(ChannelID):
    preset: str
    name: str


class Channel(ChannelShort):
    onid: int
    tsid: int
    sid: int
    service_type: str = Field(alias="serviceType")
    type: str
    logo_version: int = Field(alias="logoVersion")


class ChannelListID(APIObject):
    id: str = "allcab"


class ChannelList(ChannelListID):
    version: str


class CurrentChannel(APIObject):
    channel: ChannelShort
    channel_list: ChannelList = Field(alias="channelList")


class SetChannel(APIObject):
    channel: ChannelID
    channel_list: ChannelListID = Field(default_factory=ChannelListID, alias="channelList")


class AllChannels(APIObject):
    version: int
    id: str
    list_type: str = Field(alias="listType")
    medium: str
    operator: str
    install_country: str = Field(alias="installCountry")
    channel: List[Channel] = Field(alias="Channel")
