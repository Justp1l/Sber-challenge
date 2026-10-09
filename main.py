import cv2
import numpy as np
from pathlib import Path
import math

def main() :
    video = cv2.VideoCapture('.\\raw_data\\output_robot_pov.mp4')
    if not video.isOpened():
        print("Ошибка: Не удалось открыть видео.")
        return
    output_path = '.\\rendered_video.mp4'
    video_fps = video.get(cv2.CAP_PROP_FPS)
    video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, video_fps, (video_width, video_height))
    
    featured_params = dict(
       maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7, 
    )
    
    lk_params = dict(
        winSize=(15, 15),
        maxLevel=2,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
    )
    
    ret, prev_frame = video.read()
    if not ret:
        print("There are no video more")
        return
    
    out.write(prev_frame)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    points_0 = cv2.goodFeaturesToTrack(prev_gray, **featured_params)
    
    while True:
        ret, frame = video.read()
        if not ret:
            break
        if points_0 is None or len(points_0) < 5:
            points_0 = cv2.goodFeaturesToTrack(prev_gray, mask=None, **featured_params)
            if points_0 is None:
                continue
            
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        points_1, st, err = cv2.calcOpticalFlowPyrLK(
            prev_gray, frame_gray, points_0, None, **lk_params
        )
        
        good_new = points_1[st == 1]
        good_old = points_0[st == 1]
        
        
        if len(good_new) > 0 :
            dx_distances = np.abs(good_new[:, 0] - good_old[:, 0])
            x_total = np.mean(dx_distances)
        else:
            x_total = 0
            
        dx_threshold = 5
        if x_total > dx_threshold:
            out.write(frame)
            prev_gray = frame_gray.copy()
            points_0 = good_new.reshape(-1,1,2)
        
    video.release()
    out.release()
    print("Released!")
    
def find_difference():
    original_video_path = Path(".\\raw_data\\output_robot_pov.mp4")
    original_video = cv2.VideoCapture(original_video_path)
    frames_original = int(original_video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    sliced_video_path = Path("rendered_video.mp4")
    sliced_video = cv2.VideoCapture(sliced_video_path)
    frames_sliced = int(sliced_video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    frames_difference =  frames_original-frames_sliced
    frames_multiplicity = frames_original / frames_sliced
    print(f"""
----------Данные---------------------------------------
Оригинал {original_video_path.name} содержит {frames_original} кадров;
Отрендеренное видео {sliced_video_path.name} содержит {frames_sliced} кадров.
----------Расчёт---------------------------------------
Разница между отрендеренным {sliced_video_path.name} и оригинальным видео по {original_video_path.name} составляет {frames_difference}. 
Сокращённое видео в ~{round(frames_multiplicity,2)} раз меньше по кадрам, чем оригинал,
способ позволил сэкономить {frames_difference} итераций (поисков объекта на картинке)
""")
    
if __name__ == '__main__':
    main()
    find_difference()
    