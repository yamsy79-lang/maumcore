"""HWP 5.0 문서에서 본문 텍스트를 추출합니다 (olefile + zlib).

사용법: python tools/hwp_to_text.py 원고.hwp > 원고.txt
"""
import struct
import sys
import zlib

import olefile

HWPTAG_PARA_TEXT = 67
# 인라인/확장 컨트롤 문자: 뒤에 7개의 WCHAR(14바이트)가 따라붙는다
EXTENDED_CTRL = {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23}


def _records(data):
    pos = 0
    while pos + 4 <= len(data):
        header = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        tag, size = header & 0x3FF, (header >> 20) & 0xFFF
        if size == 0xFFF:
            size = struct.unpack_from("<I", data, pos)[0]
            pos += 4
        yield tag, data[pos:pos + size]
        pos += size


def _para_text(payload):
    out, i = [], 0
    while i + 2 <= len(payload):
        ch = struct.unpack_from("<H", payload, i)[0]
        i += 2
        if ch in EXTENDED_CTRL:
            if ch == 9:
                out.append("\t")
            i += 14
        elif ch in (10, 13):
            continue
        elif ch < 32:
            continue
        else:
            out.append(chr(ch))
    return "".join(out)


def extract(path):
    ole = olefile.OleFileIO(path)
    header = ole.openstream("FileHeader").read()
    compressed = bool(struct.unpack_from("<I", header, 36)[0] & 1)
    sections = sorted(
        (e for e in ole.listdir() if e[0] == "BodyText"),
        key=lambda e: int(e[1].replace("Section", "")),
    )
    lines = []
    for entry in sections:
        raw = ole.openstream(entry).read()
        data = zlib.decompress(raw, -15) if compressed else raw
        for tag, payload in _records(data):
            if tag == HWPTAG_PARA_TEXT:
                lines.append(_para_text(payload))
    return "\n".join(lines)


if __name__ == "__main__":
    sys.stdout.write(extract(sys.argv[1]) + "\n")
