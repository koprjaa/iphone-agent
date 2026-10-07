#!/bin/zsh
# Otevre viewer ve vlastnim okne bez prohlizecoveho chromu.
# Chromium --app= dela okno bez tabu, adresniho radku a zalozek, takze
# to na plose vypada jako appka a ne jako otevrena stranka.
#
# Vlastni profil (--user-data-dir) je schvalne: bez nej Chromium okno
# pripoji ke stavajici instanci Brave a zdedi jeji chrome i rozsireni.

set -e

PORT=8899
DIR=${0:A:h}
URL="http://localhost:$PORT/viewer.html"
BRAVE="/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

# server nastartuj jen kdyz uz nebezi
if ! curl -sf -o /dev/null -m 2 "$URL"; then
  # jen loopback: server vydava cely adresar repa a nema prihlaseni
  (cd "$DIR" && python3 -m http.server --bind 127.0.0.1 $PORT >/dev/null 2>&1 &)
  for i in {1..15}; do curl -sf -o /dev/null -m 1 "$URL" && break; sleep 0.4; done
fi

exec "$BRAVE" \
  --app="$URL" \
  --user-data-dir="$HOME/.cache/phone-viewer" \
  --window-size=430,900 \
  --disable-features=Translate \
  >/dev/null 2>&1
