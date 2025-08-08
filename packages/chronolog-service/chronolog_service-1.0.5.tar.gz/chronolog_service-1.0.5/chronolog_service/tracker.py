import redis
import json
from datetime import datetime
from typing import Optional

def track_version(redis_url: str, service_name: str, version: str, metadata: Optional[dict] = None):
    client = redis.Redis.from_url(redis_url)
    data = {
        "version": version,
        "timestamp": datetime.utcnow().isoformat()
    }
    if metadata:
        data["metadata"] = metadata
    key = f"chronolog:service:{service_name}"
    client.sadd("chronolog:services", key)
    client.set(key, json.dumps(data))
    print(f"[Chronolog] Logged {service_name} - {version}")