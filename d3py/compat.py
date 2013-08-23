import sys

PY2 = sys.version_info[0] == 2


if not PY2:
    text_type = str
    string_type = (str,)

    def to_bytes(s):
        return bytes(str(s), "utf-8")

    from io import BytesIO as StringIO
    from http.server import SimpleHTTPRequestHandler
    import socketserver

else:
    text_type = unicode
    string_types = (str, unicode)

    def to_bytes(s):
        return s

    from cStringIO import StringIO
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    import SocketServer as socketserver
