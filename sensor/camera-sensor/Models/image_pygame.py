import pygame
import pygame.camera
from cv2 import *
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class MyCamera:
    def take_picture(self):
        pygame.camera.init()
        #pygame.camera.list_camera() #Camera detected or not
        cam = pygame.camera.Camera("/dev/video0",(640,480))
        cam.start()
        img = cam.get_image()
        #pygame.image.save(img,"filename.jpg")
        return img
    
    def pic_cv2(self):
        cam = VideoCapture(0)   # 0 -> index of camera
        s, img = cam.read()
        if s:    # frame captured without any errors
            #namedWindow("cam-test",CV_WINDOW_AUTOSIZE)
            imshow("cam-test",img)
            #waitKey(0)
            destroyWindow("cam-test")
            imwrite("filename.jpg",img) #save image
            return img
cam = MyCamera()
img = cam.pic_cv2()
print(type(img))
