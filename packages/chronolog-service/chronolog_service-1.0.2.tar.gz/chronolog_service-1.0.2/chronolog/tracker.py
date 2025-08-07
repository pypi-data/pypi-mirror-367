import redis
import json
from datetime import datetime
from typing import Optional

class Chronolog:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client = redis.Redis.from_url(redis_url)

    def track_version(self, service_name: str, version: str, metadata: Optional[dict] = None):
        data = {
            "version": version,
            "timestamp": datetime.utcnow().isoformat()
        }

        if metadata:
            data["metadata"] = metadata

        # When saving a service:
        key = f"chronolog:service:{service_name}"
        self.client.sadd("chronolog:services", key)
        self.client.set(key, json.dumps(data))
        print(f"[Chronolog] Logged {service_name} - {version}")
