import struct
import datetime


def read_uint32_le(buffer, offset):
    """Read a 32-bit unsigned integer (little-endian) from buffer at offset."""
    return struct.unpack_from("<I", buffer, offset)[0]


def read_uint64_le(buffer, offset):
    """Read a 64-bit unsigned integer (little-endian) from buffer at offset."""
    return struct.unpack_from("<Q", buffer, offset)[0]


def read_uint8(buffer, offset):
    """Read an 8-bit unsigned integer from buffer at offset."""
    return buffer[offset]


def to_bits(dec, size):
    """Return the bits (as a list of '0'/'1' strings) of the value dec in a field of width size."""
    return list(bin(dec)[2:].zfill(size))


def parse_zip_time(timebytes, datebytes):
    """
    Convert the DOS date and time format used in ZIP files into a datetime object.
    - timebytes: 2-byte integer, with hours (5 bits), minutes (6 bits), seconds/2 (5 bits)
    - datebytes: 2-byte integer, with year (7 bits since 1980), month (4 bits), day (5 bits)
    """
    timebits = to_bits(timebytes, 16)
    datebits = to_bits(datebytes, 16)
    hour = int("".join(timebits[0:5]), 2)
    minute = int("".join(timebits[5:11]), 2)
    second = int("".join(timebits[11:16]), 2) * 2
    year = int("".join(datebits[0:7]), 2) + 1980
    month = int("".join(datebits[7:11]), 2)
    day = int("".join(datebits[11:16]), 2)
    try:
        return datetime.datetime(year, month, day, hour, minute, second)
    except Exception:
        # If date is invalid, return epoch 0.
        return datetime.datetime(1970, 1, 1)
