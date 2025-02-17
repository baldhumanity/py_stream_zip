# Constants for ZIP file structures

# Local file header (LOC)
LOCHDR = 30  # LOC header size
LOCSIG = 0x04034B50  # "PK\x03\x04"
LOCVER = 4  # version needed to extract
LOCFLG = 6  # general purpose bit flag
LOCHOW = 8  # compression method
LOCTIM = 10  # modification time (2 bytes time, 2 bytes date)
LOCCRC = 14  # uncompressed file crc-32 value
LOCSIZ = 18  # compressed size
LOCLEN = 22  # uncompressed size
LOCNAM = 26  # filename length
LOCEXT = 28  # extra field length

# Data descriptor (EXT)
EXTSIG = 0x08074B50  # "PK\x07\x08"
EXTHDR = 16  # EXT header size
EXTCRC = 4  # uncompressed file crc-32 value
EXTSIZ = 8  # compressed size
EXTLEN = 12  # uncompressed size

# Central directory file header (CEN)
CENHDR = 46  # CEN header size
CENSIG = 0x02014B50  # "PK\x01\x02"
CENVEM = 4  # version made by
CENVER = 6  # version needed to extract
CENFLG = 8  # encrypt, decrypt flags
CENHOW = 10  # compression method
CENTIM = 12  # modification time (2 bytes time, 2 bytes date)
CENCRC = 16  # uncompressed file crc-32 value
CENSIZ = 20  # compressed size
CENLEN = 24  # uncompressed size
CENNAM = 28  # filename length
CENEXT = 30  # extra field length
CENCOM = 32  # file comment length
CENDSK = 34  # volume number start
CENATT = 36  # internal file attributes
CENATX = 38  # external file attributes (host system dependent)
CENOFF = 42  # LOC header offset

# End of central directory (END)
ENDHDR = 22  # END header size
ENDSIG = 0x06054B50  # "PK\x05\x06"
ENDSIGFIRST = 0x50
ENDSUB = 8  # number of entries on this disk
ENDTOT = 10  # total number of entries
ENDSIZ = 12  # central directory size in bytes
ENDOFF = 16  # offset of first CEN header
ENDCOM = 20  # zip file comment length
MAXFILECOMMENT = 0xFFFF

# ZIP64 end of central directory locator
ENDL64HDR = 20  # ZIP64 locator header size
ENDL64SIG = 0x07064B50  # ZIP64 locator signature
ENDL64SIGFIRST = 0x50
ENDL64OFS = 8  # ZIP64 EOCD header offset

# ZIP64 end of central directory header
END64HDR = 56  # ZIP64 EOCD header size
END64SIG = 0x06064B50  # ZIP64 EOCD signature
END64SIGFIRST = 0x50
END64SUB = 24  # number of entries on this disk
END64TOT = 32  # total number of entries
END64SIZ = 40
END64OFF = 48

# Compression methods
STORED = 0  # no compression
SHRUNK = 1
REDUCED1 = 2
REDUCED2 = 3
REDUCED3 = 4
REDUCED4 = 5
IMPLODED = 6
DEFLATED = 8
ENHANCED_DEFLATED = 9
PKWARE = 10
BZIP2 = 12
LZMA = 14
IBM_TERSE = 18
IBM_LZ77 = 19

# General purpose bit flag values
# (For example, the bit 3 (0x08) indicates that the CRC/size fields are not set in the header.)
FLG_ENTRY_ENC = 1

# Special values for zip64 structures
EF_ZIP64_OR_32 = 0xFFFFFFFF
EF_ZIP64_OR_16 = 0xFFFF

# Extra field header IDs
ID_ZIP64 = 0x0001
ID_AVINFO = 0x0007
ID_PFS = 0x0008
ID_OS2 = 0x0009
ID_NTFS = 0x000A
ID_OPENVMS = 0x000C
ID_UNIX = 0x000D
ID_FORK = 0x000E
ID_PATCH = 0x000F
ID_X509_PKCS7 = 0x0014
ID_X509_CERTID_F = 0x0015
ID_X509_CERTID_C = 0x0016
ID_STRONGENC = 0x0017
ID_RECORD_MGT = 0x0018
ID_X509_PKCS7_RL = 0x0019
ID_IBM1 = 0x0065
ID_IBM2 = 0x0066
ID_POSZIP = 0x4690
ID_UNICODE_PATH = 0x7075
