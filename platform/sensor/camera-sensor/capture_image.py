#capture_image.py

from SimpleCV import Image, Camera

cam = Camera()
img = cam.getImage()
img.save("filename.jpg")