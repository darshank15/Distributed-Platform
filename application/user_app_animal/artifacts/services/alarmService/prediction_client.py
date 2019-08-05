# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""A client that performs inferences on a ResNet model using the REST API.

The client downloads a test image of a cat, queries the server over the REST API
with the test image repeatedly and measures how long it takes to respond.

The client expects a TensorFlow Serving ModelServer running a ResNet SavedModel
from:

https://github.com/tensorflow/models/tree/master/official/resnet#pre-trained-model

The SavedModel must be one that can take JPEG images as inputs.

Typical usage example:

    resnet_client.py
"""

from __future__ import print_function

import base64
import requests

#from image_pygame import *

# The server URL specifies the endpoint of your server running the ResNet
# model with the name "resnet" and using the predict interface.
# SERVER_URL = 'http://localhost:8501/v1/models/resnet:predict'
#SERVER_URL = 'http://172.17.0.2:8501/v1/models/face_rec:predict'

# The image URL is the location of the image we should send to the server
#IMAGE_URL = 'https://tensorflow.org/images/blogs/serving/cat.jpg'
#IMAGE_URL = "https://i.kinja-img.com/gawker-media/image/upload/s--HqfzgkTd--/c_scale,f_auto,fl_progressive,q_80,w_800/wp2qinp6fu0d8guhex9v.jpg"
#cam = MyCamera()
#img = cam.pic_cv2()

#IMAGE_URL="http://localhost:8000/new_pic.jpg"
#IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Cobra.jpg/800px-Cobra.jpg"

def main(img,SERVER_URL):
  # Download the image
  #dl_request = requests.get(IMAGE_URL, stream=True)
  #dl_request.raise_for_status()

  # Compose a JSON Predict request (send JPEG image in base64).
  #jpeg_bytes = base64.b64encode(dl_request.content).decode('utf-8')
  jpeg_bytes = base64.b64encode(img).decode('utf-8')
  predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes

  # Send few requests to warm-up the model.
  # for _ in range(3):
  #   response = requests.post(SERVER_URL, data=predict_request)
  #   response.raise_for_status()

  # Send few actual requests and report average latency.
  # total_time = 0
  # num_requests = 10
  # for _ in range(num_requests):
  response = requests.post(SERVER_URL, data=predict_request)
  response.raise_for_status()
  # total_time += response.elapsed.total_seconds()
  prediction = response.json()['predictions'][0]

  # print('Prediction class: {}, avg latency: {} ms'.format(prediction['classes'], (total_time*1000)/num_requests))
  return prediction

if __name__ == '__main__':
  imgg = open('new_pic.jpg', 'r')
  img = imgg.read(10000000)
  main(img)
