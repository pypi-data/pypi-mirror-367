from enum import Enum

# Arguments that can be used when reading
TIME_RANGE = "timerange"
UID_RANGE = "uidrange"
UID_LIST = "uidlist"
FILTER = "filter"
CHANNEL = "channel"

DEFAULT_BUFFER_SIZE = 1024

class BYTE_ORDERS(Enum):
    LITTLE_ENDIAN = "<"
    BIG_ENDIAN = ">"


class IdentifierType(Enum):
    FILE_HEADER = -1
    FILE_FOOTER = -2
    MODULE_HEADER = -3
    MODULE_FOOTER = -4
    IGNORE = -5
    FILE_BACKGROUND = -6
