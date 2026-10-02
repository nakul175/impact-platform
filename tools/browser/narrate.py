"""Voice-over for the training video (docs/TRAINING-VIDEO.md).

Two steps, both offline once the model files are present:

  synth   reads tools/browser/narration.json (one entry per caption or card: id, on-screen text,
          spoken text) and writes one 24 kHz mono WAV per entry plus clips.json (durations), with
          Kokoro through kokoro-onnx. The generator reads clips.json so that each caption stays on
          screen until its clip has been spoken.
  mix     places the clips on the recording's timeline (timeline.json, written by the generator),
          measures the offset between the generator's clock and the video's own clock at the first
          and the last title card, writes narration.wav and muxes it into a narrated MP4; it also
          rewrites chapters.json with the measured offset applied.

Model files (not in the repository; Apache-2.0, https://github.com/thewh1teagle/kokoro-onnx):
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
Python packages: kokoro-onnx, soundfile (numpy comes with them); ffmpeg and ffprobe on the PATH.

  python tools/browser/narrate.py synth --model-dir /path/to/model --out /path/to/clips
  python tools/browser/narrate.py mix --video out/impact-platform-walkthrough.mp4 \
      --timeline out/timeline.json --clips /path/to/clips --out out/impact-platform-walkthrough-narrated.mp4
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PEAK = 10 ** (-1 / 20)  # -1 dBFS


def synth(args):
    import soundfile as sf
    from kokoro_onnx import Kokoro

    lines = json.loads((args.script).read_text())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    kokoro = Kokoro(
        str(Path(args.model_dir) / "kokoro-v1.0.onnx"), str(Path(args.model_dir) / "voices-v1.0.bin")
    )
    clips = {}
    problems = []
    for entry in lines:
        samples, rate = kokoro.create(entry["spoken"], voice=args.voice, speed=args.speed, lang=args.lang)
        samples = np.asarray(samples, dtype=np.float32)
        peak = float(np.max(np.abs(samples))) if samples.size else 0.0
        if peak > 0:
            samples = samples * (PEAK / peak)
        seconds = samples.size / rate
        per_char = seconds / max(1, len(entry["spoken"]))
        if samples.size == 0 or per_char < 0.04 or per_char > 0.12:
            problems.append(f"{entry['id']}: {seconds:.2f} s for {len(entry['spoken'])} characters")
        path = out / (entry["id"] + ".wav")
        sf.write(str(path), samples, rate, subtype="PCM_16")
        clips[entry["id"]] = {"file": path.name, "seconds": round(seconds, 3), "screen": entry["screen"]}
        print(f"{entry['id']} {seconds:6.2f} s  {entry['spoken'][:70]}")
    (out / "clips.json").write_text(
        json.dumps(
            {
                "voice": args.voice,
                "speed": args.speed,
                "lang": args.lang,
                "sample_rate": rate,
                "clips": clips,
            },
            indent=2,
        )
        + "\n"
    )
    total = sum(c["seconds"] for c in clips.values())
    print(f"{len(clips)} clips, {total:.1f} s of speech, voice {args.voice} at speed {args.speed}")
    if problems:
        print("suspicious clips (empty or an unusual length per character):\n  " + "\n  ".join(problems))
        return 1
    return 0


def probe_duration(video):
    text = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        text=True,
    )
    return float(text.strip())


def transition(video, around, window=3.0, fps=25, width=64, height=36):
    """The time of the largest frame-to-frame change within `around` ± `window` seconds, found on
    a tiny grey rendering of the video (a title card appearing is such a change)."""
    start = max(0.0, around - window)
    raw = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{2 * window:.3f}",
            "-i",
            str(video),
            "-vf",
            f"fps={fps},scale={width}:{height}",
            "-pix_fmt",
            "gray",
            "-f",
            "rawvideo",
            "-",
        ]
    )
    frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1, height * width).astype(np.int16)
    if len(frames) < 2:
        return None
    jumps = np.abs(np.diff(frames, axis=0)).mean(axis=1)
    index = int(np.argmax(jumps))
    if jumps[index] < 4:
        return None
    return start + (index + 1) / fps


def mix(args):
    import soundfile as sf

    timeline = json.loads(Path(args.timeline).read_text())
    clips_dir = Path(args.clips)
    clips = json.loads((clips_dir / "clips.json").read_text())
    rate = clips["sample_rate"]
    trim = timeline.get("trimMs", 0) / 1000
    entries = [e for e in timeline["entries"] if e.get("id")]
    if not entries:
        sys.exit("the timeline holds no narrated entries")
    duration = probe_duration(args.video)

    if args.offset is None:
        # Offset at the first title card (white page -> card) and at the first outro card
        # (application -> card); the generator's clock may run slightly ahead of the video's.
        cards = [e for e in entries if e["kind"] == "card"]
        probes = [cards[0]] + ([cards[-2]] if len(cards) > 2 else [])
        measured = []
        for card in probes:
            logged = card["t"] / 1000 - trim
            seen = transition(args.video, logged)
            if seen is not None:
                measured.append((logged, seen - logged))
                print(
                    f"{card['id']} logged {logged:8.2f} s, seen {seen:8.2f} s, offset {seen - logged:+.2f} s"
                )
        if not measured:
            sys.exit("no title card transition found; pass --offset")
        if len(measured) == 2 and measured[1][0] != measured[0][0]:
            (t0, o0), (t1, o1) = measured
            slope = (o1 - o0) / (t1 - t0)

            def offset_at(t):
                return o0 + slope * (t - t0)

            print(f"offset {o0:+.2f} s at {t0:.0f} s and {o1:+.2f} s at {t1:.0f} s: interpolating")
        else:
            constant = measured[0][1]

            def offset_at(t):
                return constant

            print(f"offset {constant:+.2f} s")
    else:

        def offset_at(t):
            return args.offset

    track = np.zeros(int(round(duration * rate)), dtype=np.float32)
    previous_end = 0.0
    placed = []
    for entry in entries:
        clip = clips["clips"].get(entry["id"])
        if not clip:
            continue
        samples, clip_rate = sf.read(str(clips_dir / clip["file"]), dtype="float32")
        if clip_rate != rate:
            sys.exit(f"{clip['file']} is {clip_rate} Hz, expected {rate}")
        if samples.ndim > 1:
            samples = samples.mean(axis=1)
        logged = entry["t"] / 1000 - trim
        start = logged + offset_at(logged)
        if start < previous_end:
            print(f"{entry['id']}: would overlap the previous clip by {previous_end - start:.2f} s; shifted")
            start = previous_end + 0.2
        begin = int(round(start * rate))
        end = min(begin + samples.size, track.size)
        if begin >= track.size:
            print(f"{entry['id']}: starts after the video ends; dropped")
            continue
        track[begin:end] = samples[: end - begin]
        previous_end = end / rate
        placed.append(
            {
                "id": entry["id"],
                "start": round(start, 3),
                "end": round(end / rate, 3),
                "screen": entry.get("screen"),
            }
        )
    out = Path(args.out)
    wav = out.with_suffix(".narration.wav")
    sf.write(str(wav), track, rate, subtype="PCM_16")
    subprocess.check_call(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(args.video),
            "-i",
            str(wav),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            str(out),
        ]
    )
    (out.parent / "narration-placement.json").write_text(json.dumps(placed, indent=2) + "\n")
    chapters = {}
    for entry in timeline["entries"]:
        if entry["kind"] == "chapter":
            logged = entry["t"] / 1000 - trim
            at = max(0.0, logged + offset_at(logged))
            chapters[entry["screen"]] = f"{int(at // 60):02d}:{int(round(at % 60)):02d}"
    if chapters:
        (out.parent / "chapters.json").write_text(json.dumps(chapters, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out} ({len(placed)} clips, last ends at {previous_end:.1f} s of {duration:.1f} s)")
    if chapters:
        for title, at in chapters.items():
            print(f"  {at}  {title}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("synth", help="synthesize one clip per narration line")
    s.add_argument("--script", type=Path, default=HERE / "narration.json")
    s.add_argument(
        "--model-dir", required=True, help="directory holding kokoro-v1.0.onnx and voices-v1.0.bin"
    )
    s.add_argument("--out", required=True, help="directory for the WAV clips and clips.json")
    s.add_argument("--voice", default="bf_emma")
    s.add_argument("--speed", type=float, default=0.95)
    s.add_argument("--lang", default="en-gb")
    s.set_defaults(run=synth)
    m = sub.add_parser("mix", help="place the clips on the recording and mux the narrated MP4")
    m.add_argument("--video", required=True)
    m.add_argument("--timeline", required=True)
    m.add_argument("--clips", required=True)
    m.add_argument("--out", required=True)
    m.add_argument(
        "--offset", type=float, default=None, help="seconds to add to every logged time (default: measured)"
    )
    m.set_defaults(run=mix)
    args = parser.parse_args()
    sys.exit(args.run(args))


if __name__ == "__main__":
    main()
