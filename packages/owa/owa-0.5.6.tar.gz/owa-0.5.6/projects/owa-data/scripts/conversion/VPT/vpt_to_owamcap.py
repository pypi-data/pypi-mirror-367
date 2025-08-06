#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcap-owa-support==0.5.5",
#   "owa-core==0.5.5",
#   "owa-msgs==0.5.5",
#   "owa-env-desktop==0.5.5",
#   "tqdm",
#   "rich",
# ]
# [tool.uv]
# exclude-newer = "2025-08-01T12:00:00Z"
# ///

import argparse
import json
import os
import typing
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from rich import print
from tqdm import tqdm

from mcap_owa.highlevel import OWAMcapReader, OWAMcapWriter
from owa.env.desktop.constants import VK
from owa.msgs.desktop.keyboard import KeyboardEvent
from owa.msgs.desktop.mouse import RawMouseEvent
from owa.msgs.desktop.screen import ScreenCaptured
from owa.msgs.desktop.window import WindowInfo

# Constants for VPT conversion
VPT_INTERVAL_TICK_NS = 50_000_000  # 50 ms interval per tick
VPT_EXPECTED_TICKS = 6000  # 5 minutes of 50ms ticks
VPT_X_RESOLUTION = 1280
VPT_Y_RESOLUTION = 720


# ref: https://github.com/openai/Video-Pre-Training/blob/4ea1e8e0eddcdd5ae3cc88621a80c434f22b7f3d/run_inverse_dynamics_model.py#L17
VPT_KEYBOARD_BUTTON_MAPPING = {
    "key.keyboard.escape": "ESC",
    "key.keyboard.s": "back",
    "key.keyboard.q": "drop",
    "key.keyboard.w": "forward",
    "key.keyboard.1": "hotbar.1",
    "key.keyboard.2": "hotbar.2",
    "key.keyboard.3": "hotbar.3",
    "key.keyboard.4": "hotbar.4",
    "key.keyboard.5": "hotbar.5",
    "key.keyboard.6": "hotbar.6",
    "key.keyboard.7": "hotbar.7",
    "key.keyboard.8": "hotbar.8",
    "key.keyboard.9": "hotbar.9",
    "key.keyboard.e": "inventory",
    "key.keyboard.space": "jump",
    "key.keyboard.a": "left",
    "key.keyboard.d": "right",
    "key.keyboard.left.shift": "sneak",
    "key.keyboard.left.control": "sprint",
    "key.keyboard.f": "swapHands",
}

VPT_KEYBOARD_VK_MAPPING = {
    "key.keyboard.escape": VK.ESCAPE,
    "key.keyboard.s": VK.KEY_S,
    "key.keyboard.q": VK.KEY_Q,
    "key.keyboard.w": VK.KEY_W,
    "key.keyboard.1": VK.KEY_1,
    "key.keyboard.2": VK.KEY_2,
    "key.keyboard.3": VK.KEY_3,
    "key.keyboard.4": VK.KEY_4,
    "key.keyboard.5": VK.KEY_5,
    "key.keyboard.6": VK.KEY_6,
    "key.keyboard.7": VK.KEY_7,
    "key.keyboard.8": VK.KEY_8,
    "key.keyboard.9": VK.KEY_9,
    "key.keyboard.e": VK.KEY_E,
    "key.keyboard.space": VK.SPACE,
    "key.keyboard.a": VK.KEY_A,
    "key.keyboard.d": VK.KEY_D,
    "key.keyboard.left.shift": VK.LSHIFT,
    "key.keyboard.left.control": VK.LCONTROL,
    "key.keyboard.f": VK.KEY_F,
}


def vpt_generate_target_list_file(
    vpt_folder_path: Path,
    vpt_media_ext: str,
    target_list_file: typing.Union[str, bytes, os.PathLike],
):
    """
    Filter VPT files that have valid jsonl files paired with (mp4|mkv), and are 5 minutes long.
    The list of valid target files is saved to `target_list_file`.
    """

    all_media_stems = set([f.stem for f in vpt_folder_path.iterdir() if f.suffix == vpt_media_ext and f.is_file()])

    # Get all files with their full path and creation time
    all_jsonl_files = [
        (f, f.stat().st_ctime)
        for f in vpt_folder_path.iterdir()
        if f.suffix == ".jsonl" and f.is_file() and f.stem in all_media_stems
    ]

    # Sort by creation time (oldest first)
    all_jsonl_files.sort(key=lambda x: x[1])

    print(f"{len(all_jsonl_files)} files found in {vpt_folder_path}.")

    target_files = []

    for file_name_jsonl, _ in tqdm(all_jsonl_files):
        try:
            with open(file_name_jsonl, "r") as f:  # jsonl file
                lines = f.readlines()  # Read non-empty lines
                if len(lines) == VPT_EXPECTED_TICKS:
                    target_files.append(file_name_jsonl)
        except Exception as e:
            print(f"Error reading {file_name_jsonl}. Skipping. Error: {e}")

    print(f"{len(target_files)=}")

    with open(target_list_file, "w") as f:
        for file in target_files:
            f.write(f"{file}\n")


def process_single_file(jsonl_file_path, vpt_media_ext):
    """Process a single VPT file and convert it to OWAMcap format."""
    # Convert the file to OWAMcap format
    mcap_file_path = jsonl_file_path.with_suffix(".mcap")
    media_file_path = jsonl_file_path.with_suffix(vpt_media_ext)

    # Writing messages to an OWAMcap file
    unix_epoch_ns = 0  # Unix epoch time in nanoseconds (Jan 1, 1970)

    try:
        with open(jsonl_file_path, "r") as f:  # jsonl file
            lines = [line.strip() for line in f.readlines()]  # Read non-empty lines
            assert len(lines) == VPT_EXPECTED_TICKS, (
                f"File {jsonl_file_path} does not have {VPT_EXPECTED_TICKS=} lines. It has {len(lines)} lines."
            )
            ticks = [json.loads(line) for line in lines]
    except Exception as e:
        print(f"Error reading {jsonl_file_path}. Skipping. Error: {e}")
        return

    with OWAMcapWriter(mcap_file_path) as writer:
        topic = "window"
        event = WindowInfo(
            title=f"VPT-{mcap_file_path}",
            rect=[0, 0, VPT_X_RESOLUTION, VPT_Y_RESOLUTION],
            hWnd=-1,
        )
        writer.write_message(event, topic=topic, timestamp=unix_epoch_ns)

        keyboard_state = set()
        button_state = set()

        ## SCREEN EVENT
        topic = "screen"
        from owa.msgs.desktop.screen import MediaRef

        event = ScreenCaptured(
            utc_ns=unix_epoch_ns,
            source_shape=(VPT_X_RESOLUTION, VPT_Y_RESOLUTION),
            shape=(VPT_X_RESOLUTION, VPT_Y_RESOLUTION),
            media_ref=MediaRef(uri=str(media_file_path.name), pts_ns=unix_epoch_ns),
        )
        writer.write_message(event, topic=topic, timestamp=unix_epoch_ns)

        for i, tick in enumerate(ticks):
            # milli_timestamp = tick["milli"] # we don't use this value of VPT since it seems inaccurate
            log_time = unix_epoch_ns + ((i + 1) * VPT_INTERVAL_TICK_NS)

            ## SCREEN EVENT
            topic = "screen"
            event = ScreenCaptured(
                utc_ns=log_time,
                source_shape=(VPT_X_RESOLUTION, VPT_Y_RESOLUTION),
                shape=(VPT_X_RESOLUTION, VPT_Y_RESOLUTION),
                media_ref=MediaRef(uri=str(media_file_path.name), pts_ns=log_time),
            )
            writer.write_message(event, topic=topic, timestamp=log_time)

            ## KEYBOARD EVENT
            current_tick_keys = tick["keyboard"]["keys"]

            # NOTE: we suppose the keys are pressed/released in the fastest observable timing of tick.

            # release keys that are not in the current tick
            for state_key in list(keyboard_state):
                if state_key not in current_tick_keys:
                    keyboard_state.remove(state_key)
                    topic = "keyboard"
                    event = KeyboardEvent(event_type="release", vk=VPT_KEYBOARD_VK_MAPPING[state_key])
                    writer.write_message(event, topic=topic, timestamp=log_time)

            # press keys that are in the current tick, and not already pressed
            for key in current_tick_keys:
                if key not in VPT_KEYBOARD_VK_MAPPING:
                    continue  # skip keys that are not in the mapping
                else:
                    if key in keyboard_state:
                        continue  # already pressed
                    else:
                        keyboard_state.add(key)
                        topic = "keyboard"
                        event = KeyboardEvent(event_type="press", vk=VPT_KEYBOARD_VK_MAPPING[key])
                        writer.write_message(event, topic=topic, timestamp=log_time)

            ## MOUSE EVENT
            dx = tick["mouse"]["dx"]
            dy = tick["mouse"]["dy"]

            # NOTE: we suppose the mouse coordinates are integer values
            dx = int(round(dx))
            dy = int(round(dy))

            if dx != 0 or dy != 0:
                topic = "mouse/raw"
                event = RawMouseEvent(
                    last_x=dx,
                    last_y=dy,
                    button_flags=RawMouseEvent.ButtonFlags.RI_MOUSE_NOP,
                    timestamp=log_time,
                )
                writer.write_message(event, topic=topic, timestamp=log_time)

            # mouse buttons : https://github.com/openai/Video-Pre-Training/blob/4ea1e8e0eddcdd5ae3cc88621a80c434f22b7f3d/run_inverse_dynamics_model.py#L114-L123
            # 0 : left click, 1 : right click, 2 : middle click
            current_tick_buttons = tick["mouse"]["buttons"]

            # release buttons that are not in the current tick
            for state_button in list(button_state):
                if state_button not in current_tick_buttons:
                    button_state.remove(state_button)
                    topic = "mouse/raw"
                    if state_button == 0:  # left click
                        button_flags = RawMouseEvent.ButtonFlags.RI_MOUSE_LEFT_BUTTON_UP
                    elif state_button == 1:  # right click
                        button_flags = RawMouseEvent.ButtonFlags.RI_MOUSE_RIGHT_BUTTON_UP
                    elif state_button == 2:  # middle click
                        button_flags = RawMouseEvent.ButtonFlags.RI_MOUSE_MIDDLE_BUTTON_UP
                    else:
                        print(f"Unknown mouse button {state_button=} in VPT data.")
                        continue

                    event = RawMouseEvent(
                        last_x=0,
                        last_y=0,
                        button_flags=button_flags,
                        timestamp=log_time,
                    )
                    writer.write_message(event, topic=topic, timestamp=log_time)

            # press buttons that are in the current tick, and not already pressed
            for button in current_tick_buttons:
                if button in button_state:
                    continue  # already pressed
                else:
                    button_state.add(button)
                    topic = "mouse/raw"
                    if button == 0:  # left click
                        button_flags = RawMouseEvent.ButtonFlags.RI_MOUSE_LEFT_BUTTON_DOWN
                    elif button == 1:  # right click
                        button_flags = RawMouseEvent.ButtonFlags.RI_MOUSE_RIGHT_BUTTON_DOWN
                    elif button == 2:  # middle click
                        button_flags = RawMouseEvent.ButtonFlags.RI_MOUSE_MIDDLE_BUTTON_DOWN
                    else:
                        print(f"Unknown mouse button {button=} in VPT data.")
                        continue

                    event = RawMouseEvent(
                        last_x=0,
                        last_y=0,
                        button_flags=button_flags,
                        timestamp=log_time,
                    )
                    writer.write_message(event, topic=topic, timestamp=log_time)


def main(
    vpt_folder_path: Path, vpt_media_ext: str, vpt_target_list_file: str, max_workers: typing.Optional[int] = None
):
    if max_workers is None:
        max_workers = 50
    print(f"Using {max_workers} worker processes.")

    if not Path(vpt_target_list_file).exists():
        print(f"{vpt_target_list_file=} does not exist. Generating it.")
        vpt_generate_target_list_file(vpt_folder_path, vpt_media_ext, vpt_target_list_file)
        print(f"{vpt_target_list_file=} generated.")

    with open(vpt_target_list_file, "r") as f:
        vpt_target_list = [Path(line.strip()) for line in f.readlines()]
        print(f"We will convert {len(vpt_target_list)=} VPT files.")

    # Use ProcessPoolExecutor for multiprocessing
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_single_file, jsonl_file_path, vpt_media_ext): jsonl_file_path
            for jsonl_file_path in vpt_target_list
        }

        # Process completed tasks with progress bar
        with tqdm(total=len(vpt_target_list), desc="Converting files") as pbar:
            for future in as_completed(future_to_file):
                jsonl_file_path = future_to_file[future]
                try:
                    future.result()  # Get the result (or raise exception if there was one)
                    print(f"Successfully converted {jsonl_file_path}")
                except Exception as exc:
                    print(f"File {jsonl_file_path} generated an exception: {exc}")
                finally:
                    pbar.update(1)


def read_mcap(file_path="expert.mcap", num_messages=100):
    # Reading messages from an OWAMcap file
    cnt = 0
    with OWAMcapReader(file_path) as reader:
        for mcap_msg in reader.iter_messages():
            print(f"Topic: {mcap_msg.topic}, Timestamp: {mcap_msg.timestamp}, Message: {mcap_msg.decoded}")
            cnt += 1
            if cnt > num_messages:
                break


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert VPT dataset files to OWAMcap format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--vpt-folder-path",
        type=Path,
        default=Path("/mnt/raid12/datasets/owa/mcaps/vpt").expanduser(),
        help="Path to VPT data folder containing paired (mp4|mkv) and jsonl files",
    )

    parser.add_argument(
        "--vpt-media-ext",
        type=str,
        default=".mkv",
        choices=[".mp4", ".mkv"],
        help="Media file extension for VPT dataset",
    )

    parser.add_argument(
        "--vpt-target-list-file",
        type=str,
        default="./vpt_target_files.txt",
        help="File to store the list of target VPT files to convert",
    )

    parser.add_argument(
        "--max-workers", type=int, default=50, help="Maximum number of worker processes for parallel conversion"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(
        vpt_folder_path=args.vpt_folder_path,
        vpt_media_ext=args.vpt_media_ext,
        vpt_target_list_file=args.vpt_target_list_file,
        max_workers=args.max_workers,
    )
    # read_mcap()
