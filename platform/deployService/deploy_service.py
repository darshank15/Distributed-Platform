from flask import Flask,request, render_template
from werkzeug import secure_filename
import os,json
from threading import Thread
from time import sleep
import time,requests
import datetime
from Logger import Logger
import logging,random
import signal
import socket
import sys

sdURL = sys.argv[1]
rabbitip = sys.argv[2]

###################################################
# logger = Logger("amqp://admin:admin@"+rabbitip+"//")
# my_logger = logging.getLogger('test_logger')
# my_logger.setLevel(logging.DEBUG)

# # rabbitmq handler
# logHandler = Logger("amqp://admin:admin@"+rabbitip+"//")

# # adding rabbitmq handler
# my_logger.addHandler(logHandler)
################################################

app = Flask(__name__)

ip = sys.argv[3]
port="49005"
serviceName = "deployService"

response=requests.get(url=sdURL+"/get_service_ip/dbService")
loaddata = response.json()
ipd = loaddata['ip']
portd = loaddata['port']
URLd = "http://"+ipd+":"+str(portd)+"/db_interaction"

@app.route('/health')
def health():
    return "OK"

def handler(signal, frame):
    global ip,port,serviceName,sdURL
    print('CTRL-C pressed!')
    unregister(ip, port, serviceName, sdURL)
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

def unregister(ip, port, serviceName, sdURL):
    print('Inside UnRegister')

    data = {"serviceName":serviceName, "IP":ip, "PORT":port }
    url = sdURL + '/unregister_service'
    print(url)
    print('Response:', requests.post(url, json=data))


def register(ip, port, serviceName, sdURL):
    print('Inside register')

    data = {"serviceName":serviceName, "IP":ip, "PORT":port }
    print('Response:', requests.post(sdURL + '/register_service', json=data))



@app.route('/deployService',methods=['POST'])
def deployModelPhase():
    ###################################################3
    data = request.data
    location=json.loads(data)
    deploy_loc=location['deploy_loc']
    modelName=location['modelName']
    print(deploy_loc)
    print(modelName)
    query="select file_name from model where model_name='"+modelName+"'"
    r=requests.post(url=URLd,data=query)
    print(r)
    data = r.json()
    print(data)
    modelfilename = data[0][0]
    modelpath = "user_app/artifacts/models/"+modelName+"/"
    ####################################################3


    # my_logger.debug('Deploy Service \t Started deploy')
    print("Deploy")
    # modelName = request.args.get('model')
    listOfDict = {}
    # jsonfile="config.json"
    commands = '''
if [ -x "$(command -v docker)" ]; then
    echo "Update docker"
else
    echo "Install docker"
    sudo apt-get install curl
    sudo curl -sSL https://get.docker.com/ | sh
fi
    '''
    # data = request.get_json()
    





    #####################################################################
    # data =request.data
    # datadict=json.loads(data)
    # print(type(datadict))
    # print(datadict)
    # sched = {}
    # i=datadict
    ##############################################
    


    ################################################
    if deploy_loc != "Gateway":
        query = "select type from model where model_name='"+modelName+"'"
        r=requests.post(url=URLd,data=query)
        data = r.json()
        mtype = data[0][0]

        if mtype == "exclusive":
            URL = sdURL+"/get_exclusive_server"
            response=requests.get(url=URL)
            loaddata = response.json()
            if 'ip' not in loaddata.keys():
                return "No exclusive server available"
            else:
                ip = loaddata['ip']
                uname = loaddata['username']
                password = loaddata['password']
        else:
            URL = sdURL+"/get_free_server"
            response=requests.get(url=URL)
            loaddata = response.json()
            ip = loaddata['ip']
            uname = loaddata['username']
            password = loaddata['password']

        port = random.randint(50000,55000)
        deploy_soc=ip+":"+str(port)
        query = "select model_id from model where model_name='"+modelName+"'"
        r=requests.post(url=URLd,data=query)
        data = r.json()
        model_id = data[0][0]
        query = "update schedule set deploy_socket='"+deploy_soc+"',uname='"+uname+"',password='"+password+"' where model_id="+str(model_id)
        r=requests.post(url=URL,data=query)
    else:
        # ip = i['DeployIp']
        # uname = i['DeployUserName']
        # password = i['DeployPassword']
        # port = i['port']
        
        deploy_socket=location['deploy_socket']
        ip_port=deploy_socket.split(':')
        ip = ip_port[0]
        port = ip_port[1]
        query="select uname,password from gateway where ip='"+ip+"'"
        r=requests.post(url=URLd,data=query)
        data = r.json()
        uname = data[0][0]
        # uname = "rushit"
        password = data[0][1] 
        # password = "jasani123"
        
    
    # fname=i["Type"]
    
    # modelfilename = i['FileName']
    # modelName = i['Modelname']
    # modelpath = i["ModelPath"]
    # start = i["StartTime"]
    # end = i["EndTime"]
    # count = i["Count"]
    # repeat = i["Repeat"]
    # stream_ip = i["InputStream"]
    # interval = i["Interval"]
    # repeat_period = i["Repeat_Period"]
    # action = i["ActionName"]
    # usecase = i["UseCase"]
    # stream_ip = "192.168.43.54"
    print("------------",modelfilename)
    # dynamic1 = "unzip " + modelfilename
    dynamic2 = "echo " + password + " | sudo -S apt-get update"
    dynamic3 = "echo " + password +" | sudo -S docker pull tensorflow/serving"
    dynamic4 = "sudo docker stop $(echo " + password + " | sudo -S docker ps -aq)"
    dynamic5 = "echo " + password + " | sudo -S docker run --name=" + "\"" + modelName + "\"" + " -p " + str(port) + ":8501 --mount type=bind,source=/home/" + uname + "/nfs/"+modelpath+",target=/models/"+modelName+" -e MODEL_NAME="+modelName+" -t tensorflow/serving"
    # dynamic6 = "nohup sshpass -p " + password + " ssh " +  ip +" -l " + uname + " 'docker kill "+modelName + "'" + " &"
    # dynamic7 = "nohup sshpass -p " + password + " ssh " +  ip +" -l " + uname + " 'docker rm "+modelName + "'" + " &"
    dynamic6 = "echo " + password + " | " +"sudo -S docker kill " + modelName
    dynamic7 = "echo " + password + " | " +"sudo -S docker rm " + modelName

    # commands = dynamic1 + "\n" + commands + "\n" + dynamic3 +"\n" + dynamic4 + "\n"
    commands = commands + "\n" + dynamic3 +"\n" + dynamic4 + "\n"

    remotescript = "script_" + modelName + ".sh"
    scriptName = "./nfs/script_" + modelName + ".sh"
    f = open(scriptName,"w+")
    f.write(commands)
    f.close()

    start_s = "./nfs/start_" + modelName + ".sh"
    f = open(start_s,"w+")
    f.write(dynamic5)
    f.close()

    dynamicX = dynamic6 + "\n" + dynamic7
    stop_s = "./nfs/stop_" + modelName + ".sh"
    f = open(stop_s,"w+")
    # f.write()
    f.write(dynamicX)
    f.close()

    # cmd1 = "sshpass -p " + password + " scp -o StrictHostKeyChecking=no " + scriptName + " " + uname + "@" + ip + ":" + scriptName
    # cmd1_1 = "sshpass -p " + password + " scp -o StrictHostKeyChecking=no " + start_s + " " + uname + "@" + ip + ":" + start_s
    # cmd1_2 = "sshpass -p " + password + " scp -o StrictHostKeyChecking=no " + stop_s + " " + uname + "@" + ip + ":" + stop_s
    # cmd2 = "sshpass -p " + password + " scp -o StrictHostKeyChecking=no " + path + modelfilename + " " + uname + "@" + ip + ":" + modelfilename
    cmd3 = "nohup sshpass -p " + password + " ssh -o StrictHostKeyChecking=no " + ip + " -l " + uname + " bash "+ "/home/" + uname + "/nfs/"+remotescript + " &"

    print("Before calling")

    # tempcmd = "sshpass -p dhawal@A1 ssh -o StrictHostKeyChecking=no dhawal@10.42.0.1"
    # os.system(tempcmd)
    # os.system(cmd1)
    # os.system(cmd1_1)
    # os.system(cmd1_2)
    # os.system(cmd2)
    os.system(cmd3)

    # sched = {'InputStreamIp': stream_ip,'filename':modelName,'modelname':modelName,'uname':uname,'password':password,'ip':ip,'port':port,'start_command':dynamic5,'end_command':dynamic6,
    #                                             'action':action,'usecase':usecase}

            
    # print("Call Schedule")
    # my_logger.debug('Deploy Service \t Call Schedule')

    # # URL = "http://192.168.43.54:5003/get_service_ip/DeploymentService"
    # # response=requests.get(url=URL)
    # # sched_data = response.json()
    # # s_ip = sched_data['ip']
    # # s_port = sched_data['port']
    # # url = "http://"+s_ip+":"+s_port+"/ScheduleService"

    # url = "http://10.42.0.238:49000/ScheduleService"
    
    # # thread = Thread(target=caller_function,args=(url,sched,))
    # # thread.start()
    # caller_function(url,sched)
    # print("After Thread call")

    # r = json.dumps(sched)
    # url='http://127.0.0.1:8882/ScheduleService'
    # response = requests.post(url,data=r)
    # my_logger.debug('Deploy Service \t Done Deploy')
    return "From deploy"
        
register(ip,port,serviceName,sdURL)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=49005,debug=False,threaded=True)
