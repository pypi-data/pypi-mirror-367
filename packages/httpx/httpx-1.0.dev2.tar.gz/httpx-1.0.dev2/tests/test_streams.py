import httpx
import pytest


def byteiterator(buffer=b""):
    for num in buffer:
        yield chr(num)


def test_bytestream():
    s = httpx.ByteStream(b"1234567890")
    assert repr(s) == "<ByteStream [10B]>"
    assert s.size == 10

    s = httpx.ByteStream(b"1234567890" * 1024)
    assert repr(s) == "<ByteStream [10KB]>"
    assert s.size == 10 * 1024

    s = httpx.ByteStream(b"1234567890" * 1024 * 1024)
    assert repr(s) == "<ByteStream [10MB]>"
    assert s.size == 10 * 1024 * 1024


def test_bytestream_iter():
    s = httpx.ByteStream(b"1234567890")
    for _ in s:
        assert _ == b"1234567890"


def test_iterbytestream_unknown_size():
    s = httpx.IterByteStream(byteiterator(b"1234567890"))
    assert s.size == None
    assert repr(s) == "<IterByteStream [0% of ???]>"

    for _ in s:
        assert repr(s) == "<IterByteStream [???% of ???]>"
    assert repr(s) == "<IterByteStream [100% of 10B]>"


def test_iterbytestream_fixed_size():
    s = httpx.IterByteStream(byteiterator(b"1234567890"), size=10)
    assert s.size == 10
    assert repr(s) == "<IterByteStream [0% of 10B]>"

    for idx, _ in enumerate(s, start=1):
        percent = idx * 10
        assert repr(s) == f"<IterByteStream [{percent}% of 10B]>"
    assert repr(s) == "<IterByteStream [100% of 10B]>"


def test_iterbytestream_validates_size():
    s = httpx.IterByteStream(byteiterator(b"1234567890"), size=5)
    with pytest.raises(ValueError):
        for _ in s:
            pass

    s = httpx.IterByteStream(byteiterator(b"1234567890"), size=15)
    with pytest.raises(ValueError):
        for _ in s:
            pass


def test_humanized_size_repr():
    s = httpx.IterByteStream(byteiterator(), size=1)
    assert repr(s) == "<IterByteStream [0% of 1B]>"

    s = httpx.IterByteStream(byteiterator(), size=1024)
    assert repr(s) == "<IterByteStream [0% of 1KB]>"

    s = httpx.IterByteStream(byteiterator(), size=1024 ** 2)
    assert repr(s) == "<IterByteStream [0% of 1MB]>"

    s = httpx.IterByteStream(byteiterator(), size=1024 ** 3)
    assert repr(s) == "<IterByteStream [0% of 1GB]>"

    s = httpx.IterByteStream(byteiterator(), size=1024 ** 4)
    assert repr(s) == "<IterByteStream [0% of 1TB]>"


def test_stream_interface():
    stream = httpx.Stream()

    with pytest.raises(NotImplementedError):
        stream.size

    with pytest.raises(NotImplementedError):
        [_ for _ in stream]
