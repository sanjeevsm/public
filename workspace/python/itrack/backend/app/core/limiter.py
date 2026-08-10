from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import get_settings

settings = get_settings()

# If REDIS_URL is provided, let slowapi use it for shared storage (distributed rate limiting)
if settings.REDIS_URL:
	limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)
else:
	limiter = Limiter(key_func=get_remote_address)
