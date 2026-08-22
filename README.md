# iphone-agent

Controls a real iPhone from a Mac over WebDriverAgent, for a person and for an LLM agent. It shows the live screen in its own window, turns clicks into taps and drags into swipes, and exposes the same primitives to Python. It exists because iPhone Mirroring is region-locked in the EU and the lock cannot be lifted from the Mac side.

![python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![platform](https://img.shields.io/badge/platform-macOS-000?style=flat-square&logo=apple&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-A31F34?style=flat-square)
![status](https://img.shields.io/badge/status-prototype-lightgrey?style=flat-square)
[![ci](https://github.com/koprjaa/iphone-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/koprjaa/iphone-agent/actions/workflows/ci.yml)

## What it does

`viewer.html` draws the phone screen and sends input back. It is one file with no
dependencies and no backend, because WebDriverAgent sends
`Access-Control-Allow-Origin: *`. A click taps, a drag swipes, two fingers scroll, and
the keyboard types.

`phone.py` wraps `facebook-wda` and gives an agent the same primitives from Python.

## Why not iPhone Mirroring

Since iOS 26 the region check runs on the phone and is signed in the authentication
response, so it cannot be spoofed from the Mac. The log shows:

```
Error Domain=com.apple.sharing.authentication Code=35
"Remote device threw an error: SFAuthenticationErrorCodeRegionLocked"
```

`Remote device` is the phone, not the Mac. The older Mac-side patches (`mirroreu`,
`Pauli1Go/iphone-mirroring-eu-enabler`, `timi2506/iphone-mirroring-eu-activate`) worked
while Apple checked only the Mac. Today they set `OS_ELIGIBILITY_DOMAIN_IRON` to
eligible, the Mac passes every check, and the phone still refuses. A detailed analysis
is in [`nxm/iphone-mirroring-bypass`](https://github.com/nxm/iphone-mirroring-bypass).

This is not about SIP. `/private/var/db/os_eligibility/eligibility.plist` is
TCC-protected, not SIP-restricted.

## Security

**WebDriverAgent has no authentication.** Anyone who reaches port 8100 controls the
phone: they read the screen, tap, type, and open applications. On a tailnet that means
every one of your devices, plus anything you share.

Do not run this on a phone that matters to you. Use a spare device, a separate Apple ID,
and ideally a separate VLAN. When you finish, remove the runner from the phone and turn
off Developer Mode; WebDriverAgent cannot start without it.

## Install

A cable is necessary only if the Mac and the phone have never been paired. Everything
else runs over Wi-Fi, including the build.

1. Install Xcode. The App Store version comes without the iOS platform, so add it:
   `xcodebuild -downloadPlatform iOS`
2. On the phone open **Settings > Privacy & Security > Developer Mode**, turn it on, and
   restart.
3. On the phone open **Settings > Developer** and turn on **Enable UI Automation**.
   Without it XCUITest fails with `Timed out while enabling automation mode`.
4. Clone and build WebDriverAgent:

   ```bash
   git clone https://github.com/appium/WebDriverAgent
   cd WebDriverAgent
   ```

   Open `WebDriverAgent.xcodeproj` in Xcode. For the `WebDriverAgentRunner` and
   `WebDriverAgentLib` targets turn on automatic signing and select your team. The bundle
   identifier `com.facebook.WebDriverAgentRunner` is taken, so replace it with your own.

   ```bash
   xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner \
     -destination "id=$UDID" -allowProvisioningUpdates build-for-testing
   ```

5. The first launch is refused by iOS. On the phone open
   **Settings > General > VPN & Device Management**, select your account, and trust it.
6. Copy the configuration: `cp .env.example .env` and fill it in.

## Use

```bash
./wda-up.sh      # starts and holds the WebDriverAgent session
./viewer.sh      # opens the viewer in its own window
```

## Two limits to expect

**The session loses touches silently.** After some time taps and swipes stop working. The
element tree, the screenshots, and `/status` continue to answer and nothing reports an
error. The XCUITest log still prints `Synthesize event` with the correct coordinates. The
only repair is a restart, so run `./wda-up.sh` again. Touches work again immediately
after the restart.

**The image is capped near 10 fps.** Measured in four configurations:

| framerate | quality | scale | measured |
|---|---|---|---|
| 10 (default) | 25 | 100 % | 9.5 fps |
| 30 | 45 | 80 % | 8.0 fps |
| 60 | 20 | 50 % | 7.0 fps |
| 60 | 10 | 40 % | 9.8 fps |

The bottleneck is screenshot capture in XCUITest, not the network and not the settings. A
higher framerate makes it worse, because heavier frames slow the transfer down. A smooth
image needs a different video source: H264 from
[`devicekit-ios`](https://github.com/mobile-next/devicekit-ios), or AirPlay to the Mac
(which works in the EU) with WebDriverAgent left to do the control only.

## WebDriverAgent endpoints, verified against a device

WebDriverAgent versions differ. These hold for August 2026 on iOS 26.5:

| operation | request |
|---|---|
| tap | `POST /session/{sid}/actions`, W3C pointer sequence |
| swipe | `POST /session/{sid}/wda/dragfromtoforduration` |
| text | `POST /session/{sid}/wda/keys` `{"value":["hello"]}` |
| home screen | `POST /wda/homescreen`, no session |
| stream | `GET :9100`, `multipart/x-mixed-replace` |

The old `/session/{sid}/wda/tap/0` returns **404 unknown command**. Many guides on the
internet still list it.

## Contents

| | |
|---|---|
| `phone.py` | Python client over `facebook-wda`, primitives for an agent |
| `viewer.html` | live screen and control, one file, no dependencies |
| `viewer.sh` | opens the viewer in its own window without browser chrome |
| `wda-up.sh` | starts and holds the WebDriverAgent session |
| `harness/` | fork of [ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness) (MIT) with the target window as a variable, so it works over any window on the Mac |

The fork also repairs an upstream defect: `pyproject.toml` required
`pyobjc-framework-AppKit`, which does not exist on PyPI. The correct name is
`pyobjc-framework-Cocoa`.

## Known defects

- The viewer corners are too round. `--radius: 13.5%` does not match a real iPhone.
- The window title bar stays light. Chromium on macOS cannot open a window without a
  title bar, and `<meta name="color-scheme">` does not reach the frame.
- The scroll direction is the constant `SCROLL_NATURAL` in `viewer.html`, not a
  detection.

## License

MIT. `harness/` keeps the license of the original project. See `NOTICE`.
