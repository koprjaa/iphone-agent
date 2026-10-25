# iphone-agent

Control an iPhone from a Mac, by hand or by LLM agent.

[![ci](https://github.com/koprjaa/iphone-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/koprjaa/iphone-agent/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/license-AGPL--3.0-A31F34?style=flat-square)](LICENSE)

`harness/` is a fork of [ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness) (MIT, see `NOTICE`).

It talks to WebDriverAgent running on the phone, because iPhone Mirroring is region-locked in the EU. `viewer.html` shows the live screen in its own window: a click taps, a drag swipes, two fingers scroll, the keyboard types. `phone.py` gives an agent the same actions from Python, including tapping an element by its accessibility label.

WebDriverAgent has no authentication. Anyone who reaches port 8100 controls the phone, so use a spare device on a network you trust.

Known limits: touches can stop working after a while (rerun `wda-up.sh`), and the image is capped near 10 fps.

## Install

macOS with Xcode and Python 3.10+. Developer Mode and Settings > Developer > Enable UI Automation must be on, on the phone.

```bash
pip install facebook-wda
git clone https://github.com/appium/WebDriverAgent ~/Projects/WebDriverAgent
```

Build the `WebDriverAgentRunner` scheme for your phone with `xcodebuild ... build-for-testing` (your own team and bundle identifier), then trust your account under Settings > General > VPN & Device Management.

```bash
cp .env.example .env   # set UDID, XCTESTRUN, PHONE_HOST
```

## Use

```bash
./wda-up.sh                    # starts and holds the WebDriverAgent session
./viewer.sh                    # opens the viewer (needs Brave)
python3 phone.py               # checks that WebDriverAgent answers
```

```python
import phone
phone.app("com.apple.Preferences")
phone.tap("General")
print(phone.tree())
```

`viewer.sh` opens `http://localhost:8899/viewer.html`. The viewer reads the phone address from the URL hash, for example `viewer.html#<phone-ip>`.

## License

[AGPL-3.0-or-later](LICENSE). `harness/` keeps the license of the original project.
