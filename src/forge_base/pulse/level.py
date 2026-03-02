from enum import IntEnum


class MonitoringLevel(IntEnum):
    OFF = 0
    BASIC = 10
    STANDARD = 20
    DETAILED = 30
    DIAGNOSTIC = 40
