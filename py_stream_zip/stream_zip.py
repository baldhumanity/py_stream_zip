import os
import struct
import zlib

from . import constants, utils
from .zip_entry import ZipEntry
from .central_directory import (
    CentralDirectoryHeader,
    CentralDirectoryLoc64Header,
    CentralDirectoryZip64Header,
)


class StreamZip:
    def __init__(
        self,
        file,
        store_entries=True,
        lazy_entries=False,
        chunk_size=None,
        encoding="utf-8",
    ):
        """
        Initialize a StreamZip instance.

        :param file: Path to ZIP file or a file-like object (opened in binary mode).
        :param store_entries: If True then store entries in a dict for random access.
        :param lazy_entries: If True then defer parsing of variable-length fields for each entry until needed.
        :param chunk_size: Not used in this synchronous version but kept for parity.
        :param encoding: Filename encoding.
        """
        self.encoding = encoding
        self.store_entries = store_entries
        self.lazy_entries = lazy_entries
        self.entries = {} if store_entries else None
        self.entries_count = 0
        self.comment = None
        self._file_path = None
        self._fp = None  # file pointer
        self._central_dir_header = None

        # Open the file if a path is provided; otherwise, assume file-like object.
        if isinstance(file, str):
            self._file_path = file
            self._fp = open(file, "rb")
        else:
            self._fp = file

        # Get the file size (needed for scanning the EOCD record at the file tail).
        self._file_size = os.fstat(self._fp.fileno()).st_size

        # Step 1: Locate and read the central directory (EOCD record).
        self._read_central_directory()
        # Step 2: Read all entries from the central directory.
        self._read_entries()

    def _read_central_directory(self):
        """
        Locate and parse the End-of-Central-Directory (EOCD) record.

        Process:
          1. Determine the maximum number of bytes at the end of the file to search.
          2. Seek to that area (file_size - read_size) and read it.
          3. Search backwards for the EOCD signature.
          4. Extract the EOCD header and fill a CentralDirectoryHeader instance.
          5. Decode and store the ZIP comment (if any).
          6. Record the number of entries as specified in the header.

        Note: ZIP64 is not supported. If the header indicates ZIP64 values, an error is raised.
        """
        max_comment = constants.MAXFILECOMMENT
        eocd_search_size = (
            constants.ENDHDR + max_comment
        )  # maximum size for EOCD record plus comment
        read_size = min(
            eocd_search_size, self._file_size
        )  # ensure we do not exceed file size

        # Seek to the location where the EOCD record might be located.
        self._fp.seek(self._file_size - read_size)
        data = self._fp.read(read_size)

        # Look for the EOCD signature in the data block (convert signature to little-endian bytes).
        signature = constants.ENDSIG.to_bytes(4, byteorder="little")
        pos = data.rfind(signature)
        if pos < 0:
            raise ValueError("End of central directory signature not found")

        # Extract the EOCD record (fixed-size header portion).
        eocd = data[pos : pos + constants.ENDHDR]
        cd_header = CentralDirectoryHeader()
        cd_header.read(eocd)
        self._central_dir_header = cd_header

        # Decode the ZIP file comment if present (after the fixed EOCD header).
        self.comment = (
            data[
                pos
                + constants.ENDHDR : pos
                + constants.ENDHDR
                + cd_header.comment_length
            ].decode(self.encoding, errors="replace")
            if cd_header.comment_length
            else None
        )
        self.entries_count = cd_header.volume_entries

        # Check for ZIP64 markers. Currently, ZIP64 support is not implemented.
        if (
            cd_header.volume_entries == constants.EF_ZIP64_OR_16
            or cd_header.total_entries == constants.EF_ZIP64_OR_16
            or cd_header.size == constants.EF_ZIP64_OR_32
            or cd_header.offset == constants.EF_ZIP64_OR_32
        ):
            raise NotImplementedError("ZIP64 format not implemented in this version")

    def _read_entries(self):
        """
        Read the central directory entries from the ZIP file.
        Depending on the lazy_entries flag, parse the variable-length fields now or later.
        """
        cd_offset = self._central_dir_header.offset
        cd_size = self._central_dir_header.size
        self._fp.seek(cd_offset)
        if self.lazy_entries:
            # Use a memoryview to avoid unnecessary data copying.
            cd_data = memoryview(self._fp.read(cd_size))
            pos = 0
            entry_count = self._central_dir_header.volume_entries
            for _ in range(entry_count):
                # Each entry must have at least the fixed-size header
                if pos + constants.CENHDR > len(cd_data):
                    raise ValueError("Incomplete central directory entry")
                entry = ZipEntry()
                # Parse fixed header fields
                entry.read_header(cd_data, pos)
                pos_header_end = pos + constants.CENHDR
                # Only decode the filename to enable indexing.
                fname_data = cd_data[pos_header_end : pos_header_end + entry.fname_len]
                entry.name = fname_data.tobytes().decode(
                    self.encoding, errors="replace"
                )
                # Store lazy information for deferred parsing.
                entry._cd_data = (
                    cd_data  # the entire central directory block (as memoryview)
                )
                entry._variable_offset = (
                    pos_header_end  # start of variable part (filename, extra, comment)
                )
                entry._variable_size = entry.fname_len + entry.extra_len + entry.com_len
                entry._parsed_lazy = (
                    False  # marks that extra and comment haven't been parsed yet
                )
                pos = pos_header_end + entry._variable_size
                if self.store_entries:
                    self.entries[entry.name] = entry
        else:
            cd_data = self._fp.read(cd_size)
            pos = 0
            entry_count = self._central_dir_header.volume_entries
            for _ in range(entry_count):
                if pos + constants.CENHDR > len(cd_data):
                    raise ValueError("Incomplete central directory entry")
                entry = ZipEntry()
                entry.read_header(cd_data, pos)
                pos += constants.CENHDR
                variable_size = entry.fname_len + entry.extra_len + entry.com_len
                if pos + variable_size > len(cd_data):
                    raise ValueError("Corrupted central directory entry")
                entry.read(cd_data, pos, self.encoding)
                pos += variable_size
                if self.store_entries:
                    self.entries[entry.name] = entry

    def entry(self, name):
        """
        Retrieve an entry by name from the stored entries.
        """
        if not self.store_entries:
            raise ValueError("Entries storage is disabled")
        return self.entries.get(name)

    def open_entry(self, entry):
        """
        Open an entry and verify its local file header.
        Before processing, if the entry was lazy-loaded, ensure it has been fully parsed.
        Returns the data offset (position where file data starts).
        """
        if isinstance(entry, str):
            entry_obj = self.entry(entry)
            if not entry_obj:
                raise ValueError(f"Entry {entry} not found")
        else:
            entry_obj = entry

        # For lazy entries, ensure variable fields are parsed.
        if hasattr(entry_obj, "_parsed_lazy") and not entry_obj._parsed_lazy:
            entry_obj.ensure_parsed(self.encoding)

        if entry_obj.is_directory:
            raise ValueError("Entry is a directory")

        self._fp.seek(entry_obj.offset)
        local_header = self._fp.read(constants.LOCHDR)
        if utils.read_uint32_le(local_header, 0) != constants.LOCSIG:
            raise ValueError("Local header signature mismatch")
        entry_obj.read_data_header(local_header)
        data_offset = (
            entry_obj.offset
            + constants.LOCHDR
            + entry_obj.fname_len
            + entry_obj.extra_len
        )
        return entry_obj, data_offset

    def entry_data_sync(self, entry):
        """
        Synchronously read an entry's data (compressed or not) and return the uncompressed bytes.

        Process:
          1. Open the entry to validate it and compute the data offset.
          2. Seek to the data offset and read the number of bytes specified by compressed_size.
          3. Depending on the compression method:
             - If STORED, the data is returned as-is.
             - If DEFLATED, the data is decompressed using zlib.
          4. Validate that the uncompressed data size matches the expected size.
          5. Optionally, perform a CRC check to ensure data integrity.
        """
        entry_obj, data_offset = self.open_entry(entry)
        self._fp.seek(data_offset)
        data = self._fp.read(entry_obj.compressed_size)
        if entry_obj.method == constants.STORED:
            result = data
        elif entry_obj.method == constants.DEFLATED:
            result = zlib.decompress(data, -zlib.MAX_WBITS)
        else:
            raise NotImplementedError(
                f"Compression method {entry_obj.method} not supported"
            )
        if len(result) != entry_obj.size:
            raise ValueError("Invalid uncompressed data size")
        # If the flag indicates that CRC can be checked, calculate and compare.
        if (
            entry_obj.flags & 0x8
        ) != 0x8:  # bit 3 indicates missing CRC in header if set
            calc_crc = zlib.crc32(result) & 0xFFFFFFFF
            if calc_crc != entry_obj.crc:
                raise ValueError("CRC check failed")
        return result

    def close(self):
        """
        Close the underlying file pointer.
        """
        if self._fp:
            self._fp.close()
            self._fp = None
