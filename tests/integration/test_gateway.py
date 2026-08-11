"""Testes da camada de integração (gateway)."""

from app.integration import YelenaGateway, ProcessMessageRequest


def test_gateway_start_process_stop():
    gw = YelenaGateway()
    gw.start()
    assert gw.state == "ready"

    resp = gw.process(ProcessMessageRequest(message="oi", user_id="u1"))
    assert resp.text
    assert resp.request_id
    assert isinstance(resp.to_dict(), dict)

    health = gw.health()
    assert health["state"] == "ready"

    gw.stop()
    assert gw.state == "stopped"


def test_gateway_process_dict():
    gw = YelenaGateway()
    gw.start()
    resp = gw.process({
        "message": "oi",
        "user_id": "discord:1",
        "channel": "discord",
    })
    assert resp.text
    gw.stop()


def test_gateway_process_string():
    gw = YelenaGateway()
    gw.start()
    resp = gw.process("oi")
    assert resp.text
    gw.stop()
