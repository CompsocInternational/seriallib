from seriallib.consts import ATTEMPTS_MAX, MOCK_PORT_NAME
from seriallib.commands import IncomingArmCommand, OutgoingArmCommand


import serial


import time

from seriallib.exceptions import (
    ArmRetryLimitExceededException,
    ArmUnknownOrUnexpectedResponseException,
)


class ArmController:
    def __init__(self, port: str):
        self.serial = None
        self.port = port

        if self.port == MOCK_PORT_NAME:
            print("mocking output")

    def grab(self):
        self._write_command(OutgoingArmCommand.GRAB)

    def move_bin1(self):
        self._write_command(OutgoingArmCommand.MOVE_BIN1)

    def move_bin2(self):
        self._write_command(OutgoingArmCommand.MOVE_BIN2)

    def move_bin3(self):
        self._write_command(OutgoingArmCommand.MOVE_BIN3)

    def move_neutral(self):
        self._write_command(OutgoingArmCommand.RESET)

    def _write_command(self, command: OutgoingArmCommand) -> None:
        print(f"Sending command {command}")
        
        if self.port == MOCK_PORT_NAME:
            return

        done = False
        attempts = 1


        while not done:
            if attempts > ATTEMPTS_MAX:
                raise ArmRetryLimitExceededException(
                    f"Failed to send command after {ATTEMPTS_MAX} attempts"
                )
            try:
                self._get_serial().write(command.value.encode())
                # if unwritten > 0:
                # raise serial.SerialException("Could not write all bytes")
                done = True
            except serial.SerialException as e:
                print(e)
                print(f"Failed to send command {command} attempt {attempts}, retrying")
                attempts += 1
                self.serial = None
                time.sleep(1)

        print(f"Completed sending command in {attempts} attempts")

        # wait for command finished_ack
        attempts = 1
        done = False



        while not done:
            if attempts > ATTEMPTS_MAX:
                raise ArmRetryLimitExceededException(
                    f"Failed to rcv response after {ATTEMPTS_MAX} attempts"
                )
            try:
                data = self._get_serial().read_until(IncomingArmCommand.ACK.value.encode()).decode()
                if data == IncomingArmCommand.ACK.value:
                    done = True
                else:
                    raise ArmUnknownOrUnexpectedResponseException(
                        f"Unexpected response '{data}' to command {command}"
                    )
            except serial.SerialException as e:
                print(
                    f"Failed to receive ack for command {command} attempt {attempts}, retrying\n{e}"
                )
                attempts += 1
                self.serial = None
                time.sleep(1)

        print(f"Received ack for command {command}")

        attempts = 1
        done = False

        while not done:
            if attempts > ATTEMPTS_MAX:
                raise ArmRetryLimitExceededException(
                    f"Failed to rcv success after {ATTEMPTS_MAX} attempts"
                )
            try:
                data = self._get_serial().read_until(IncomingArmCommand.ACK.value.encode()).decode()
                if data == IncomingArmCommand.FINISHED.value:
                    done = True
                else:
                    raise ArmUnknownOrUnexpectedResponseException(
                        f"Unexpected response '{data}' to command {command}"
                    )
            except serial.SerialException as e:
                print(f"Failed to receive finished_ack for command {command} attempt {attempts}, retrying\n{e}")
                attempts += 1
                self.serial = None
                time.sleep(1)

        print("Received finished_ack for command")
    

    def _get_serial(self) -> serial.Serial:
        """Internal: get underlying serial object, initializing if necessary
        DO NOT CALL THIS WHEN self.port == MOCK_PORT

        Returns:
            _type_: _description_
        """
        if self.serial is None:
            self.serial = self._serial_init()
        return self.serial

    def _serial_init(self) -> serial.Serial:
        print("start serial init")
        s = serial.Serial(self.port, timeout=2)
        time.sleep(1)
        s.flush()
        s.reset_input_buffer()
        s.reset_output_buffer()
        print("serial init done", s.in_waiting)
        return s
