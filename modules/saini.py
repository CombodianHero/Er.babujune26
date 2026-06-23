"""
saini.py — Backward-compatible helper aliases.
drm_handler.py imports this as `import saini as helper`
All actual implementations live in utils.py.
"""
from utils import (
    get_video_duration      as duration,
    get_mps_and_keys,
    run_cmd                 as exec,
    run_parallel            as pull_run,
    aio,
    download,
    parse_vid_info,
    vid_info,
    decrypt_and_merge_video,
    async_run               as run,
    old_download,
    human_readable_bytes    as human_readable_size,
    time_name,
    download_video,
    decrypt_file,
    download_and_decrypt_video,
    send_vid,
)
