import asyncio
from seriallib.consts import ATTEMPTS_MAX, MOCK_PORT_NAME
from seriallib.commands import IncomingArmCommand, OutgoingArmCommand


import serial


import time

from seriallib.exceptions import (
    ArmInUseException,
    ArmRetryLimitExceededException,
    ArmUnknownOrUnexpectedResponseException,
)


class ArmController:
    def __init__(self, port: str):
        self.serial = None
        self.port = port
        self.lock = asyncio.Lock()

        if self.port == MOCK_PORT_NAME:
            print("mocking output")

    async def grab(self):
        await self._write_command(OutgoingArmCommand.GRAB)

    async def move_bin1(self):
        await self._write_command(OutgoingArmCommand.MOVE_BIN1)

    async def move_bin2(self):
        await self._write_command(OutgoingArmCommand.MOVE_BIN2)

    async def move_bin3(self):
        await self._write_command(OutgoingArmCommand.MOVE_BIN3)

    async def move_neutral(self):
        await self._write_command(OutgoingArmCommand.RESET)

    async def _write_command(self, command: OutgoingArmCommand) -> None:
        print(f"Sending command {command}")
        
        if (self.lock.locked()):
            raise ArmInUseException("Arm is currently in use: only one command can be sent at a time.")
        
        
        async with self.lock:
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
                    (await self._get_serial()).write(command.value.encode())
                    # if unwritten > 0:
                    # raise serial.SerialException("Could not write all bytes")
                    done = True
                except serial.SerialException as e:
                    print(e)
                    print(f"Failed to send command {command} attempt {attempts}, retrying")
                    attempts += 1
                    self.serial = None
                    await asyncio.sleep(1)

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
                    response = (await self._get_serial()).read(1).decode()
                    if response == IncomingArmCommand.ACK.value:
                        done = True
                    else:
                        raise ArmUnknownOrUnexpectedResponseException(
                            f"Unexpected response '{response}' to command {command}"
                        )
                except serial.SerialException:
                    print(
                        f"Failed to receive ack for command {command} attempt {attempts}, retrying"
                    )
                    attempts += 1
                    self.serial = None
                    await asyncio.sleep(1)

            print(f"Received ack for command {command}")

            attempts = 1
            done = False

            while not done:
                if attempts > ATTEMPTS_MAX:
                    raise ArmRetryLimitExceededException(
                        f"Failed to rcv success after {ATTEMPTS_MAX} attempts"
                    )
                try:
                    response = (await self._get_serial()).read(1).decode()
                    if response == IncomingArmCommand.FINISHED.value:
                        done = True
                    else:
                        raise ArmUnknownOrUnexpectedResponseException(
                            f"Unexpected response '{response}' to command {command}"
                        )
                except serial.SerialException:
                    print(f"Failed to receive finished_ack for command {command} attempt {attempts}, retrying")
                    attempts += 1
                    self.serial = None
                    await asyncio.sleep(1)

            print("Received finished_ack for command")
        finally:
        

    async def _get_serial(self) -> serial.Serial:
        """Internal: get underlying serial object, initializing if necessary
        DO NOT CALL THIS WHEN self.port == MOCK_PORT

        Returns:
            _type_: _description_
        """
        if self.serial is None:
            self.serial = self._serial_init()
        return await self.serial

    async def _serial_init(self) -> serial.Serial:
        print("start serial init")
        s = serial.Serial(self.port, timeout=2)
        await asyncio.sleep(1)
        s.flush()
        s.reset_input_buffer()
        s.reset_output_buffer()
        print("serial init done", s.in_waiting)
        return s
