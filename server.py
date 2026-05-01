#!/usr/bin/env python3
from __future__ import annotations

import time

from kardpad.config import APP_NAME
from kardpad.runtime import KardPadRuntime
from kardpad.web import print_qr


def print_banner(runtime: KardPadRuntime, local_ip: str) -> None:
    info = runtime.info
    http_url = info.http_url(local_ip)
    https_url = info.https_url(local_ip)

    w = 58
    print()
    print("+" + "=" * w + "+")
    print(f"|{APP_NAME:^{w}}|")
    print("+" + "-" * w + "+")
    print(f"|  Red: {local_ip:<{w - 8}}|")
    print("+" + "-" * w + "+")
    print(f"|{'':^{w}}|")
    print(f"|  {'COMO CONECTAR':<{w - 4}}|")
    print(f"|{'':^{w}}|")
    print(f"|  {'1. Abre Safari (iPhone) o Chrome (Android)':.<{w - 4}}|")
    print(f"|  {'2. Escribe esta URL:':<{w - 4}}|")
    print(f"|{'':^{w}}|")
    print(f"|     >>> {http_url:<{w - 11}}|")
    if info.https_enabled:
        print(f"|     >>> {https_url:<{w - 11}}|")
    print(f"|{'':^{w}}|")
    print(f"|  {'3. iPhone: Compartir > Anadir a inicio':.<{w - 4}}|")
    print(f"|     {'(se abre como app, sin barras de Safari)':.<{w - 7}}|")
    print(f"|{'':^{w}}|")
    print(f"|  DSU Dolphin: 127.0.0.1:{info.dsu_port:<{w - 27}}|")
    print("+" + "=" * w + "+")


def main() -> None:
    runtime = KardPadRuntime()
    info = runtime.start()

    for ip in info.local_ips:
        print_banner(runtime, ip)
        print_qr(info.preferred_browser_url(ip))
        print()

    if info.https_enabled:
        print("\n  Android: si pide certificado, toca 'Avanzado' > 'Continuar'")
    print("\n  Asegurate de que PC y movil estan en la MISMA Wi-Fi.")
    print("  En Dolphin: Mandos > Alternativo > DSUClient > udp://127.0.0.1:26760")
    print()

    try:
        while True:
            time.sleep(1)
    finally:
        runtime.stop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[{APP_NAME}] Stopped.")
