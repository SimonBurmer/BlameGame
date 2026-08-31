"""EXIF/GPS must not survive an upload.

Every photo in a room is served to everyone in it, so metadata that names
where the picture was taken is a bigger disclosure than the picture. These
build real container bytes rather than mocking, because the stripper walks the
container structure and a mock would only test the mock.
"""

import struct

from app.photo_meta import strip_metadata


def _jpeg(*segments: bytes, scan: bytes = b"\xff\xda\x00\x08body\xff\xd9") -> bytes:
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + b"".join(segments) + scan


def _segment(marker: int, payload: bytes) -> bytes:
    return bytes([0xFF, marker]) + struct.pack(">H", len(payload) + 2) + payload


# An APP1 whose payload is an Exif TIFF header carrying a GPS IFD pointer —
# the shape a phone camera actually writes.
_EXIF_GPS = _segment(
    0xE1,
    b"Exif\x00\x00"
    + b"II*\x00\x08\x00\x00\x00"  # little-endian TIFF header
    + b"\x01\x00"  # one IFD entry
    + b"\x25\x88\x04\x00\x01\x00\x00\x00\x1a\x00\x00\x00"  # GPSInfo -> offset
    + b"\x00\x00\x00\x00",
)


def _png(*chunks: bytes) -> bytes:
    header = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = _chunk(b"IDAT", b"\x78\x9c\x63\x00\x00\x00\x01\x00\x01")
    return header + ihdr + b"".join(chunks) + idat + _chunk(b"IEND", b"")


def _chunk(kind: bytes, payload: bytes) -> bytes:
    import zlib

    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def test_jpeg_gps_exif_is_removed():
    stripped = strip_metadata(_jpeg(_EXIF_GPS))

    assert b"Exif" not in stripped
    assert b"\x25\x88" not in stripped  # the GPSInfo tag id


def test_jpeg_keeps_the_image_itself():
    original = _jpeg(_EXIF_GPS)
    stripped = strip_metadata(original)

    assert stripped.startswith(b"\xff\xd8\xff")
    assert stripped.endswith(b"\xff\xd9")
    # JFIF is structural, not metadata, and the scan data is the picture.
    assert b"JFIF" in stripped
    assert b"body" in stripped
    assert len(stripped) < len(original)


def test_jpeg_xmp_and_comments_go_too():
    stripped = strip_metadata(
        _jpeg(
            _segment(0xE1, b"http://ns.adobe.com/xap/1.0/\x00<x:xmpmeta/>"),
            _segment(0xFE, b"shot on a phone at home"),
        )
    )

    assert b"xmpmeta" not in stripped
    assert b"shot on a phone" not in stripped


def test_a_photo_with_no_metadata_is_untouched():
    clean = _jpeg()

    assert strip_metadata(clean) == clean


def test_png_text_and_exif_chunks_are_removed():
    original = _png(
        _chunk(b"eXIf", b"II*\x00gps-goes-here"),
        _chunk(b"tEXt", b"Comment\x0056.3 N, 10.7 E"),
    )
    stripped = strip_metadata(original)

    assert b"gps-goes-here" not in stripped
    assert b"56.3 N" not in stripped
    # The chunks that decode the image survive.
    assert b"IHDR" in stripped
    assert b"IDAT" in stripped
    assert stripped.endswith(_chunk(b"IEND", b""))


def test_unrecognised_bytes_pass_through():
    # The stripper is a privacy filter, not a validator: the upload endpoint
    # is what rejects anything that isn't a JPEG or PNG.
    assert strip_metadata(b"not an image") == b"not an image"


def test_truncated_jpeg_does_not_raise():
    assert strip_metadata(b"\xff\xd8\xff\xe1\x00") == b"\xff\xd8\xff\xe1\x00"


def test_truncated_png_does_not_raise():
    truncated = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 999) + b"IHDR"
    assert strip_metadata(truncated) == truncated
