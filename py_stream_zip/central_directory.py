import struct
from . import constants, utils


class CentralDirectoryHeader:
    def __init__(self):
        self.volume_entries = None
        self.total_entries = None
        self.size = None
        self.offset = None
        self.comment_length = None

    def read(self, data):
        """
        Parse the End-of-Central-Directory (EOCD) record from data.

        Process:
          1. Ensure the data length matches the expected size of an EOCD record.
          2. Verify that the signature matches the END signature.
          3. Unpack the number of entries on this disk and in total.
          4. Read the size and offset of the central directory.
          5. Extract the length of the ZIP comment.
        """
        if (
            len(data) != constants.ENDHDR
            or utils.read_uint32_le(data, 0) != constants.ENDSIG
        ):
            raise ValueError("Invalid central directory header")
        self.volume_entries = struct.unpack_from("<H", data, constants.ENDSUB)[0]
        self.total_entries = struct.unpack_from("<H", data, constants.ENDTOT)[0]
        self.size = utils.read_uint32_le(data, constants.ENDSIZ)
        self.offset = utils.read_uint32_le(data, constants.ENDOFF)
        self.comment_length = struct.unpack_from("<H", data, constants.ENDCOM)[0]


class CentralDirectoryLoc64Header:
    def __init__(self):
        self.header_offset = None  # ZIP64 EOCD header offset

    def read(self, data):
        """
        Parse the ZIP64 End-of-Central-Directory Locator from data.

        Process:
          1. Verify that the data size and signature are correct.
          2. Read the offset to the ZIP64 EOCD header.
        """
        if (
            len(data) != constants.ENDL64HDR
            or utils.read_uint32_le(data, 0) != constants.ENDL64SIG
        ):
            raise ValueError("Invalid zip64 central directory locator")
        self.header_offset = utils.read_uint64_le(data, constants.ENDSUB)


class CentralDirectoryZip64Header:
    def __init__(self):
        self.volume_entries = None
        self.total_entries = None
        self.size = None
        self.offset = None

    def read(self, data):
        """
        Parse the ZIP64 End-of-Central-Directory Header from data.

        Process:
          1. Check that the data length and signature are as expected.
          2. Extract the number of entries on this disk and total across the ZIP.
          3. Read the size and starting offset of the central directory.
        """
        if (
            len(data) != constants.END64HDR
            or utils.read_uint32_le(data, 0) != constants.END64SIG
        ):
            raise ValueError("Invalid zip64 central directory header")
        self.volume_entries = utils.read_uint64_le(data, constants.END64SUB)
        self.total_entries = utils.read_uint64_le(data, constants.END64TOT)
        self.size = utils.read_uint64_le(data, constants.END64SIZ)
        self.offset = utils.read_uint64_le(data, constants.END64OFF)
