from chronolog import Chronolog

def test_version_log(monkeypatch):
    class MockRedis:
        def set(self, key, value):
            assert key == "chronolog:service:test-service"
            assert "1.0.0" in value

    monkeypatch.setattr("redis.Redis.from_url", lambda url: MockRedis())
    c = Chronolog("redis://mock")
    c.track_version("test-service", "1.0.0")
