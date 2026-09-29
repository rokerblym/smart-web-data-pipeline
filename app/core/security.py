import ipaddress
import socket
from urllib.parse import urlparse

class UnsafeURLError(ValueError):
    pass

def validate_public_http_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise UnsafeURLError("Only http and https URLs are allowed")

    if not parsed.hostname:
        raise UnsafeURLError("URL must contain a hostname")

    hostname = parsed.hostname.lower()
    if hostname in {"localhost", "localhost.localdomain"}:
        raise UnsafeURLError("Localhost URLs are not allowed")

    try:
        infos = socket.getaddrinfo(
            hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
        )
    except socket.gaierror as exc:
        raise UnsafeURLError("Hostname could not be resolved") from exc

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise UnsafeURLError(f"Refusing non-public address: {ip}")
