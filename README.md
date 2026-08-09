# iphone-agent

Ovládání skutečného iPhonu z Macu, pro člověka i pro LLM agenta. Postavené na
WebDriverAgent, protože **iPhone Mirroring v EU nefunguje a nepůjde obejít**.

Živý obraz telefonu ve vlastním okně, klik ťuká, tažení swipuje, dva prsty
scrollují, klávesnice píše. Plus Python klient, přes který to řídí agent.

## Proč ne iPhone Mirroring

Od iOS 26 se region check vyhodnocuje **na telefonu** a je podepsaný v auth
odpovědi, takže se z Macu spoofnout nedá. Chyba, kterou uvidíš v logu:

```
Error Domain=com.apple.sharing.authentication Code=35
"Remote device threw an error: SFAuthenticationErrorCodeRegionLocked"
```

`Remote device` je telefon, ne Mac. Starší Mac-side patche (`mirroreu`,
`Pauli1Go/iphone-mirroring-eu-enabler`, `timi2506/iphone-mirroring-eu-activate`)
fungovaly, dokud Apple hlídal jen Mac. Dnes ti nastaví
`OS_ELIGIBILITY_DOMAIN_IRON` na eligible, Mac projde všemi kontrolami a telefon
tě stejně odmítne. Detailní rozbor: [`nxm/iphone-mirroring-bypass`](https://github.com/nxm/iphone-mirroring-bypass).

Není to o SIP. `/private/var/db/os_eligibility/eligibility.plist` je TCC-chráněný,
ne SIP-restricted.

## Bezpečnost, čti to

**WDA nemá žádnou autentizaci.** Kdo dosáhne na port 8100, ovládá telefon:
čte obrazovku, ťuká, píše, otevírá appky. Na tailnetu to znamená každé tvoje
zařízení plus cokoli sdíleného.

Nepouštěj to na telefon, který ti něco znamená. Testovací kus, vlastní Apple ID,
ideálně vlastní VLAN. Když skončíš, smaž runner z telefonu a vypni Developer
Mode; bez něj WDA nejde spustit.

## Setup

Kabel je potřeba jen tehdy, když Mac s telefonem ještě nikdy nebyl spárovaný.
Jinak jede všechno po Wi-Fi včetně buildu.

1. Xcode. Z App Store přijde bez iOS platformy, dotáhni ji:
   `xcodebuild -downloadPlatform iOS`
2. Na telefonu **Nastavení → Soukromí a zabezpečení → Režim pro vývojáře** → zapnout → restart
3. Na telefonu **Nastavení → Vývoj → Zapnout automatizaci rozhraní**.
   Bez toho XCUITest spadne na `Timed out while enabling automation mode`.
4. Naklonuj a postav WebDriverAgent:
   ```bash
   git clone https://github.com/appium/WebDriverAgent
   cd WebDriverAgent
   ```
   V Xcode otevři `WebDriverAgent.xcodeproj`, u targetů `WebDriverAgentRunner`
   a `WebDriverAgentLib` zapni automatické podepisování a vyber svůj tým.
   Bundle ID `com.facebook.WebDriverAgentRunner` je zabrané, přepiš ho na svoje.
   ```bash
   xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner \
     -destination "id=$UDID" -allowProvisioningUpdates build-for-testing
   ```
5. Napoprvé iOS odmítne appku spustit. Na telefonu
   **Nastavení → Obecné → VPN a správa zařízení** → tvůj účet → Důvěřovat.
6. `cp .env.example .env` a vyplň
7. `./wda-up.sh` a v druhém okně `./viewer.sh`

## Dvě omezení, se kterými musíš počítat

**Session tiše ztrácí dotyky.** Po nějaké době přestanou tapy a swipy fungovat.
Strom, snímky i `/status` jedou dál a nic nehlásí chybu, v logu XCUITest pořád
píše `Synthesize event` se správnými souřadnicemi. Jediná náprava je restart,
tedy `./wda-up.sh` znovu. Hned po restartu dotyky prokazatelně fungují.

**Obraz je stropovaný kolem 10 fps.** Naměřeno ve čtyřech konfiguracích:

| framerate | kvalita | zmenšení | naměřeno |
|---|---|---|---|
| 10 (default) | 25 | 100 % | 9,5 fps |
| 30 | 45 | 80 % | 8,0 fps |
| 60 | 20 | 50 % | 7,0 fps |
| 60 | 10 | 40 % | 9,8 fps |

Úzké hrdlo je pořizování snímků v XCUITestu, ne síť ani nastavení. Vyšší
framerate dokonce ubližuje, protože těžší snímky zpomalí přenos. Pro plynulý
obraz musí jinam zdroj videa: H264 z [`devicekit-ios`](https://github.com/mobile-next/devicekit-ios),
nebo AirPlay na Mac (v EU funguje) a WDA nechat jen na ovládání.

## Endpointy WDA, ověřené proti zařízení

Verze WDA se liší, tyhle platí pro srpen 2026 na iOS 26.5:

| co | jak |
|---|---|
| tap | `POST /session/{sid}/actions`, W3C pointer sekvence |
| swipe | `POST /session/{sid}/wda/dragfromtoforduration` |
| text | `POST /session/{sid}/wda/keys` `{"value":["ahoj"]}` |
| plocha | `POST /wda/homescreen`, bez session |
| stream | `GET :9100`, `multipart/x-mixed-replace` |

Staré `/session/{sid}/wda/tap/0` vrací **404 unknown command**. Hodně návodů
na internetu ho pořád uvádí.

WDA posílá `Access-Control-Allow-Origin: *`, takže viewer nepotřebuje backend.
Je to jeden HTML soubor.

## Obsah

| | |
|---|---|
| `phone.py` | Python klient nad `facebook-wda`, primitiva pro agenta |
| `viewer.html` | živý obraz + ovládání, jeden soubor, bez závislostí |
| `viewer.sh` | otevře viewer ve vlastním okně bez prohlížečového chromu |
| `wda-up.sh` | nahodí a drží WDA session |
| `harness/` | fork [ShawnPana/phone-harness](https://github.com/ShawnPana/phone-harness) (MIT) s cílovým oknem jako proměnná, funguje nad libovolným oknem na Macu |

Ve forku je opravený i upstream bug: `pyproject.toml` požadoval
`pyobjc-framework-AppKit`, který na PyPI neexistuje. Správně je
`pyobjc-framework-Cocoa`.

## Známé vady

- Viewer má **moc zaoblené rohy**, `--radius: 13.5%` neodpovídá skutečnému iPhonu
- Titulkový pruh okna zůstává světlý. Chromium na macOS okno bez titulku neumí
  a `<meta name="color-scheme">` na rám nedosáhne.
- Směr scrollu je konstanta `SCROLL_NATURAL` ve `viewer.html`, ne autodetekce

## Licence

MIT. `harness/` přebírá licenci původního projektu.
