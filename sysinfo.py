#!/usr/bin/env python3
"""Muestra información del sistema (CPU, RAM, disco, usuario) con colores.

Solo usa la biblioteca estándar; lee /proc, por lo que está pensado para Linux.
"""

import getpass
import os
import platform
import shutil
import socket
import sys
import time

USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def color(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def bold(t): return color(t, "1")
def cyan(t): return color(t, "36")
def green(t): return color(t, "32")
def yellow(t): return color(t, "33")
def red(t): return color(t, "31")


def human(num_bytes):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if num_bytes < 1024 or unit == "TiB":
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024


def bar(percent, width=30):
    filled = round(width * percent / 100)
    paint = green if percent < 60 else yellow if percent < 85 else red
    return "[" + paint("█" * filled) + "░" * (width - filled) + "] " + paint(f"{percent:5.1f}%")


def cpu_model():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "desconocido"


def cpu_usage(interval=0.5):
    def snapshot():
        with open("/proc/stat") as f:
            values = list(map(int, f.readline().split()[1:]))
        idle = values[3] + values[4]  # idle + iowait
        return idle, sum(values)

    try:
        idle1, total1 = snapshot()
        time.sleep(interval)
        idle2, total2 = snapshot()
    except OSError:
        return None
    total = total2 - total1
    return 100 * (1 - (idle2 - idle1) / total) if total else 0.0


def memory():
    info = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":", 1)
            info[key] = int(value.split()[0]) * 1024
    total = info["MemTotal"]
    used = total - info.get("MemAvailable", info["MemFree"])
    return used, total


def uptime():
    try:
        with open("/proc/uptime") as f:
            seconds = int(float(f.read().split()[0]))
    except OSError:
        return "desconocido"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    return f"{days}d {hours}h {rem // 60}m"


def section(title):
    print("\n" + bold(cyan(f"▶ {title}")))


def row(label, value):
    print(f"  {bold(label + ':'):<{24 if USE_COLOR else 16}} {value}")


def main():
    print(bold(cyan("═" * 50)))
    print(bold(cyan("  Información del sistema")))
    print(bold(cyan("═" * 50)))

    section("Usuario")
    row("Usuario", green(getpass.getuser()))
    row("Host", socket.gethostname())
    row("Sistema", f"{platform.system()} {platform.release()}")
    row("Python", platform.python_version())
    row("Encendido", uptime())

    section("CPU")
    row("Modelo", cpu_model())
    row("Núcleos", os.cpu_count())
    usage = cpu_usage()
    row("Uso", bar(usage) if usage is not None else "desconocido")
    load = os.getloadavg()
    row("Carga", " ".join(f"{x:.2f}" for x in load) + " (1/5/15 min)")

    section("Memoria RAM")
    used, total = memory()
    row("Usada", f"{human(used)} / {human(total)}")
    row("Uso", bar(100 * used / total))

    section("Disco (/)")
    disk = shutil.disk_usage("/")
    row("Usado", f"{human(disk.used)} / {human(disk.total)}")
    row("Libre", human(disk.free))
    row("Uso", bar(100 * disk.used / disk.total))
    print()


if __name__ == "__main__":
    main()
