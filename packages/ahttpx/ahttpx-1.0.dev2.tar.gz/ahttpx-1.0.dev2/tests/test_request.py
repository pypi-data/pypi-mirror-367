import httpx


def byteiterator(buffer=b""):
    for num in buffer:  # pragma: nocover
        yield chr(num)


def test_request():
    r = httpx.Request("GET", "https://example.com")

    assert repr(r) == "<Request [GET 'https://example.com']>"
    assert r.method == "GET"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com"
    }
    assert r.stream == httpx.ByteStream(b"")

def test_request_bytes():
    content = b"Hello, world"
    r = httpx.Request("POST", "https://example.com", content=content)

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Content-Length": "12",
    }
    assert r.stream == httpx.ByteStream(b"Hello, world")


def test_request_stream():
    stream = httpx.IterByteStream(byteiterator(b"Hello, world"))
    r = httpx.Request("POST", "https://example.com", content=stream)

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Transfer-Encoding": "chunked",
    }
    assert r.stream is stream


def test_request_json():
    data = httpx.JSON({"msg": "Hello, world"})
    r = httpx.Request("POST", "https://example.com", content=data)

    assert repr(r) == "<Request [POST 'https://example.com']>"
    assert r.method == "POST"
    assert r.url == "https://example.com"
    assert r.headers == {
        "Host": "example.com",
        "Content-Length": "22",
        "Content-Type": "application/json",
    }
    assert r.stream == httpx.ByteStream(b'{"msg":"Hello, world"}')
