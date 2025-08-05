from enum import Enum


class MediaSource(str, Enum):
    EMAIL = "Email"
    TEL = "Telephone"
    OTA = "Online Traveling Agent"
    APP = "Application"
    