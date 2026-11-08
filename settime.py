#!/usr/bin/env python3
"""
Set the time on a Xiaomi Mi Temperature & Humidity Monitor Clock (LYWSD02MMC) over BLE.
Cross-platform (macOS / Linux / Windows) via bleak.

  python settime.py --scan                      # list nearby BLE devices, Xiaomi ones marked
  python settime.py                             # find the clock and sync it to system time
  python settime.py --address <UUID-or-MAC>     # connect directly (no name scan)
  python settime.py --shift -60                 # system time shifted by N minutes
  python settime.py --at "2026-11-08 07:30"     # any local date/time
"""
import argparse
import asyncio
import struct
from datetime import datetime, timedelta, timezone

from bleak import BleakClient, BleakScanner

TIME_CHAR = "ebe0ccb7-7a0a-4b0c-8a1a-6ff2997da3a6"
XIAOMI_SVC = "fe95"


def fmt(raw: bytes) -> str:
    ts, tz = struct.unpack("<Ib", raw[:5])
    local = datetime.fromtimestamp(ts + tz * 3600, timezone.utc)
    return f"{local:%Y-%m-%d %H:%M:%S} (UTC{tz:+d})"


async def scan(timeout: float):
    found = await BleakScanner.discover(timeout=timeout, return_adv=True)
    for addr, (d, adv) in sorted(found.items(), key=lambda x: -x[1][1].rssi):
        xiaomi = any(XIAOMI_SVC in u for u in list(adv.service_data) + adv.service_uuids)
        name = d.name or adv.local_name or "-"
        print(f"{adv.rssi:4d}  {'XIAOMI ' if xiaomi else '       '}{name:25} {addr}")


async def find_by_name(name: str, timeout: float):
    print(f"Scanning {timeout:.0f}s for '{name}'...")
    for d in await BleakScanner.discover(timeout=timeout):
        if d.name and name.lower() in d.name.lower():
            return d
    return None


async def main():
    ap = argparse.ArgumentParser(description="Set time on Xiaomi LYWSD02MMC")
    ap.add_argument("--scan", action="store_true", help="list nearby devices and exit")
    ap.add_argument("--address", help="device address (CoreBluetooth UUID on macOS, MAC elsewhere)")
    ap.add_argument("--name", default="LYWSD02", help="advertised name to look for")
    ap.add_argument("--shift", type=int, default=0, help="shift system time by N minutes")
    ap.add_argument("--at", help='set a specific local time, e.g. "2026-11-08 07:30"')
    ap.add_argument("--timeout", type=float, default=15.0, help="scan timeout in seconds")
    args = ap.parse_args()

    if args.scan:
        await scan(args.timeout)
        return

    if args.at:
        target = datetime.strptime(args.at, "%Y-%m-%d %H:%M").astimezone()
    else:
        target = datetime.now().astimezone() + timedelta(minutes=args.shift)
    tz_hours = int(target.utcoffset().total_seconds() // 3600)
    payload = struct.pack("<Ib", int(target.timestamp()), tz_hours)

    device = args.address or await find_by_name(args.name, args.timeout)
    if not device:
        print("Clock not found. The name is often not advertised - run with --scan "
              "and pass the strongest XIAOMI entry with --address.")
        return

    async with BleakClient(device, timeout=30.0) as client:
        print("Before:", fmt(await client.read_gatt_char(TIME_CHAR)))
        await client.write_gatt_char(TIME_CHAR, payload, response=True)
        print("After: ", fmt(await client.read_gatt_char(TIME_CHAR)))
    print("Done. The e-ink display refreshes within a minute.")


if __name__ == "__main__":
    asyncio.run(main())
