from osdp import *
import os
import time

PORT: str = 'COM9'
SERIAL_SPEED: int = 115200
FIRST_CHUNK_SIZE: int = 44
CHUNK_SIZE: int = 1421
CMD_TYPE: list[int] = [0x01]
FILE_NAME: str = "debug.mcu"

conn = SerialPortOsdpConnection(port=PORT, baud_rate=SERIAL_SPEED)
cp = ControlPanel()
bus_id = cp.start_connection(conn)
cp.add_device(
    connection_id=bus_id, address=0x02, use_crc=False, use_secure_channel=False
)
id_report = cp.id_report(connection_id=bus_id, address=0x02)
device_capabilities = cp.device_capabilities(connection_id=bus_id, address=0x02)
local_status = cp.local_status(connection_id=bus_id, address=0x02)
input_status = cp.input_status(connection_id=bus_id, address=0x02)
output_status = cp.output_status(connection_id=bus_id, address=0x02)


class FileTransferTestCommand(Command):
    def __init__(self, address: int, manufacturer_data: bytes):
        self.address = address
        self.manufacturer_data = manufacturer_data

    @property
    def command_code(self) -> int:
        return 0x7C

    def security_control_block(self) -> bytes:
        return bytes([0x02, 0x17])

    def data(self) -> bytes:
        return self.manufacturer_data

    def custom_command_update(self, command_buffer: bytearray):
        pass

class AbortTestCommand(Command):
    def __init__(self, address: int, manufacturer_data: bytes):
        self.address = address
        self.manufacturer_data = manufacturer_data

    @property
    def command_code(self) -> int:
        return 0xA2

    def security_control_block(self) -> bytes:
        return bytes([0x02, 0x17])

    def data(self) -> bytes:
        return self.manufacturer_data

    def custom_command_update(self, command_buffer: bytearray):
        pass


device = Device(address=0x02, use_crc=False, use_secure_channel=False)

file_size = os.path.getsize(FILE_NAME)
total_size: list[int] = list(file_size.to_bytes(4, "little"))

offset: int = 0
offset_bytes: list[int] = list(offset.to_bytes(4, "little"))

initial_fragment_size: list[int] = list(FIRST_CHUNK_SIZE.to_bytes(2, "little"))
zero_fragment_size: list[int] = [0, 0]
fragment_size: list[int] = list(CHUNK_SIZE.to_bytes(2, "little"))

with open(FILE_NAME, "rb") as file:
    chunk_data: str = bytearray(file.read(FIRST_CHUNK_SIZE))
    print(f"Bytearray test data is {chunk_data}")

    chunk_data_list: list[int] = list(chunk_data)
    print(f"CHUNK DATA LIST is {chunk_data_list}")
    offset += FIRST_CHUNK_SIZE
    print(f"CURRENT OFFSET IS {offset}")

    test_ft_cmd = bytes(
        CMD_TYPE + total_size + offset_bytes + initial_fragment_size + chunk_data_list
    )
    file_transfer_command = FileTransferTestCommand(
        address=0x02, manufacturer_data=test_ft_cmd
    )
    file_transfer_command.build_command(device)
    cp.send_custom_command(connection_id=bus_id, command=file_transfer_command)

    # abort_command = AbortTestCommand(address=0x02, manufacturer_data=[])
    # abort_command.build_command(device)
    # cp.send_custom_command(connection_id=bus_id, command=abort_command)

    while chunk_data:  # loop until the chunk is empty (the file is exhausted)

        chunk_data = bytearray(file.read(CHUNK_SIZE))  # read the next chunk
        print(f"Bytearray test data is {chunk_data}")

        chunk_data_list: list[int] = list(chunk_data)
        print(f"CHUNK DATA LIST is {chunk_data_list}")
        chunk_data_list_len: int = len(chunk_data_list)
        print(f"CHUNK DATA LIST SIZE IS {chunk_data_list_len}")

        if not chunk_data_list:
            print("CHUNK DATA LIST IS EMPTY")
            fragment_size = [0x00, 0x00]
            print(f"LAST CURRENT OFFSET IS {offset}")
            offset_bytes = list(offset.to_bytes(4, "little"))
            print(f"LAST CURRENT OFFSET BYTES ARE {offset_bytes}")
            break
        elif len(chunk_data_list) != CHUNK_SIZE:
            print(f"CURRENT OFFSET IS {offset}")
            offset_bytes = list(offset.to_bytes(4, "little"))
            print(f"CURRENT OFFSET BYTES ARE {offset_bytes}")
            offset += len(chunk_data_list)
            fragment_size = list(chunk_data_list_len.to_bytes(2, "little"))
            print(f"CHUNK DATA LIST SIZE IN BYTES IS {fragment_size}")
        else:
            print(f"CURRENT OFFSET IS {offset}")
            offset_bytes = list(offset.to_bytes(4, "little"))
            print(f"CURRENT OFFSET BYTES ARE {offset_bytes}")
            offset += CHUNK_SIZE
            # Timeout test
            if offset == 2886:
                break

        # Idling osdp_FILETRANSFER TEST
        test_ft_cmd = bytes(
            CMD_TYPE + total_size + offset_bytes + zero_fragment_size + chunk_data_list
        )
        file_transfer_command = FileTransferTestCommand(
            address=0x02, manufacturer_data=test_ft_cmd
        )
        file_transfer_command.build_command(device)
        cp.send_custom_command(connection_id=bus_id, command=file_transfer_command)

        test_ft_cmd = bytes(
            CMD_TYPE + total_size + offset_bytes + fragment_size + chunk_data_list
        )
        file_transfer_command = FileTransferTestCommand(
            address=0x02, manufacturer_data=test_ft_cmd
        )
        file_transfer_command.build_command(device)
        cp.send_custom_command(connection_id=bus_id, command=file_transfer_command)

    time.sleep(5)
    # Idling osdp_FILETRANSFER TEST
    test_ft_cmd = bytes(
        CMD_TYPE + total_size + offset_bytes + zero_fragment_size + chunk_data_list
    )
    file_transfer_command = FileTransferTestCommand(
        address=0x02, manufacturer_data=test_ft_cmd
    )
    file_transfer_command.build_command(device)
    cp.send_custom_command(connection_id=bus_id, command=file_transfer_command)

file.close()
cp.shutdown()
