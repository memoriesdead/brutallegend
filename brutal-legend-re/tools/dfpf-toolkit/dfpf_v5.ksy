meta:
  id: dfpf_v5
  title: DFPF V5 Container Format (Brutal Legend)
  license: MPL-2.0
  endian: be
  encoding: UTF-8

doc: |
  DFPF V5 is a container format used by Brutal Legend.
  This specification is based on the DoubleFine Explorer Pascal source code
  by Bennyboy (http://quickandeasysoftware.net).

  The format consists of:
  - Header (88 bytes)
  - File extension table
  - File records (16 bytes each)
  - Name directory (null-terminated strings)
  - File data (in separate .~p data file)

doc-ref: http://quickandeasysoftware.net

instances:
  magic:
    pos: 0
    type: str
    size: 4
    enum: magic
    valid:
      value: dfpf

  version:
    pos: 4
    type: u1

  header:
    type: header_struct

  file_extension_table:
    pos: header.file_extension_offset
    type: file_extension_table
    if: header.file_extension_offset > 0

  file_records:
    pos: header.file_records_offset
    type: file_record
    repeat: expr
    repeat-expr: header.num_files

  name_directory:
    pos: header.name_dir_offset
    type: str
    size: header.name_dir_size
    encoding: ASCII
    term-legacy: true

types:
  magic:
    enum-as-int: true
    type: u4

  header_struct:
    doc: DFPF V5 header structure at offset 0x05
    size: 88
    fields:
      file_extension_offset:
        doc: Offset to file extension table
        type: u8
      name_dir_offset:
        doc: Offset to name directory
        type: u8
      file_extension_count:
        doc: Number of file extensions in table
        type: u4
      name_dir_size:
        doc: Size of name directory section
        type: u4
      num_files:
        doc: Number of files in archive
        type: u4
      marker1:
        doc: Marker value 0x23A1CEAB (little-endian)
        type: u4
      blank_bytes1:
        type: u4
      blank_bytes2:
        type: u4
      junk_data_offset:
        doc: Offset to junk/extra data in .~p file
        type: u8
      file_records_offset:
        doc: Offset to file record table
        type: u8
      footer_offset1:
        type: u8
      footer_offset2:
        type: u8
      unknown:
        type: u4
      marker2:
        doc: Marker value 0x23A1CEAB (little-endian)
        type: u4

  file_extension_table:
    doc: Table mapping file type indices to file extensions
    seq:
      - id: entries
        type: file_extension_entry
        repeat: expr
        repeat-expr: _root.header.file_extension_count

  file_extension_entry:
    doc: A single file extension entry
    seq:
      - id: name_length
        type: u4
        doc: Length of extension string
      - id: name
        type: str
        size: name_length
        encoding: ASCII
        doc: File extension (e.g., lua, xml)
      - id: unknown
        size: 12
        doc: Unknown bytes (padding?)

  file_record:
    doc: |
      File record entry (16 bytes).
      Contains bit-shifted fields for space optimization.
    seq:
      - id: raw_dword0
        type: u4
        doc: First dword containing uncompressed_size and part of name_offset
      - id: raw_dword1
        type: u4
        doc: Second dword containing part of name_offset and offset
      - id: raw_dword2
        type: u4
        doc: Third dword containing part of offset, size, and file_type_index
      - id: raw_dword3
        type: u4
        doc: Fourth dword containing part of file_type_index and compression_type
      - id: raw_bytes
        size: 16
        doc: Raw bytes for manual bit manipulation

    instances:
      uncompressed_size:
        doc: Uncompressed file size (bits 8-31 of raw_dword0)
        value: raw_dword0 >> 8

      name_offset:
        doc: Offset to filename in name directory (bits 11-31 of raw_dword1)
        value: raw_dword1 >> 11

      offset:
        doc: Offset to file data in .~p data file (bits 3-31 of raw_dword2)
        value: raw_dword2 >> 3

      size:
        doc: Compressed/stored size in data file (bits 9-31 of raw_dword2, shifted)
        value: (raw_dword2 << 5) >> 9

      file_type_index:
        doc: Index into file extension table
        value: ((raw_dword3 << 4) >> 24) >> 1

      compression_type:
        doc: Compression type (lower 4 bits of last byte)
        value: (raw_bytes[15]) & 0x0F

    enums:
      compression_type:
        1: uncompressed_v6
        2: zlib_v2
        4: uncompressed_v5
        8: zlib_v5
        12: xmemcompress_xbox

  compression_type_enum:
    1: uncompressed_v6
    2: zlib_v2
    4: uncompressed_v5
    8: zlib_v5
    12: xmemcompress_xbox
