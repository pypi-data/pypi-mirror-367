import httpx


def byteiterator(buffer=b""):
    for num in buffer:  # pragma: nocover
        yield chr(num)


def test_response():
    r = httpx.Response(200)

    assert repr(r) == "<Response [200 OK]>"
    assert r.status_code == 200
    assert r.headers == {'Content-Length': '0'}
    assert r.stream == httpx.ByteStream(b"")


def test_response_204():
    r = httpx.Response(204)

    assert repr(r) == "<Response [204 No Content]>"
    assert r.status_code == 204
    assert r.headers == {}
    assert r.stream == httpx.ByteStream(b"")


def test_response_bytes():
    content = b"Hello, world"
    r = httpx.Response(200, content=content)

    assert repr(r) == "<Response [200 OK]>"
    assert r.headers == {
        "Content-Length": "12",
    }
    assert r.stream == httpx.ByteStream(b"Hello, world")


def test_response_stream():
    stream = httpx.IterByteStream(byteiterator(b"Hello, world"))
    r = httpx.Response(200, content=stream)

    assert repr(r) == "<Response [200 OK]>"
    assert r.headers == {
        "Transfer-Encoding": "chunked",
    }
    assert r.stream is stream


def test_response_json():
    data = httpx.JSON({"msg": "Hello, world"})
    r = httpx.Response(200, content=data)

    assert repr(r) == "<Response [200 OK]>"
    assert r.headers == {
        "Content-Length": "22",
        "Content-Type": "application/json",
    }
    assert r.stream == httpx.ByteStream(b'{"msg":"Hello, world"}')
