import enum

class OutgoingArmCommand(enum.Enum):
    GRAB = "1"
    MOVE_BIN1 = "2"
    MOVE_BIN2 = "3"
    MOVE_BIN3 = "4"
    RESET = "5"

class IncomingArmCommand(enum.Enum):
    ACK = "A"
    FINISHED = "F"
    ERROR = "E"