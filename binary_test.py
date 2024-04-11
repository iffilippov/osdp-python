"""
Binary file read
"""

import os

FIRST_CHUNK_SIZE: int = 44
CHUNK_SIZE: int = 1421
CMD_TYPE: list[int] = [0x01]
FILE_NAME: str = 'test.mcu'

file_size = os.path.getsize(FILE_NAME)
total_size: list[int] = list(file_size.to_bytes(4, "little"))

offset: int = 0
offset_bytes: list[int] = list(offset.to_bytes(4, "little"))

initial_fragment_size: list[int] = list(FIRST_CHUNK_SIZE.to_bytes(2, "little"))
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

    while chunk_data:  # loop until the chunk is empty (the file is exhausted)
        print("WHILE LOOP")

        chunk_data = bytearray(file.read(CHUNK_SIZE))  # read the next chunk
        # print(f"Bytearray test data is {chunk_data}")

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

        test_ft_cmd = bytes(
            CMD_TYPE + total_size + offset_bytes + fragment_size + chunk_data_list
        )
        # print(f"CMD {test_ft_cmd}")
file.close()
