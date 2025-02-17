import struct
import re
from . import constants, utils


class ZipEntry:
    def __init__(self):
        # Initialize all attributes that will be filled when parsing an entry.
        self.ver_made = None
        self.version = None
        self.flags = None
        self.method = None
        self.time = None
        self.crc = None
        self.compressed_size = None
        self.size = None
        self.fname_len = None
        self.extra_len = None
        self.com_len = None
        self.disk_start = None
        self.inattr = None
        self.attr = None
        self.offset = None
        self.name = None
        self.is_directory = False
        self.comment = None

    def read_header(self, data, offset=0):
        """
        Read the fixed-size central directory header (46 bytes) from data starting at offset.

        Process:
          1. Validate that there is enough data and that the header begins with the proper signature.
          2. Parse fields including version, flags, method, modification time/date,
             CRC, sizes, and the lengths of variable fields (filename, extra, comment).
          3. These values are stored in the corresponding attributes.
        """
        if (
            len(data) < offset + constants.CENHDR
            or utils.read_uint32_le(data, offset) != constants.CENSIG
        ):
            raise ValueError("Invalid entry header")
        # Read version information.
        self.ver_made = struct.unpack_from("<H", data, offset + constants.CENVEM)[0]
        self.version = struct.unpack_from("<H", data, offset + constants.CENVER)[0]
        # Read general purpose bit flags.
        self.flags = struct.unpack_from("<H", data, offset + constants.CENFLG)[0]
        # Read compression method.
        self.method = struct.unpack_from("<H", data, offset + constants.CENHOW)[0]
        # Read the DOS-formatted time and date; convert to a Python datetime.
        timebytes = struct.unpack_from("<H", data, offset + constants.CENTIM)[0]
        datebytes = struct.unpack_from("<H", data, offset + constants.CENTIM + 2)[0]
        self.time = utils.parse_zip_time(timebytes, datebytes)
        # Extract CRC, compressed size, and uncompressed size.
        self.crc = utils.read_uint32_le(data, offset + constants.CENCRC)
        self.compressed_size = utils.read_uint32_le(data, offset + constants.CENSIZ)
        self.size = utils.read_uint32_le(data, offset + constants.CENLEN)
        # Read the lengths of the filename, extra field, and file comment.
        self.fname_len = struct.unpack_from("<H", data, offset + constants.CENNAM)[0]
        self.extra_len = struct.unpack_from("<H", data, offset + constants.CENEXT)[0]
        self.com_len = struct.unpack_from("<H", data, offset + constants.CENCOM)[0]
        # Read disk start number and file attributes.
        self.disk_start = struct.unpack_from("<H", data, offset + constants.CENDSK)[0]
        self.inattr = struct.unpack_from("<H", data, offset + constants.CENATT)[0]
        self.attr = utils.read_uint32_le(data, offset + constants.CENATX)
        # Get the offset to the local file header.
        self.offset = utils.read_uint32_le(data, offset + constants.CENOFF)

    def read_data_header(self, data):
        """
        Read the local file header (30 bytes) from data and update the entry's attributes.

        Process:
          1. Ensure the local header has the correct signature.
          2. Parse version, flags, and compression method.
          3. Convert the DOS timestamp into a datetime.
          4. Update CRC, compressed size, and uncompressed size if available.
          5. Read the lengths of the filename and extra field that follow the fixed header.
        """
        if utils.read_uint32_le(data, 0) != constants.LOCSIG:
            raise ValueError("Invalid local header")
        self.version = struct.unpack_from("<H", data, constants.LOCVER)[0]
        self.flags = struct.unpack_from("<H", data, constants.LOCFLG)[0]
        self.method = struct.unpack_from("<H", data, constants.LOCHOW)[0]
        timebytes = struct.unpack_from("<H", data, constants.LOCTIM)[0]
        datebytes = struct.unpack_from("<H", data, constants.LOCTIM + 2)[0]
        self.time = utils.parse_zip_time(timebytes, datebytes)
        # Read the CRC; if 0, keep previously set value.
        self.crc = utils.read_uint32_le(data, constants.LOCCRC) or self.crc
        comp_size = utils.read_uint32_le(data, constants.LOCSIZ)
        if comp_size and comp_size != constants.EF_ZIP64_OR_32:
            self.compressed_size = comp_size
        size = utils.read_uint32_le(data, constants.LOCLEN)
        if size and size != constants.EF_ZIP64_OR_32:
            self.size = size
        # Get lengths of the variable-length fields.
        self.fname_len = struct.unpack_from("<H", data, constants.LOCNAM)[0]
        self.extra_len = struct.unpack_from("<H", data, constants.LOCEXT)[0]

    def read(self, data, offset=0, encoding="utf-8"):
        """
        Read variable-length fields (filename, extra, comment) from data starting at offset.

        Process:
          1. Decode the filename from the first fname_len bytes.
          2. Mark the entry as a directory if the name ends with "/" or "\\".
          3. Process extra field data if available.
          4. Decode the file comment if present.
        """
        # Decode filename.
        name_data = data[offset : offset + self.fname_len]
        self.name = name_data.decode(encoding, errors="replace")
        if self.name.endswith("/") or self.name.endswith("\\"):
            self.is_directory = True
        current = offset + self.fname_len
        # Process the extra field if present.
        if self.extra_len:
            self.read_extra(data[current : current + self.extra_len])
            current += self.extra_len
        # Process the file comment if available.
        if self.com_len:
            self.comment = data[current : current + self.com_len].decode(
                encoding, errors="replace"
            )
        else:
            self.comment = None

    def validate_name(self):
        """
        Reject suspicious or malicious file names.
        """
        if re.search(r"\\|^\w+:|^\/|(^|\/)\.\.(\/|$)", self.name):
            raise ValueError(f"Malicious entry: {self.name}")

    def read_extra(self, data):
        """
        Parse the extra data block.

        The extra block can contain several sub-fields. Each sub-field consists of:
          - A 2-byte signature indicating its type.
          - A 2-byte length of the extra field data.
          - The extra field data itself.

        This function iterates over the block and dispatches to appropriate handlers
        based on the signature (e.g., ZIP64 or Unicode filename).
        """
        offset = 0
        while offset < len(data):
            if offset + 4 > len(data):
                break
            signature = struct.unpack_from("<H", data, offset)[0]
            offset += 2
            size = struct.unpack_from("<H", data, offset)[0]
            offset += 2
            block = data[offset : offset + size]
            if signature == constants.ID_ZIP64:
                self.parse_zip64_extra(block)
            elif signature == constants.ID_UNICODE_PATH:
                self.parse_unicode_filename(block)
            offset += size

    def parse_unicode_filename(self, data):
        """
        Handle the extra field for a Unicode filename.

        The format is:
          - 1 byte for the version.
          - 4 bytes for the CRC of the original filename.
          - The rest is the UTF-8 encoded filename.

        This routine decodes the filename from the provided block.
        """
        if len(data) < 5:
            return
        # version = data[0] (unused)
        name_data = data[5:]
        self.name = name_data.decode("utf-8", errors="replace")

    def parse_zip64_extra(self, data):
        """
        Parse the ZIP64 extra field.

        The order of values in the data block is:
          - Uncompressed size (8 bytes) if original size equals EF_ZIP64_OR_32.
          - Compressed size (8 bytes) if original compressed size equals EF_ZIP64_OR_32.
          - Local header offset (8 bytes) if original offset equals EF_ZIP64_OR_32.
          - Disk start number (4 bytes) if original disk start equals EF_ZIP64_OR_16.

        Each field is read only if the corresponding value in the header was set to the placeholder.
        """
        offset = 0
        if len(data) >= 8 and self.size == constants.EF_ZIP64_OR_32:
            self.size = utils.read_uint64_le(data, offset)
            offset += 8
        if len(data) >= offset + 8 and self.compressed_size == constants.EF_ZIP64_OR_32:
            self.compressed_size = utils.read_uint64_le(data, offset)
            offset += 8
        if len(data) >= offset + 8 and self.offset == constants.EF_ZIP64_OR_32:
            self.offset = utils.read_uint64_le(data, offset)
            offset += 8
        if len(data) >= offset + 4 and self.disk_start == constants.EF_ZIP64_OR_16:
            self.disk_start = struct.unpack_from("<I", data, offset)[0]
