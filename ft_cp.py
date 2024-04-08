from osdp import *
import time

conn = SerialPortOsdpConnection(port="COM8", baud_rate=9600)
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

device = Device(address=0x02, use_crc=False, use_secure_channel=False)

cmd_type: list[int] = [1]
total_size: list[hex] = [0xAA, 0xBB, 0xCC, 0xDD]
offset: list[hex] = [0x03, 0x00, 0x00, 0x00]
fragment_size: list[hex] = [0x01, 0x00]
data: list[hex] = [0xFF]
test_ft_cmd = bytes(cmd_type + total_size + offset + fragment_size + data)
file_transfer_command = FileTransferTestCommand(
            address=0x02, manufacturer_data=test_ft_cmd
        )
file_transfer_command.build_command(device)
cp.send_custom_command(connection_id=bus_id, command=file_transfer_command)

cp.shutdown()
