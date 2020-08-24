import pytest
import requests

from requests.exceptions import ConnectionError

def is_responsive(url):
    import zmq
    context = zmq.Context()
    sock = context.socket(zmq.REQ)
    try:    
        sock.connect(url)
        return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def zmq_sock_url(docker_ip, docker_services):
    """Ensure that ZMQ REP is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("sigpyparser_zmq", 10001)
    url = "tcp://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    return url

def test_zmq_sock(zmq_sock_url):
    import zmq
    context = zmq.Context()
    sock = context.socket(zmq.REQ)
    sock.connect(zmq_sock_url)
    
    sock.send_string("BUY STOP EURUSD 1.20 SL 1.185 TP 1.22")
    response = sock.recv()
    
    import json
    payload = json.loads(response)
    assert type(payload) is dict
    assert payload.get('ok') is True

    parsed = payload.get('res')
    assert type(parsed) is dict
    
    pair = parsed.get('pair')
    assert pair == 'EURUSD'
