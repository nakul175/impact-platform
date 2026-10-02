# Training video — how the platform works, end to end

A captioned screen recording of the real user interface for a non-engineer audience (a programme owner and the two colleagues who act as second operator and organisation owner), with a synthetic voice-over reading the captions. It is generated, not hand-recorded, so it can be remade for any build: `tools/browser/training-video.mjs` drives the packaged Chromium through a running local development instance with the synthetic fixture data and records one page into a video; `tools/browser/narrate.py` synthesizes the narration and lays it onto the recording.

The video itself is not kept in the repository. A generation writes, into the output directory:

- `impact-platform-walkthrough.mp4` — the silent recording: H.264, yuv420p, 1280×720, 25 fps, `+faststart`;
- `impact-platform-walkthrough-narrated.mp4` — the same picture with the narration track (AAC, 96 kb/s, mono); about 14 minutes and about 25 MB at the default quality;
- `chapters.json` — chapter title → `mm:ss` (rewritten by the narration step with the measured offset);
- `timeline.json` — when each caption, card and chapter appeared, relative to the start of the recording;
- `raw.webm` — the unconverted recording.

## What it shows

Captions carry the narration and the voice reads them (lightly smoothed for speech: "Step 1 —" becomes "Step one:", "59 of 120" is spoken in words). Captions avoid the engineering vocabulary (no "revision", "tenant", "capability"): they say organisation, data entry, approval, permission.

1. Two title cards: the two parts, and the one rule that explains most of the steps (nobody approves their own work).
2. **Part 1 — Setting up an organisation**, the owner click-path of `docs/current/DEPLOYMENT-GUIDE.md` §4.1 with three people: Nakul (fixture `admin`, a platform operator) nominates a colleague as second operator and creates their sign-in and the future owner's sign-in (one-time passwords shown once, as the product shows them); the colleague accepts the operator role; the owner signs in once; Nakul requests the organisation ("Clean Water Trust") and chooses the owner by name; the owner accepts and nominates Nakul as recovery contact; Nakul confirms; the second operator approves the contact and activates; the owner proposes the initial access with Nakul as second administrator; Nakul accepts; the second operator approves; the owner sets up the standard reference data.
3. **Part 2 — The measurement cycle** in the fixture workspace: the author enters the third site's return (8 of 10) with a photo as evidence and submits it; the independent reviewer approves it and calculates the quarter (59 / 120 = 49.17 %, provisional); targets versus actuals; the author submits the period close and the reviewer approves it; the dashboard shows the official 49.17 % with coverage and freshness; the author drafts the report from the locked snapshot with a bound placeholder in the narrative; a form response and a previewed import batch (accepted, quarantined, duplicate rows); the reviewer approves the report and requests a PDF, which the background worker renders; People & access as the administrator (members, reference data, audit export, data-subject requests).
4. Two closing cards: what you need to start (three people, then two) and the chapter index.

Everything shown is synthetic: the colleagues' addresses end in `example.org`, the organisation and programmes are invented, and the one-time passwords belong to accounts of a disposable local instance.

## Regenerating it

Needs Linux x86_64, `make setup` done, the packaged browser prepared once (`make browser` does it, or `node tools/browser/prepare.mjs`), `ffmpeg` and `ffprobe` on the PATH (or `FFMPEG=/path/to/ffmpeg` for the generator), and for the voice-over a Python environment with `kokoro-onnx` and `soundfile` (`python3 -m venv .local/tts && .local/tts/bin/pip install kokoro-onnx soundfile`; it brings `onnxruntime`, `numpy`, `phonemizer-fork` and `espeakng-loader`, so no system package is needed) plus the two Kokoro model files, downloaded once outside the repository (about 340 MB):

- https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
- https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

Kokoro (model and weights) and `kokoro-onnx` are published under the Apache-2.0 licence. The voice used is `bf_emma` (British English) at speed 0.95; the language passed to the phonemizer is `en-gb`.

1. Synthesize the clips (once per change of `tools/browser/narration.json`): `.local/tts/bin/python tools/browser/narrate.py synth --model-dir /path/to/model --out /path/to/clips`. It writes one 24 kHz mono WAV per line, peak-normalised to −1 dBFS, and `clips.json` with the durations, and refuses a run in which a clip is empty or implausibly short or long for its text.
2. Start a fresh instance: `.venv/bin/python scripts/run.py dev --ephemeral` (it also starts the worker that renders the PDF). Use a fresh instance for a final take: part 1 creates two sign-in accounts and an organisation by name, and `.local/dev/users.json` keeps the accounts across restarts, so remove it before restarting if the names must be reused; for repeated test runs against one instance set `TRAINING_VIDEO_UNIQUE=1`, which suffixes every created name.
3. Record, from the repository root: `TRAINING_VIDEO_DIR=/path/to/output TRAINING_VIDEO_AUDIO_DIR=/path/to/clips node tools/browser/training-video.mjs`. With the clips present every caption and card stays on screen until its clip would have been spoken (clip length plus 0.8 s) before the next action, so the narration drives the pacing; a full take then runs about fourteen minutes plus the ffmpeg conversion. Run it detached from a shell that may time out. Without `TRAINING_VIDEO_AUDIO_DIR` the film is paced for reading only (about 9½ minutes, no narration).
4. Lay the narration onto the recording: `.local/tts/bin/python tools/browser/narrate.py mix --video /path/to/output/impact-platform-walkthrough.mp4 --timeline /path/to/output/timeline.json --clips /path/to/clips --out /path/to/output/impact-platform-walkthrough-narrated.mp4`. It measures the offset between the generator's clock and the video's own clock at the first title card and at the first closing card (the largest frame change near each logged time), places each clip at its logged time plus that offset (clips never overlap because of the holds), writes `narration.wav`, muxes it (`-c:v copy -c:a aac -b:a 96k`), writes `narration-placement.json` and rewrites `chapters.json` with the offset applied. Pass `--offset <seconds>` to override the measurement.
5. Check the result: `ffprobe` both MP4s, open `chapters.json`, look at a few frames (`ffmpeg -ss <seconds> -i … -frames:v 1 frame.png`) and confirm that audio is present around a few captions (`ffmpeg -ss <seconds> -t 4 -i … -af volumedetect -f null -`).

Options of the generator (environment variables): `IMPACT_BASE_URL` (default `http://127.0.0.1:8000`), `IMPACT_TEST_LOCAL` (the run directory, default `.local/dev`), `TRAINING_VIDEO_PACE` (1 = human pace; `0.2` for a quick selector check), `TRAINING_VIDEO_SCENES` (`all`, or a comma list of `intro,part1,part2,outro`), `TRAINING_VIDEO_AUDIO_DIR` (the clips, see above), `TRAINING_VIDEO_CRF` (x264 quality, default 23), `TRAINING_VIDEO_RESET_LOGIN_LIMIT=0` to leave the development sign-in counters alone.

The narration script is `tools/browser/narration.json`: one entry per caption or card with its `id`, the on-screen text (`screen`, which the generator uses to find the clip) and the spoken text (`spoken`). A new or changed caption in the generator needs its entry there, or the generator warns and the line stays silent. The spoken text may smooth a caption for speech but never adds a claim the caption does not make.

Two things the script does that a person would not:

- Part 2's set-up (the programme, its approved indicator and collection plan, the two earlier site returns, the framework and target, the second programme with its published form and import batches) is created through the API with development bearer tokens before recording starts, so the film shows the measurement cycle rather than configuration.
- The development sign-in counts every attempt, successful or not, against the account and the network address (ten per five minutes), and the film signs people in about twenty times; the script clears `impact.login_attempt` on the local instance before each sign-in (`resetSignInLimit`). That is a test-instance affordance only: the staging sign-in is Keycloak's, which locks only after wrong passwords.

The overlay (caption bar, visible cursor, click ripple, highlight outline) is injected with `context.addInitScript` and styled through the CSSOM, which the application's content-security policy allows; the caption and cursor are manual popovers so that they stay above the application's modal dialogs, which live in the browser's top layer.

## Known limits

- The recording is of the development sign-in, not Keycloak: the live server additionally asks new people for their own password and an authenticator app at first sign-in, which the captions say but the film cannot show.
- After the organisation is activated and before its initial access is applied, the owner's landing page shows the portfolio with "The action is not permitted" for a few seconds (the owner has no grants yet); the film moves on to the console at once.
- Browser checks are the source of the selectors; when a label changes, the script fails at that step and writes `failure.png` into the output directory.
- The voice is synthetic and nobody listened to every clip before publication: the clips were checked for length per character, leading and trailing silence and peak level, and the phonemizer's rendering of the product terms (Nakul, PDF, 49.17 %, People & access) was inspected, not heard.
