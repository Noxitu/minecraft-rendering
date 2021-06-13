import struct


def parse(buffer, offset=0):
    def pop_byte():
        nonlocal offset
        offset += 1
        return buffer[offset-1]

    def pop_short():
        nonlocal offset
        offset += 2
        return struct.unpack_from('>h', buffer, offset-2)[0]

    def pop_int():
        nonlocal offset
        offset += 4
        return struct.unpack_from('>i', buffer, offset-4)[0]

    def pop_long():
        nonlocal offset
        offset += 8
        return struct.unpack_from('>q', buffer, offset-8)[0]

    def pop_float():
        nonlocal offset
        offset += 4
        return struct.unpack_from('>f', buffer, offset-4)[0]

    def pop_double():
        nonlocal offset
        offset += 8
        return struct.unpack_from('>d', buffer, offset-8)[0]

    def pop_string():
        nonlocal offset
        length = struct.unpack_from('>H', buffer, offset)[0]
        offset += 2 + length
        return buffer[offset-length:offset]

    def pop_list():
        item_type = tags.get(pop_byte())
        length = pop_int()
        return [item_type() for _ in range(length)]

    def pop_compound():
        ret = {}
        while True:
            item = pop_compound_item()
            if item is None:
                break

            key, value = item
            ret[key] = value

        return ret

    def pop_byte_array():
        length = pop_int()
        return [pop_byte() for _ in range(length)]

    def pop_int_array():
        length = pop_int()
        return [pop_int() for _ in range(length)]

    def pop_long_array():
        length = pop_int()
        return [pop_long() for _ in range(length)]

    tags = {
        0x01: pop_byte,
        0x02: pop_short,
        0x03: pop_int,
        0x04: pop_long,
        0x05: pop_float,
        0x06: pop_double,
        0x07: pop_byte_array,
        0x08: pop_string,
        0x09: pop_list,
        0x0a: pop_compound,
        0x0b: pop_int_array,
        0x0c: pop_long_array
    }

    def pop_compound_item():
        item_type = pop_byte()
        if item_type == 0x00:
            return

        item_name = pop_string()
        item_value = tags[item_type]()

        return item_name, item_value

    key, value = pop_compound_item()

    return {key: value}, offset
