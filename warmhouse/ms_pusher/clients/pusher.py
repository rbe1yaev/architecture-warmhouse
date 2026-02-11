import hashlib
import hmac
import time

import httpx
import ujson as json

__all__ = ("trigger_event",)

from warmhouse.ms_pusher.settings import PUSHER_APP_ID, PUSHER_CLUSTER, PUSHER_KEY, PUSHER_SECRET

AUTH_VERSION = "1.0"
API_URL = "https://api-%s.pusher.com" % PUSHER_CLUSTER
TIMEOUT = 8


class TriggerEventError(Exception):
    pass


def get_path(app_id):
    return "/apps/%s/events" % app_id


def get_md5_body(body):
    m = hashlib.md5()
    m.update(body.encode())

    return m.hexdigest()


def generate_signature(
    path=None,
    auth_key=None,
    auth_version=None,
    auth_secret=None,
    timestamp=None,
    md5_body=None,
):
    s = "POST\n%s\nauth_key=%s&auth_timestamp=%s&auth_version=%s&body_md5=%s" % (
        path,
        auth_key,
        timestamp,
        auth_version,
        md5_body,
    )

    return hmac.new(
        auth_secret.encode(),
        msg=s.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()


async def trigger_event(channel, event_name, event_data):

    payload = {
        "channel": channel,
        "name": event_name,
        "data": json.dumps(event_data),
    }
    event_body = json.dumps(payload)
    md5_body = get_md5_body(event_body)
    timestamp = int(time.time())
    signature = generate_signature(
        path=get_path(PUSHER_APP_ID),
        auth_key=PUSHER_KEY,
        auth_version=AUTH_VERSION,
        timestamp=timestamp,
        md5_body=md5_body,
        auth_secret=PUSHER_SECRET,
    )

    async with httpx.AsyncClient() as client:
        await client.post(
            API_URL + get_path(PUSHER_APP_ID),
            params={
                "auth_key": PUSHER_KEY,
                "auth_timestamp": timestamp,
                "auth_signature": signature,
                "auth_version": AUTH_VERSION,
                "body_md5": md5_body,
            },
            headers={
                "content-type": "application/json",
            },
            json=payload,
            timeout=TIMEOUT,
        )

    return
