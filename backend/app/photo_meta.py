"""Strip metadata out of uploaded photos.

Camera-roll originals carry EXIF, and EXIF carries GPS coordinates. Every
photo in a game is served to everyone in the room, so shipping that metadata
through would hand the other players the street the picture was taken on —
which is a considerably bigger disclosure than the picture itself.

The iOS client happens to re-encode through photo_manager's thumbnail
pipeline, which drops EXIF as a side effect. That is a property of one client
on one platform, not a guarantee: the Android client, a future web client or
anything talking to the API directly would all bypass it. So the server does
the stripping, and the privacy property holds for every caller.

This is deliberately structural rather than a Pillow dependency: it walks the
container's segment/chunk headers and drops the metadata ones, leaving the
compressed image data untouched. There is no decode, so nothing is re-encoded
and no quality is lost — and no image library is in the trust path for
attacker-supplied bytes.
"""

from __future__ import annotations

import struct

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

# JPEG APPn markers (0xE0-0xEF) hold EXIF (APP1), XMP (APP1), Photoshop/IPTC
# (APP13) and friends; COM (0xFE) is a free-text comment. APP0 is the JFIF
# header, which is structural rather than metadata, so it stays.
_JPEG_DROP = set(range(0xE1, 0xF0)) | {0xFE}
# Markers that carry no length field and are copied verbatim.
_JPEG_STANDALONE = {0x01} | set(range(0xD0, 0xD8))

# PNG chunks that carry text or metadata. Everything else — IHDR, PLTE, IDAT,
# transparency, colour management — affects how the image decodes and stays.
_PNG_DROP = {b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"tIME", b"dSIG"}


def strip_metadata(data: bytes) -> bytes:
    """Return [data] with its metadata segments removed.

    Only JPEG and PNG are recognised, which is exactly what the upload
    endpoint accepts. Anything else, or anything malformed, is returned
    unchanged: this is a privacy filter, not a validator, and rejecting is the
    caller's job.
    """
    if data.startswith(b"\xff\xd8\xff"):
        return _strip_jpeg(data)
    if data.startswith(_PNG_MAGIC):
        return _strip_png(data)
    return data


def _strip_jpeg(data: bytes) -> bytes:
    out = bytearray(data[:2])  # SOI
    i = 2
    n = len(data)
    while i + 1 < n:
        if data[i] != 0xFF:
            # Not on a marker boundary; the file is malformed from here on, so
            # copy the rest verbatim rather than guessing.
            out += data[i:]
            return bytes(out)
        marker = data[i + 1]
        if marker == 0xFF:  # fill byte
            out.append(0xFF)
            i += 1
            continue
        if marker in _JPEG_STANDALONE:
            out += data[i : i + 2]
            i += 2
            continue
        if marker == 0xDA:  # start of scan: entropy-coded data to the end
            out += data[i:]
            return bytes(out)
        if i + 4 > n:
            out += data[i:]
            return bytes(out)
        (length,) = struct.unpack(">H", data[i + 2 : i + 4])
        if length < 2 or i + 2 + length > n:
            out += data[i:]
            return bytes(out)
        if marker not in _JPEG_DROP:
            out += data[i : i + 2 + length]
        i += 2 + length
    out += data[i:]
    return bytes(out)


def _strip_png(data: bytes) -> bytes:
    out = bytearray(_PNG_MAGIC)
    i = len(_PNG_MAGIC)
    n = len(data)
    while i + 8 <= n:
        (length,) = struct.unpack(">I", data[i : i + 4])
        kind = data[i + 4 : i + 8]
        end = i + 12 + length  # length + type + data + crc
        if end > n:
            out += data[i:]
            return bytes(out)
        if kind not in _PNG_DROP:
            out += data[i:end]
        i = end
        if kind == b"IEND":
            break
    return bytes(out)
