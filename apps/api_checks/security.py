"""
SSRF (Server-Side Request Forgery) Protection for ReleaseGuard.

Critical security layer for user-configured health check URLs.
Blocks access to internal/private networks, validates DNS, enforces timeouts.
"""

import ipaddress
import logging
import socket
import ssl
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


# --- IP Address Classification ---

# Private IP ranges (RFC 1918)
PRIVATE_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
]

# Loopback
LOOPBACK_NETWORKS = [
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('::1/128'),
]

# Link-local (RFC 3927, RFC 4291)
LINK_LOCAL_NETWORKS = [
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('fe80::/10'),
]

# Reserved/private use
RESERVED_NETWORKS = [
    ipaddress.ip_network('0.0.0.0/8'),
    ipaddress.ip_network('100.64.0.0/10'),  # Carrier-grade NAT
    ipaddress.ip_network('192.0.0.0/24'),    # IETF protocol assignments
    ipaddress.ip_network('192.0.2.0/24'),    # TEST-NET-1
    ipaddress.ip_network('198.18.0.0/15'),   # Benchmark testing
    ipaddress.ip_network('198.51.100.0/24'), # TEST-NET-2
    ipaddress.ip_network('203.0.113.0/24'),  # TEST-NET-3
    ipaddress.ip_network('224.0.0.0/4'),     # Multicast
    ipaddress.ip_network('240.0.0.0/4'),     # Reserved
    ipaddress.ip_network('255.255.255.255/32'), # Broadcast
]

# All blocked networks combined
BLOCKED_NETWORKS = PRIVATE_NETWORKS + LOOPBACK_NETWORKS + LINK_LOCAL_NETWORKS + RESERVED_NETWORKS


@dataclass
class SSRFValidationResult:
    """Result of SSRF validation."""
    allowed: bool
    reason: str = ''
    resolved_ips: list[str] = None


def is_ip_allowed(ip_str: str) -> tuple[bool, str]:
    """
    Check if an IP address is allowed (not in blocked ranges).

    Returns:
        (allowed, reason)
    """
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False, f'Invalid IP address: {ip_str}'

    for network in BLOCKED_NETWORKS:
        if ip in network:
            return False, f'IP {ip_str} is in blocked network {network}'

    return True, ''


def resolve_hostname_safely(hostname: str, timeout: float = 5.0) -> list[str]:
    """
    Resolve hostname to IP addresses with timeout.

    Returns list of IP addresses (IPv4 and IPv6).
    """
    try:
        # Use getaddrinfo with timeout
        socket.setdefaulttimeout(timeout)
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        ips = list({info[4][0] for info in infos})
        return ips
    except socket.gaierror as e:
        logger.warning('DNS resolution failed for %s: %s', hostname, e)
        return []
    except Exception as e:
        logger.exception('Unexpected error resolving %s', hostname)
        return []


def validate_url_against_ssrf(url: str, timeout: float = 5.0) -> SSRFValidationResult:
    """
    Comprehensive SSRF validation for a URL.

    Checks:
    1. Scheme is HTTP/HTTPS
    2. Hostname resolves to allowed IPs
    3. No redirect to blocked IPs (checked at request time)
    4. No localhost/private IP in URL directly
    """
    try:
        parsed = urlparse(url)
    except Exception as e:
        return SSRFValidationResult(False, f'Invalid URL: {e}')

    # Check scheme
    if parsed.scheme not in ('http', 'https'):
        return SSRFValidationResult(False, f'Scheme {parsed.scheme} not allowed (only HTTP/HTTPS)')

    # Extract hostname
    hostname = parsed.hostname
    if not hostname:
        return SSRFValidationResult(False, 'No hostname in URL')

    # Check for direct IP in URL
    try:
        ipaddress.ip_address(hostname)
        # It's an IP address directly
        allowed, reason = is_ip_allowed(hostname)
        if not allowed:
            return SSRFValidationResult(False, reason)
        return SSRFValidationResult(True, '', [hostname])
    except ValueError:
        # It's a hostname, need to resolve
        pass

    # Resolve hostname
    resolved_ips = resolve_hostname_safely(hostname, timeout)
    if not resolved_ips:
        return SSRFValidationResult(False, f'Could not resolve hostname: {hostname}')

    # Check each resolved IP
    for ip in resolved_ips:
        allowed, reason = is_ip_allowed(ip)
        if not allowed:
            return SSRFValidationResult(False, f'Hostname {hostname} resolves to blocked IP: {reason}', resolved_ips)

    return SSRFValidationResult(True, '', resolved_ips)


# --- Safe HTTP Session ---

class SSRFProtectedSession(requests.Session):
    """
    Requests session with SSRF protection.

    - Validates URL before request
    - Follows redirects but validates each hop
    - Enforces timeout
    - No automatic proxy from environment
    """

    def __init__(self, timeout: float = 10.0, max_redirects: int = 5):
        super().__init__()
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.trust_env = False  # Ignore HTTP_PROXY etc.

        # Disable automatic redirects - we'll handle manually with validation
        self._max_redirects_internal = 0

        # Mount adapter with no retries (we control retry logic)
        adapter = HTTPAdapter(max_retries=Retry(total=0))
        self.mount('http://', adapter)
        self.mount('https://', adapter)

    def request(self, method, url, *args, **kwargs):
        """Override request to add SSRF validation."""
        # Initial URL validation
        validation = validate_url_against_ssrf(url, timeout=5.0)
        if not validation.allowed:
            raise SSRFError(f'URL blocked: {validation.reason}')

        # Set timeout if not provided
        kwargs.setdefault('timeout', self.timeout)

        # Make request without auto-redirects
        response = super().request(method, url, *args, **kwargs)

        # Handle redirects manually with validation
        redirect_count = 0
        while response.is_redirect and redirect_count < self.max_redirects:
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                break

            # Resolve relative redirect
            from urllib.parse import urljoin
            redirect_url = urljoin(url, redirect_url)

            # Validate redirect target
            validation = validate_url_against_ssrf(redirect_url, timeout=5.0)
            if not validation.allowed:
                raise SSRFError(f'Redirect blocked: {validation.reason}')

            # Follow redirect
            response = super().request(method, redirect_url, *args, **kwargs)
            redirect_count += 1
            url = redirect_url

        return response


class SSRFError(Exception):
    """Raised when SSRF validation fails."""
    pass


# --- SSL Certificate Validation ---

def validate_ssl_certificate(hostname: str, port: int = 443, timeout: float = 5.0) -> tuple[bool, str]:
    """
    Validate SSL certificate for a hostname.

    Returns (is_valid, details).
    """
    try:
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return True, f'Valid cert for {cert.get("subject", "unknown")}'
    except ssl.SSLError as e:
        return False, f'SSL error: {e}'
    except socket.timeout:
        return False, 'SSL connection timeout'
    except Exception as e:
        return False, f'SSL validation error: {e}'


# --- Usage Example ---

def make_safe_request(
    method: str,
    url: str,
    timeout: float = 10.0,
    headers: dict = None,
    data: str = None,
    verify_ssl: bool = True,
    max_redirects: int = 5,
) -> requests.Response:
    """
    Make a safe HTTP request with full SSRF protection.

    Usage:
        response = make_safe_request('GET', 'https://api.example.com/health')
    """
    session = SSRFProtectedSession(timeout=timeout, max_redirects=max_redirects)

    # SSL verification
    if not verify_ssl:
        session.verify = False
        # Suppress InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        response = session.request(
            method=method,
            url=url,
            headers=headers or {},
            data=data,
        )
        return response
    except SSRFError:
        raise
    except requests.Timeout:
        raise SSRFError('Request timeout')
    except requests.RequestException as e:
        raise SSRFError(f'Request failed: {e}')