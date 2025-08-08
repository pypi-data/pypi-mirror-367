from __future__ import annotations
"""NetworkParser

Typical Usage:

    >>> from dmarc.milter.networkparser import NetworkParser, ip_address
    >>> networks = NetworkParser("127.0.0.0/8 ::1/128 !127.127.127.127")
    >>> ip_address("127.0.0.1") in networks
    True
    >>> ip_address("::1") in networks
    True
    >>> ip_address("127.127.127.127") in networks
    False
"""

from ipaddress import (
    ip_network,
    ip_address,
    IPv4Address,
    IPv6Address,
)

class NetworkParser:
    
    def __init__(self, s: str = None):
        self.networks = set()
        self.excluded = set()
        if s:
            self.readfp(s.split())
    
    def __iter__(self):
        networks = self.networks
        for exclude in self.excluded:
            _networks = []
            for net in networks:
                try:
                    _networks.extend(list(net.address_exclude(exclude)))
                except (ValueError, TypeError):
                    _networks.append(net)
            networks = _networks
        return iter(networks)
    
    def __contains__(self, address: IPv4Address | IPv6Address) -> bool:
        for network in self.excluded:
            if address in network:
                return False
        for network in self.networks:
            if address in network:
                return True
        return False
    
    def read(self, filenames: list[str]) -> list[str]:
        ret = []
        for filename in filenames:
            try:
                with open(filename) as file:
                    self.readfp(file)
                    ret.append(filename)
            except IOError:
                pass
        return ret
    
    def readfp(self, f, _rec=None) -> None:
        rec = _rec or []
        for line in f:
            line = line.strip()
            line = line.replace('[', '').replace(']', '')
            if not line:
                continue
            if line[0] == '#':
                continue
            if line[0] == '/':
                if line in rec:
                    raise ValueError(f"file read recursion error: {line!r}")
                with open(line) as file:
                    rec.append(line)
                    self.readfp(file, rec)
                continue
            if line[0] == '!':
                self.excluded.add(ip_network(line.lstrip('!')))
            else:
                self.networks.add(ip_network(line))
