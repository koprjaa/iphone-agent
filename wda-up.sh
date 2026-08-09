#!/bin/zsh
# Nahodi WDA na telefon a drzi ho. Pust znovu, kdyz prestanou chodit dotyky.
#
# WDA session na iOS 26.5 casem tise ztrati schopnost injektovat dotyky:
# dotazy, strom i snimky jedou dal, /status hlasi ready, ale tapy a swipy
# se nikam nedostanou. XCUITest je v logu porad "synthesize"-uje bez chyby.
# Jedina znama naprava je restart teto session.

set -e

[[ -f "${0:A:h}/.env" ]] && source "${0:A:h}/.env"

: ${UDID:?nastav UDID v .env (zjistis pres: xcrun devicectl list devices)}
: ${XCTESTRUN:?nastav XCTESTRUN v .env (najdes pres: find ~/Library/Developer/Xcode/DerivedData -name "*.xctestrun")}

pkill -f "test-without-building" 2>/dev/null || true
sleep 2

cd ~/Projects/WebDriverAgent
xcodebuild test-without-building -xctestrun "${XCTESTRUN/#\~/$HOME}" -destination "id=$UDID" 2>&1 \
  | while IFS= read -r line; do
      case "$line" in
        *ServerURLHere*) echo "WDA nahore: ${line#*ServerURLHere->}" | sed 's/<-.*//' ;;
        *"Testing failed"*|*"TEST EXECUTE FAILED"*) echo "SPADLO: $line" ;;
      esac
    done
