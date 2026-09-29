from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx
from app.config import settings
from app.core.security import validate_public_http_url

class FetchError(RuntimeError):
    pass

async def robots_allowed(client: httpx.AsyncClient, url: str) -> bool:
    if not settings.respect_robots_txt:
        return True

    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        response = await client.get(robots_url, follow_redirects=True)
        if response.status_code >= 400:
            return True

        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(response.text.splitlines())
        return parser.can_fetch(settings.user_agent, url)

    except httpx.HTTPError:
        return True

async def fetch_html(url: str) -> str:
    validate_public_http_url(url)

    timeout = httpx.Timeout(settings.fetch_timeout_seconds)
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)

    async with httpx.AsyncClient(
        headers={"User-Agent": settings.user_agent},
        timeout=timeout,
        limits=limits,
        follow_redirects=True,
    ) as client:
        if not await robots_allowed(client, url):
            raise FetchError("robots.txt does not allow this crawler to fetch the URL")

        response = await client.get(url)
        response.raise_for_status()

        validate_public_http_url(str(response.url))

        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type:
            raise FetchError(f"Unsupported content type: {content_type or 'unknown'}")

        if len(response.content) > settings.max_response_bytes:
            raise FetchError("Response exceeds configured size limit")

        return response.text
