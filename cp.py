from osdp import *

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

class XWRTestCommand(Command):
    def __init__(self, address: int, manufacturer_data: bytes):
        self.address = address
        self.manufacturer_data = manufacturer_data

    @property
    def command_code(self) -> int:
        return 0xA1

    def security_control_block(self) -> bytes:
        return bytes([0x02, 0x17])

    def data(self) -> bytes:
        return self.manufacturer_data

    def custom_command_update(self, command_buffer: bytearray):
        pass

device = Device(address=0x02, use_crc=False, use_secure_channel=False)
read_settings_buffer = bytes([0x00, 0x01])
set_mode_buffer = bytes([0x00, 0x02, 0x00, 0x00])

test_command = XWRTestCommand(
            address=0x02, manufacturer_data=read_settings_buffer
        )
test_command.build_command(device)

cp.send_custom_command(connection_id=bus_id, command=test_command)

cp.shutdown()
