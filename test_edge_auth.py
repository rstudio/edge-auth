import base64

import pytest

import edge_auth


def _build_edge_auth_known_users(auth_users):
    return ",".join([f"{k}:{v}" for k, v in auth_users.items()])


def _build_event(user: str, token: str) -> dict:
    encoded_auth = base64.b64encode(f"{user}:{token}".encode("utf-8")).decode("utf-8")
    return {
        "Records": [
            {
                "cf": {
                    "request": {
                        "headers": {
                            "authorization": [
                                {
                                    "key": "Authorization",
                                    "value": f"Basic {encoded_auth}",
                                }
                            ]
                        }
                    }
                }
            }
        ]
    }


@pytest.mark.parametrize(
    ["event", "known_users", "expected_request"],
    (
        pytest.param(
            {"Records": [{"cf": {"request": {}}}]},
            {"non": "empty"},
            edge_auth.ERR_401_MISSING,
            id="no_auth_401",
        ),
        pytest.param(
            {
                "Records": [
                    {
                        "cf": {
                            "request": {
                                "headers": {
                                    "authorization": [
                                        {
                                            "key": "Authorization",
                                            "value": f"Basic bmFyZgo=",
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            },
            {"poit": "narf"},
            edge_auth.ERR_401_INVALID,
            id="invalid_auth_401",
        ),
        pytest.param(
            _build_event("brian", "brain"),
            {"poit": "narf"},
            edge_auth.ERR_403_SHH,
            id="fake_403",
        ),
        pytest.param(
            _build_event("brian", "brain"),
            {"poit": "narf", "brian": "brain"},
            _build_event("brian", "brain")["Records"][0]["cf"]["request"],
            id="ok",
        ),
    ),
)
def test_handler(monkeypatch, event, known_users, expected_request):
    edge_auth.KNOWN_USERS.clear()
    monkeypatch.setenv(
        "EDGE_AUTH_KNOWN_USERS", _build_edge_auth_known_users(known_users)
    )

    assert edge_auth.handler(event, {}) == expected_request
