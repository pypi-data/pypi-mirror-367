# gatenet 🛰️

[![Static Badge](https://img.shields.io/badge/readthedocs-readme?style=for-the-badge&logo=readthedocs&logoColor=%23182026&color=%23788793&link=https%3A%2F%2Fgatenet.readthedocs.io%2Fen%2Flatest%2F)](https://gatenet.readthedocs.io/en/latest/) [![Changelog](https://img.shields.io/badge/changelog-log?logo=gitbook&logoColor=%23333333&color=%233860a9&style=for-the-badge&link=https%3A%2F%2Fgithub.com%2Fclxrityy%2Fgatenet%2Fblob%2Fmaster%2FCHANGELOG.md)](https://gatenet.readthedocs.io/en/latest/changelog.html)

| **Package** | [![PyPI](https://img.shields.io/pypi/v/gatenet?style=for-the-badge)](https://pypi.org/project/gatenet/) [![Python](https://img.shields.io/pypi/pyversions/gatenet?style=for-the-badge)](https://pypi.org/project/gatenet/)                                                                                                                                                                                                                                                                                                         |
| :---------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tests**   | [![Coverage](https://img.shields.io/badge/coverage-Report-green?logo=readthedocs&logoColor=%238CA1AF&color=%2333CC99&style=for-the-badge)](https://gatenet.readthedocs.io/en/latest/coverage_summary.html) [![CI](https://github.com/clxrityy/gatenet/actions/workflows/test.yml/badge.svg?style=for-the-badge)](https://github.com/clxrityy/gatenet/actions/workflows/test.yml) [![codecov](https://codecov.io/gh/clxrityy/gatenet/graph/badge.svg?token=4644O5NGW9&style=for-the-badge)](https://codecov.io/gh/clxrityy/gatenet) |
| **License** | [![License](https://img.shields.io/github/license/clxrityy/gatenet?style=for-the-badge)](LICENSE)                                                                                                                                                                                                                                                                                                                                                                                                                                  |

**Gatenet is a batteries-included Python networking toolkit for diagnostics, service discovery, mesh networking, and building robust socket, UDP, HTTP, and radio microservices.**

- **Diagnostics:** Traceroute, ping/latency, bandwidth, port scanning, geo IP, and more.
- **Service Discovery:** Identify running services (SSH, HTTP, FTP, SMTP, mDNS, SSDP, Bluetooth, etc.) using banners, ports, and extensible detectors.
- **Socket & HTTP:** Modular TCP/UDP/HTTP servers and clients, with async support.
- **Mesh & Radio:** Modular mesh networking with LoRa, ESP, Wi-Fi, GPS, and SDR integration. Supports encrypted messaging, topology mapping, hardware scanning, and protocol extension.
- **Extensible:** Strategy and chain-of-responsibility patterns for easy extension and custom detection.
- **Comprehensive tests and documentation.**

Gatenet is designed for developers who need reliable, extensible, and well-tested networking tools for diagnostics, automation, and microservice development.

- [Changelog](https://gatenet.readthedocs.io/en/latest/changelog.html)
- [Installation](#installation)
- [Features](#features)
- [Quickstart](#quickstart)
- [Usage Examples](#usage-examples)
- [Service Discovery](#service-discovery)
- [Diagnostics](#diagnostics)
- [Tests](#tests)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

```zsh
pip install gatenet
```

## Features

- **Modular**: Each component is modular and can be used independently.
- **Testable**: Each component is designed to be testable with unit tests.
- **Service Discovery**: Identify running services (SSH, HTTP, FTP, SMTP, etc.) using banners and ports.
- **Diagnostics**: Tools for traceroute, latency, and bandwidth measurement.
- **Socket Servers & Clients**: TCP, UDP, and HTTP server/client implementations.
- **Async Support**: Asynchronous HTTP client and server.
- **Extensible**: Strategy and chain-of-responsibility patterns for easy extension.
- **Comprehensive Documentation**: With examples and usage guides.

---

## Quickstart

### TCP Client

```python
# Synchronous usage
from gatenet.client.tcp import TCPClient

client = TCPClient(host="127.0.0.1", port=12345)
client.connect()
response = client.send("ping")
print(response)
client.close()

# --- Async usage ---
from gatenet.client.tcp import AsyncTCPClient
import asyncio

async def main():
    client = AsyncTCPClient(host="127.0.0.1", port=12345)
    await client.connect()
    response = await client.send("ping")
    print(response)
    await client.close()

asyncio.run(main())
```

### HTTP Server

```python
# Synchronous usage
from gatenet.http.server import HTTPServer

server = HTTPServer(host="0.0.0.0", port=8080)

@server.route("/status", method="GET")
def status_handler(req):
    return {"ok": True}

server.serve()

# --- Async usage ---
from gatenet.http_.async_client import AsyncHTTPClient
import asyncio

async def main():
    client = AsyncHTTPClient("http://localhost:8080")
    response = await client.get("/status")
    print(response)

asyncio.run(main())
```

---

## Usage Examples

### Service Discovery

Identify a service by port and banner:

```python
from gatenet.discovery.ssh import _identify_service

service = _identify_service(22, "SSH-2.0-OpenSSH_8.9p1")
print(service)  # Output: "OpenSSH 8.9p1"
```

Use a specific detector:

```python
from gatenet.discovery.ssh import HTTPDetector

detector = HTTPDetector()
result = detector.detect(80, "apache/2.4.41")
print(result)  # Output: "Apache HTTP Server"
```

### Custom Service Detector

```python
from gatenet.discovery.ssh import ServiceDetector
from typing import Optional

class CustomDetector(ServiceDetector):
    """Custom service detector implementation."""
    def detect(self, port: int, banner: str) -> Optional[str]:
        if 'myapp' in banner:
            return "MyCustomApp"
        return None
```

---

## Service Discovery

- **SSH, HTTP, FTP, SMTP, and more**: Uses a strategy pattern and chain of responsibility for extensible service detection.
- **Banner and port-based detection**: Extracts service names and versions from banners and well-known ports.
- **Fallback detection**: Always returns a result, even for unknown services.

See [examples/discovery/ssh_discovery.py](examples/discovery/ssh_discovery.py) for more.

---

## Diagnostics

- **Traceroute**: Trace the route to a host.
- **Latency Measurement**: Measure round-trip time to a host.
- **Bandwidth Measurement**: Measure throughput to a host.

Example traceroute:

```python
from gatenet.diagnostics.traceroute import traceroute

hops = traceroute("google.com")
for hop in hops:
    print(hop)
```

Example bandwidth measurement:

```python
from gatenet.diagnostics.bandwidth import measure_bandwidth

result = measure_bandwidth("google.com")
print(f"Download: {result['download_mbps']} Mbps, Upload: {result['upload_mbps']} Mbps")
```

---

## Tests

Run all tests with:

```bash
pytest
```

- Uses `pytest` for all tests.
- Includes unit and integration tests for all modules.
- Use `get_free_port()` from `gatenet.utils.net` in tests to avoid port conflicts.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- Follow the code style and patterns used in the project.
- Add tests for new features.
- Update documentation as needed.

---

## License

[MIT](LICENSE)
