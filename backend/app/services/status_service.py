from threading import Lock


_video_status = {}

_lock = Lock()


def set_status(video_id, status, progress, message):
    with _lock:
        _video_status[video_id] = {
            "video_id": video_id,
            "status": status,
            "progress": progress,
            "message": message,
        }


def get_status(video_id):
    with _lock:
        return _video_status.get(
            video_id,
            {
                "video_id": video_id,
                "status": "not_found",
                "progress": 0,
                "message": "Video not found.",
            }
        )