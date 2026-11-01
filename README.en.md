# RAW-SNES OBS Companion

**v1.0.0 — Stable release. Verified on real SNES hardware.**

**RetroAchievements achievement notifications for OBS Studio when playing on real Super Nintendo / Super Famicom hardware.**

An independent companion by [HeresAChallenger](https://github.com/HeresAChallenger), adapted from the MIT-licensed [MegaRaw-OBS-Companion](https://github.com/HeresAChallenger/MegaRaw-OBS-Companion). RAW-SNES itself is authored by [Liqui](https://github.com/liquid-wq/raw-snes) and released under a separate, restrictive license. **This package does not include RAW-SNES binaries or source code.**

## Features

- Polls RetroAchievements' official public Web API for **confirmed achievement unlocks**.
- Filters notifications to **SNES / Super Nintendo / Super Famicom** achievements.
- Displays title, description, game, badge, points, and unlock mode in a **transparent OBS browser source** (520 × 160 pixels).
- Plays a replaceable CC0 demo WAV in OBS browser source audio.
- Includes a local dashboard and demonstration button; no real achievements are used during tests.
- Adjustable API intervals: 2 / 3 / 5 / 10 / 15 seconds; retries with backoff on errors.
- Stores the **Web API Key** with Windows DPAPI inside `%LOCALAPPDATA%\RawSNESObsOverlay\` (separately from RAW-SNES).
- Requires Python 3.10+ standard library only; doesn't communicate with, introspect, or modify RAW-SNES.

## Requirements and setup

1. Install Python 3.10 or newer on Windows 10/11 and extract the entire ZIP to a new folder.
2. Run `INICIAR.bat`; choose **1** (demonstration).
3. In OBS, add a Browser source with URL `http://127.0.0.1:8766/overlay`, width **520**, height **160**, enable **Control audio via OBS**, and place it above the console capture source.
4. Open `http://127.0.0.1:8766/painel` and press the test notification button.
5. Stop the companion with `Ctrl+C` and relaunch with **2** (LIVE 5 seconds); on first run, provide your RetroAchievements username and **Web API Key** from your RetroAchievements control panel.
6. Run RAW-SNES separately and use your SD2SNES/FXPak Pro per its official instructions. Keep both programs running while streaming.

**Important:** The Web API Key is **not** the `ra_token` stored in `rawsnes_config.json`. Never publish either credential.

This tool does not receive instantaneous events from the RAW-SNES application: it polls the online API, so alert latency depends on online confirmation and polling. The 2-second option is experimental, and may result in HTTP 429. Start with 5 seconds; if throttled, choose 10 or 15 seconds.

The original MegaRaw Companion uses port **8765**, while this companion uses **8766**. Both can be installed together. Using both against one RetroAchievements account adds to the account's aggregate API usage.

### Audio

`som_alerta.wav` is an **original CC0 demo sound**, not extracted from RAW-SNES. Replace it locally only with audio you have the right to use. To disable sound, change the Browser URL to `http://127.0.0.1:8766/overlay?som=0`.

### Developer commands

```powershell
python rawsnes_obs.py --demo
python rawsnes_obs.py --interval 5
python rawsnes_obs.py --interval 2
python rawsnes_obs.py --reset
python -m unittest discover -s tests -v
```

## Attribution and license

- Companion: © 2026 HeresAChallenger, MIT; derived from his separately released MIT-licensed MegaRaw-OBS-Companion.
- Bundled synthetic demonstration sound: CC0 1.0, see `AUDIO-LICENSE.txt`.
- RAW-SNES: © 2025–2026 Liqui, separate license; not modified or redistributed.
- RetroAchievements data and trademarks remain owned by their respective parties. This project is not affiliated with Liqui, RetroAchievements, OBS or Nintendo.

See [Portuguese README](README.md), [security](docs/SEGURANCA.md) and [release notes](RELEASE_NOTES.md).