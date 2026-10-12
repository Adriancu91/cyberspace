"""Rețeaua interfeței: cine are voie să intre și pe ce adrese ascultă serverul.

Interfața e accesibilă DOAR de pe acest calculator și prin Tailscale (rețeaua privată dintre aparatele lui Adrian).
Sunt două lacăte, unul peste altul:
1. serverul ascultă numai pe 127.0.0.1 și pe adresa Tailscale a calculatorului, niciodată pe 0.0.0.0;
2. fiecare cerere e verificată: dacă adresa clientului nu e a calculatorului sau din rețeaua Tailscale, primește 403.
"""

from __future__ import annotations

import ipaddress
import subprocess

ADRESA_LOCALA = "127.0.0.1"
# Adresele pe care le împarte Tailscale aparatelor din rețea (IPv4).
RETEA_TAILSCALE = ipaddress.ip_network("100.64.0.0/10")
ADRESE_INTERZISE = ("", "0.0.0.0", "::")  # „toate plăcile de rețea”: nu ascultăm niciodată așa


def adresa_permisa(adresa: str) -> bool:
    """Are voie clientul cu această adresă? Da doar pentru 127.0.0.1, ::1 și rețeaua Tailscale 100.64.0.0/10.
    Orice altceva (inclusiv un text care nu e o adresă) e refuzat."""
    try:
        ip = ipaddress.ip_address(str(adresa).strip().split("%", 1)[0])  # fără zona de după „%” (IPv6)
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped  # „::ffff:127.0.0.1” e tot 127.0.0.1
    if isinstance(ip, ipaddress.IPv4Address):
        return ip == ipaddress.ip_address(ADRESA_LOCALA) or ip in RETEA_TAILSCALE
    return ip == ipaddress.ip_address("::1")


def adresa_tailscale() -> str | None:
    """Adresa Tailscale (IPv4) a acestui calculator, aflată cu „tailscale ip -4”. None dacă Tailscale nu e instalat,
    nu e pornit sau răspunde cu altceva decât o adresă din rețeaua lui."""
    try:
        rezultat = subprocess.run(["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    if rezultat.returncode != 0:
        return None
    for rand in rezultat.stdout.splitlines():
        try:
            ip = ipaddress.ip_address(rand.strip())
        except ValueError:
            continue
        if isinstance(ip, ipaddress.IPv4Address) and ip in RETEA_TAILSCALE:
            return str(ip)
    return None


def adrese_de_ascultat(tailscale: str | None = None) -> list[str]:
    """Adresele pe care ascultă serverul: 127.0.0.1 și, dacă există, adresa Tailscale. Atât."""
    adrese = [ADRESA_LOCALA]
    if tailscale and tailscale not in adrese and adresa_permisa(tailscale):
        adrese.append(tailscale)
    return adrese
