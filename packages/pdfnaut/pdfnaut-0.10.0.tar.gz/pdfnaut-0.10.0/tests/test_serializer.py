# Unit Tests for serializing the COS syntax seen in PDFs
#
# The main assumption made is that EOLs are CRLF by default.

from __future__ import annotations

from pdfnaut.cos import PdfParser
from pdfnaut.cos.objects import (
    FreeXRefEntry,
    InUseXRefEntry,
    PdfArray,
    PdfComment,
    PdfDictionary,
    PdfHexString,
    PdfName,
    PdfNull,
    PdfReference,
    PdfStream,
)
from pdfnaut.cos.objects.xref import PdfXRefSection
from pdfnaut.cos.serializer import PdfSerializer, serialize


def test_comment() -> None:
    assert serialize(PdfComment(b"Comment")) == b"%Comment"


def test_null_and_boolean() -> None:
    assert serialize(True) == b"true"
    assert serialize(False) == b"false"
    assert serialize(PdfNull()) == b"null"


def test_numeric() -> None:
    assert serialize(-1) == b"-1"
    assert serialize(-5.402) == b"-5.402"
    assert serialize(46) == b"46"
    assert serialize(3.1415) == b"3.1415"


def test_name_object() -> None:
    assert serialize(PdfName(b"Type")) == b"/Type"
    assert serialize(PdfName(b"Lime Green")) == b"/Lime#20Green"
    assert serialize(PdfName(b"F#")) == b"/F#23"


def test_literal_string() -> None:
    # Basic string
    assert serialize(b"The quick brown fox") == b"(The quick brown fox)"

    # Nested parenthesis
    assert serialize(b"(Hello world)") == b"(\\(Hello world\\))"
    assert serialize(b"(Hello again))") == b"(\\(Hello again\\)\\))"

    # Escape characters
    assert (
        serialize(b"This is a string with a \t character and a + sign.")
        == b"(This is a string with a \\t character and a + sign.)"
    )

    # keep_ascii
    assert serialize(b"Espa\xf1ol", params={"keep_ascii": True}) == b"(Espa\\361ol)"


def test_hex_string() -> None:
    assert serialize(PdfHexString(b"A5B2FF")) == b"<A5B2FF>"


def test_dictionary() -> None:
    assert (
        serialize(
            PdfDictionary(
                {
                    "Type": PdfName(b"Catalog"),
                    "Metadata": PdfReference(2, 0),
                    "Pages": PdfReference(3, 0),
                }
            )
        )
        == b"<</Type /Catalog /Metadata 2 0 R /Pages 3 0 R>>"
    )


def test_array() -> None:
    assert (
        serialize(PdfArray([45, PdfDictionary({"Size": 40}), b"data"]))
        == b"[45 <</Size 40>> (data)]"
    )
    assert serialize(PdfArray([PdfName(b"XYZ"), 45, 32, 76])) == b"[/XYZ 45 32 76]"


def test_stream() -> None:
    # Make sure it's written correctly
    stream = PdfStream(PdfDictionary({"Length": 11}), b"Hello World")
    assert (
        serialize(stream, params={"eol": b"\r\n"})
        == b"<</Length 11>>\r\nstream\r\nHello World\r\nendstream"
    )

    # Make sure filters are applied
    stream = PdfStream.create(b"Hello, world!", PdfDictionary({"Filter": PdfName(b"FlateDecode")}))
    assert serialize(stream, params={"eol": b"\r\n"}) == (
        b"<</Filter /FlateDecode /Length 21>>\r\n"
        + b"stream\r\n"
        + b"x\x9c\xf3H\xcd\xc9\xc9\xd7Q(\xcf/\xcaIQ\x04\x00 ^\x04\x8a\r\n"
        + b"endstream"
    )
    assert stream.decode() == b"Hello, world!"


def test_serialize_document() -> None:
    serializer = PdfSerializer()
    serializer.write_header("1.7")
    assert serializer.content.startswith(b"%PDF-1.7\r\n")
    before_object = len(serializer.content)

    object_start = serializer.write_object((1, 0), PdfDictionary({"A": b"BC", "D": 10.24}))
    assert before_object == object_start
    assert serializer.content.endswith(b"1 0 obj\r\n<</A (BC) /D 10.24>>\r\nendobj\r\n")

    subsections = serializer.generate_xref_section(
        [(0, FreeXRefEntry(0, 65535)), (1, InUseXRefEntry(object_start, 0))]
    )
    assert (
        len(subsections)
        and subsections[0].first_obj_number == 0
        and subsections[0].count == 2
        and isinstance(subsections[0].entries[0], FreeXRefEntry)
        and isinstance(subsections[0].entries[1], InUseXRefEntry)
    )

    before_xref = len(serializer.content)
    startxref = serializer.write_standard_xref_section(subsections)
    assert before_xref == startxref

    serializer.write_trailer(PdfDictionary({"Size": 2}), startxref)
    assert serializer.content.endswith(
        b"trailer\r\n<</Size 2>>\r\n" + b"startxref\r\n" + str(startxref).encode() + b"\r\n"
    )
    serializer.write_eof()
    assert serializer.content.endswith(b"%%EOF\r\n")


def test_serialize_compressed_table() -> None:
    serializer = PdfSerializer()
    serializer.write_header("1.7")

    object_start = serializer.write_object((1, 0), PdfDictionary({"A": b"BC", "D": 10.24}))

    subsections = serializer.generate_xref_section(
        [(0, FreeXRefEntry(0, 65535)), (1, InUseXRefEntry(object_start, 0))]
    )

    before_xref = len(serializer.content)
    startxref = serializer.write_compressed_xref_section(
        PdfXRefSection(subsections, PdfDictionary({"Size": 2}))
    )
    assert before_xref == startxref

    obj = PdfParser(serializer.content[startxref:]).parse_indirect_object(
        InUseXRefEntry(0, 0), None
    )
    assert isinstance(obj, PdfStream)
    assert obj.details == {
        "Type": PdfName(b"XRef"),
        "W": [1, 1, 2],
        "Index": [0, 2],
        "Length": 8,
        "Size": 2,
    }
    assert obj.decode() == b"\x00\x00\xff\xff\x01\x11\x00\x00"

    serializer.write_trailer(startxref=startxref)
    serializer.write_eof()

    assert serializer.content.endswith(
        b"startxref\r\n" + str(startxref).encode() + b"\r\n%%EOF\r\n"
    )
