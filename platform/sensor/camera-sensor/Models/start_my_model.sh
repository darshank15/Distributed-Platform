echo dhawal@A1 | sudo -S docker run --name="my_model1" -p 8901:8501 --mount type=bind,source=/home/dhawal/iris/,target=/models/my_model1/ -e MODEL_NAME=my_model1 -t tensorflow/serving	
# echo dhawal@A1 | sudo -S docker run --name="Sonar" -p 8900:8501 --mount type=bind,source=/home/dhawal/Sonar/tmp/sonar,target=/models/Sonar -e MODEL_NAME=Sonar -t tensorflow/serving


sudo docker run --name="face_rec" -p 8901:8501 --mount type=bind,source=/home/rajesh/Desktop/IAS-Project/Models/face_serving/serving_model,target=/models/face_rec -e MODEL_NAME=face_rec -t tensorflow/serving


GET http://localhost:8501/v1/models/face_rec/versions/1

http://host:port/v1/models/${MODEL_NAME}[/versions/${MODEL_VERSION}]/metadata

http://localhost:8501/v1/models/face_rec/versions/1/metadata


http://172.17.0.2:8501/v1/models/face_rec/metadata

POST http://172.17.0.2:8501/v1/models/face_rec:classify
|regress)


curl -X POST \
 http://192.168.43.227:45017/v1/models/my_model2/versions/1:predict  \
 -d '{"signature_name":"predict","instances":[{"sepal_length":[6.8],"sepal_width":[3.2],"petal_length":[5.9],"petal_width":[2.3]}]}'

curl -X POST \
 http://172.17.0.2:8501/v1/models/face_rec:predict  \
 -d '{"signature_name":"predict","instances":[{"sepal_length":[6.8],"sepal_width":[3.2],"petal_length":[5.9],"petal_width":[2.3]}]}'
