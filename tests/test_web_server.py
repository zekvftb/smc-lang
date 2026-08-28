"""Automated unit test for DexterVM native HTTP Web Server capabilities."""

import threading
import time
import urllib.error
import urllib.request
import pytest

from smc.lexer import SmcLexer
from smc.parser import SmcParser
from smc.vm import DexterVM


def test_serve_http_routes_and_responses():
    """Verify serve_http handles requests, matches paths, and returns structured responses."""
    code = (
        "fn handle_web(req) {\n"
        "    let p = req['path']\n"
        "    if (p == '/hello') {\n"
        "        return {'status': 200, 'content_type': 'text/html', 'body': '<h1>Hello from SMC!</h1>'}\n"
        "    }\n"
        "    if (p == '/api/ping') {\n"
        "        return {'status': 200, 'content_type': 'application/json', 'body': '{\"pong\": true}'}\n"
        "    }\n"
        "    return {'status': 404, 'content_type': 'text/plain', 'body': 'Not Found'}\n"
        "}\n"
        "serve_http(8999, 'handle_web', 3)\n"
        "halt\n"
    )

    tokens = SmcLexer(code).tokenize()
    ast = SmcParser(tokens).parse()
    vm = DexterVM()

    # Launch server in background thread for 3 requests
    server_thread = threading.Thread(target=vm.run, args=(ast,), daemon=True)
    server_thread.start()
    time.sleep(0.3)  # Wait for socket to bind

    # 1. Test GET /hello
    req1 = urllib.request.Request("http://localhost:8999/hello")
    with urllib.request.urlopen(req1, timeout=3) as resp1:
        assert resp1.status == 200
        assert resp1.headers.get("Content-Type") == "text/html"
        assert "<h1>Hello from SMC!</h1>" in resp1.read().decode("utf-8")

    # 2. Test GET /api/ping
    req2 = urllib.request.Request("http://localhost:8999/api/ping")
    with urllib.request.urlopen(req2, timeout=3) as resp2:
        assert resp2.status == 200
        assert resp2.headers.get("Content-Type") == "application/json"
        assert '{"pong": true}' in resp2.read().decode("utf-8")

    # 3. Test GET /unknown (404)
    req3 = urllib.request.Request("http://localhost:8999/unknown")
    try:
        urllib.request.urlopen(req3, timeout=3)
    except urllib.error.HTTPError as e:
        assert e.code == 404
        assert "Not Found" in e.read().decode("utf-8")

    server_thread.join(timeout=2)
    assert any("Laboratory server listening" in s for s in vm.stdout)
