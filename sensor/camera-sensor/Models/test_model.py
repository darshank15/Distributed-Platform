import time

from resnet_client import *
from image_pygame import *

while (1):
    cam = MyCamera()
    img = cam.pic_cv2()
    time.sleep(1)
    main()
    time.sleep(5)