#python
#mapper_webcam_capture.py
from webcam import Webcam

_file = 'BLANK.MP4'
_fr = ''

def start_webcam(video_source=0, frame_rate = 12):
    webcam_12_fps = Webcam(src=video_source, max_frame_rate=frame_rate, as_bgr=True, simulate_webcam=True)
    video_writer = cv2.VideoWriter(filename=_file, fourcc=cv2.VideoWriter_fourcc(*'mp4v'), fps=12, frameSize=(webcam_12_fps.w, webcam_12_fps.h))

    for frame in webcam_12_fps:
        video_writer.write(frame)
        _fr = frame
        video_writer.release()

def set_file_save(file_name='FILE.MP4'):
    _file = file_name

def get_file_saved():
    return _file

def get_frame():
    return _fr