import enum


class PdbState(enum.Enum):
    Unattached = enum.auto()
    Attached = enum.auto()
    Attaching = enum.auto()


class PdbMessageType(enum.Enum):
    COMMAND = enum.auto()
    EOF = enum.auto()
    INT = enum.auto()
