#!/usr/bin/env python3
"""AudioNormer - batch normalize MP3 collections."""

import argparse
import subprocess
import sys
from pathlib import Path

from pydub import AudioSegment
from pydub.silence import detect_leading_silence


def strip_silence(
    audio: AudioSegment,
    silence_threshold: float = -50.0,
    chunk_size: int = 10,
) -> AudioSegment:
    """Strip silence from start and end of an audio segment."""
    start_trim = detect_leading_silence(
        audio, silence_threshold=silence_threshold, chunk_size=chunk_size
    )
    end_trim = detect_leading_silence(
        audio.reverse(), silence_threshold=silence_threshold, chunk_size=chunk_size
    )
    duration = len(audio)
    if end_trim == 0:
        return audio[start_trim:]
    return audio[start_trim : duration - end_trim]


def process_file(
    input_path: Path,
    output_path: Path,
    silence_threshold: float,
    chunk_size: int,
) -> bool:
    """Strip silence from a single MP3 file and export to output_path."""
    try:
        audio = AudioSegment.from_mp3(str(input_path))
        trimmed = strip_silence(audio, silence_threshold=silence_threshold, chunk_size=chunk_size)
        trimmed.export(str(output_path), format="mp3")
        return True
    except Exception as exc:
        print(f"  Error processing {input_path.name}: {exc}", file=sys.stderr)
        return False


def apply_replaygain(directory: Path) -> bool:
    """Apply ReplayGain album normalization to all MP3s in directory."""
    mp3_files = sorted(directory.glob("*.mp3"))
    if not mp3_files:
        print("  No MP3 files found for ReplayGain.", file=sys.stderr)
        return False
    try:
        subprocess.run(
            ["replaygain", "--album"] + [str(f) for f in mp3_files],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as exc:
        print(f"  ReplayGain failed (exit {exc.returncode}).", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("  'replaygain' not found. Install rgain3.", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch normalize MP3 collections: strip silence then apply ReplayGain."
    )
    parser.add_argument("input_dir", type=Path, help="Directory containing MP3 files")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: overwrite in place)",
    )
    parser.add_argument(
        "--silence-threshold",
        type=float,
        default=-50.0,
        help="Silence threshold in dBFS (default: -50.0)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10,
        help="Chunk size in ms for silence detection (default: 10)",
    )
    parser.add_argument(
        "--skip-silence-strip",
        action="store_true",
        help="Skip silence stripping step",
    )
    parser.add_argument(
        "--skip-replaygain",
        action="store_true",
        help="Skip ReplayGain normalization step",
    )

    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    if not input_dir.is_dir():
        print(f"Error: '{input_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    mp3_files = sorted(input_dir.glob("*.mp3"))
    if not mp3_files:
        print(f"No MP3 files found in '{input_dir}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(mp3_files)} MP3 file(s) in '{input_dir}'.")

    if args.output_dir:
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = input_dir

    if not args.skip_silence_strip:
        print("\n[1/2] Stripping silence...")
        success = 0
        for mp3 in mp3_files:
            out = output_dir / mp3.name
            print(f"  {mp3.name}", end="", flush=True)
            if process_file(mp3, out, args.silence_threshold, args.chunk_size):
                print(" done")
                success += 1
            else:
                print(" FAILED")
        print(f"  {success}/{len(mp3_files)} files stripped.")
    else:
        print("[1/2] Silence stripping skipped.")

    if not args.skip_replaygain:
        print("\n[2/2] Applying ReplayGain normalization...")
        if apply_replaygain(output_dir):
            print("  ReplayGain applied.")
        else:
            sys.exit(1)
    else:
        print("[2/2] ReplayGain skipped.")

    print("\nDone.")


if __name__ == "__main__":
    main()
