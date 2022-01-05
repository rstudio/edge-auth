import base64
import json
import os
import warnings

ERR_401_MISSING = {
    "status": "401",
    "headers": {
        "www-authenticate": [
            {"key": "WWW-Authenticate", "value": 'Basic realm="auth required"'}
        ],
        "edge-auth-error": [
            {"key": "Edge-Auth-Error", "value": "missing authorization header"}
        ],
    },
}

ERR_401_INVALID = {
    "status": "400",
    "headers": {
        "edge-auth-error": [
            {"key": "Edge-Auth-Error", "value": "invalid authorization header"}
        ]
    },
}

ERR_403_SHH = {
    "status": "404",
    "headers": {
        "edge-auth-error": [{"key": "Edge-Auth-Error", "value": "nobody home"}]
    },
}


KNOWN_USERS = set()

# NOTE: KNOWN_USERS_JSON is overwritten by being appended at lambda creation time.
KNOWN_USERS_JSON = "{}"


def handler(event: dict, _context: dict) -> dict:
    try:
        if not _ensure_known_users():
            return _make_err_500("failed to load known users")

        req = event["Records"][0]["cf"]["request"]
        headers = req.get("headers", {})

        auth_header = headers.get("authorization", [{}])[0].get("value")
        if auth_header is None or not str(auth_header).lower().strip().startswith(
            "basic"
        ):
            return ERR_401_MISSING

        auth = base64.b64decode(auth_header.strip().split()[1].encode("utf-8")).decode(
            "utf-8"
        )
        if not ":" in auth:
            return ERR_401_INVALID

        user, token = auth.split(":", maxsplit=1)
        if (user, token) not in KNOWN_USERS:
            return ERR_403_SHH

        return req
    except Exception as exc:
        return _make_err_500(f"oh no: {exc}")


def _ensure_known_users() -> bool:
    if len(KNOWN_USERS) > 0:
        return True

    env_known_users = os.getenv("EDGE_AUTH_KNOWN_USERS")
    if env_known_users is not None:
        for pair in env_known_users.strip().split(","):
            user, token = pair.split(":", maxsplit=1)
            KNOWN_USERS.add((user, token))
        return len(KNOWN_USERS) > 0

    for user, token in json.loads(KNOWN_USERS_JSON).items():
        KNOWN_USERS.add((user, token))

    return len(KNOWN_USERS) > 0


def _make_err_500(msg: str) -> dict:
    return {
        "status": "500",
        "headers": {"edge-auth-error": [{"key": "Edge-Auth-Error", "value": msg}]},
    }
