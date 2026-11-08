# LYWSD02MMC clock setter

Set the time on a **Xiaomi Mi Temperature and Humidity Monitor Clock (LYWSD02MMC)**, the e-ink clock with a thermometer and hygrometer, straight from a computer over Bluetooth. You don't need the Mi Home app, a Xiaomi account or a bind key.

This is handy because the clock doesn't switch between summer and winter time (DST) on its own. You can also set it to any time you like.

## Option 1: in the browser (Web Bluetooth)

Open `index.html` in **Chrome or Edge**. Safari and Firefox don't support Web Bluetooth.

- **Computer time, shifted by N min** syncs the clock to your system time, with an optional offset.
- **Any time** sets the clock to a date and time you choose.
- Click **Set time** and pick the clock in the browser's device chooser. The clock often doesn't advertise its name. If it isn't listed, use **Set (show all devices)** and pick the "Unknown device" with the strongest signal.
- The page has an EN/PL language switch.

If this repo is published with GitHub Pages, the page can be used directly from `https://danny3b.github.io/LYWSD02MMC/`.

On macOS, allow Chrome to use Bluetooth the first time it asks (System Settings → Privacy & Security → Bluetooth).

## Option 2: Python script (bleak)

```bash
python3 -m venv venv
./venv/bin/pip install bleak

./venv/bin/python settime.py --scan                    # find the clock (strongest XIAOMI entry, often without a name)
./venv/bin/python settime.py --address <UUID-or-MAC>   # sync to system time
./venv/bin/python settime.py --address <...> --shift -60
./venv/bin/python settime.py --address <...> --at "2026-11-08 07:30"
```

On macOS the address is a CoreBluetooth UUID such as `BD1A43A2-…`. On Linux and Windows it's the MAC address.

## Protocol

| Item | Value |
|---|---|
| Service | `ebe0ccb0-7a0a-4b0c-8a1a-6ff2997da3a6` |
| Time characteristic (read/write) | `ebe0ccb7-7a0a-4b0c-8a1a-6ff2997da3a6` |
| Payload | 5 bytes: `uint32` little-endian Unix timestamp + `int8` UTC offset in hours |

The clock shows `timestamp + offset × 3600` as local time.

## Troubleshooting

- **The clock isn't found.** Close Mi Home on your phone or turn off its Bluetooth, and check that no Xiaomi gateway is holding the connection. A BLE device usually accepts only one connection at a time. Removing and reinserting the CR2032 battery makes the clock advertise right away.
- **Similar devices show up.** `LYWSD03MMC` is the small square thermometer. It uses a different protocol and this tool won't work with it.
