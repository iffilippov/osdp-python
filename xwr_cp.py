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
read_settings_cmd = bytes([0x00, 0x01])
read_mode_command = XWRTestCommand(
            address=0x02, manufacturer_data=read_settings_cmd
        )
read_mode_command.build_command(device)
cp.send_custom_command(connection_id=bus_id, command=read_mode_command)

set_ext_mode_buffer = bytes([0x00, 0x02, 0x00, 0x01])
set_ext_mode_command = XWRTestCommand(
            address=0x02, manufacturer_data=set_ext_mode_buffer
        )
set_ext_mode_command.build_command(device)
cp.send_custom_command(connection_id=bus_id, command=set_ext_mode_command)

cp.send_custom_command(connection_id=bus_id, command=read_mode_command)

set_transparent_mode_buffer = bytes([0x00, 0x02, 0x01, 0x00])
set_transparent_mode_command = XWRTestCommand(
            address=0x02, manufacturer_data=set_transparent_mode_buffer
        )
set_transparent_mode_command.build_command(device)
cp.send_custom_command(connection_id=bus_id, command=set_transparent_mode_command)

cp.send_custom_command(connection_id=bus_id, command=read_mode_command)

set_all_mode_buffer = bytes([0x00, 0x02, 0x01, 0x01])
set_all_mode_command = XWRTestCommand(
            address=0x02, manufacturer_data=set_all_mode_buffer
        )
set_all_mode_command.build_command(device)
cp.send_custom_command(connection_id=bus_id, command=set_all_mode_command)

cp.send_custom_command(connection_id=bus_id, command=read_mode_command)

time.sleep(3)

set_default_mode_buffer = bytes([0x00, 0x02, 0x00, 0x00])
set_def_mode_command = XWRTestCommand(
            address=0x02, manufacturer_data=set_default_mode_buffer
        )
set_def_mode_command.build_command(device)
cp.send_custom_command(connection_id=bus_id, command=set_def_mode_command)

cp.send_custom_command(connection_id=bus_id, command=read_mode_command)

smart_card_scan_buffer = bytes([0x01, 0x04, 0x00])
smart_card_scan_command = XWRTestCommand(
            address=0x02, manufacturer_data=smart_card_scan_buffer
        )
smart_card_scan_command.build_command(device)
cp.send_custom_command(connection_id=bus_id, command=smart_card_scan_command)

cmd_list: list[hex] = [0x01, 0x01, 0x00]
apdu_list: list[hex] = [0x80, 0xCA, 0x9F, 0x7F, 0x2D]
select_ppse_test: list[hex] = [0x00,
            0xa4,
            0x04,
            0x00,
            0x0e,
            0x32, 0x50, 0x41, 0x59, 0x2e, 0x53, 0x59, 0x53, 0x2e, 0x44, 0x44, 0x46, 0x30, 0x31,
            0x00]
select_application: list[hex] = [0x00,
            0xa4,
            0x04,
            0x00]
test_list: list[hex] = [0x60, 0x00, 0x00, 0x00]
transparent_request_buffer = bytes(cmd_list + select_ppse_test)
# transparent_request_buffer = bytes([0x01, 0x01, 0x00, 0x00, 0xB2, 0x01, 0x14, 0x00,])
transparent_request_command = XWRTestCommand(
            address=0x02, manufacturer_data=transparent_request_buffer
        )
transparent_request_command.build_command(device)
cp.send_custom_command(connection_id=bus_id, command=transparent_request_command)
