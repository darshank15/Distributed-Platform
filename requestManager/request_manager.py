from flask import Flask,request, render_template,redirect,url_for,session
from werkzeug import secure_filename
import os,json
from threading import Thread
from time import sleep
import time
import datetime
import requests
import numpy
from Logger import Logger
import logging
import xmltodict
import sys

homepath=os.path.expanduser("~")
UPLOAD_FOLDER = homepath+"/nfs/"
ALLOWED_EXTENSIONS = set(['txt', 'json', 'png', 'jpg', 'jpeg', 'gif', 'zip'])
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

sdURL = sys.argv[1]
rabbitIp = sys.argv[2]
###################################################
# logger = Logger("amqp://admin:admin@"+rabbitIp+"//")
# my_logger = logging.getLogger('test_logger')
# my_logger.setLevel(logging.DEBUG)

# # rabbitmq handler
# logHandler = Logger("amqp://admin:admin@"+rabbitIp+"//")

# # adding rabbitmq handler
# my_logger.addHandler(logHandler)
################################################

response=requests.get(url=sdURL+"/get_service_ip/dbService")
loaddata = response.json()
ipd = loaddata['ip']
portd = loaddata['port']
URLd = "http://"+ipd+":"+str(portd)+"/db_interaction"

@app.route('/health')
def health():
    return "OK"

@app.route('/deployWebApp')
def deployWebApp():
    return render_template('webapp.html')

def uifunction(execcmd):
	os.system(execcmd)

@app.route('/webservice', methods=['GET', 'POST'])
def webservice():
	model_file = request.files['model_file']

	if model_file.filename == '':
		return "Test Data file not found"
	if model_file and allowed_file(model_file.filename):
		filename = secure_filename(model_file.filename)
		model_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

	cmd = "unzip " + UPLOAD_FOLDER+filename + " -d "+UPLOAD_FOLDER
	os.system(cmd)
	filename = filename[:-4]
	path = UPLOAD_FOLDER+filename+"/main.py"
	execcmd = "nohup python3 "+path+" &"
	thread = Thread(target=uifunction,args=(execcmd,))
	thread.start()
	
	return "Your web-app hosted"

@app.route('/')
def index():
    # my_logger.debug('RequestManager Service \t Started RMS')
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_from_model_xml(path):
    print(path)
    with open(path, 'r') as f:
        xmlString = f.read()
             
        jsonString = json.dumps(xmltodict.parse(xmlString))
        actualJson = json.loads(jsonString)

        listmodels = actualJson['main']['models']['model']
        print(listmodels)
        finallist = []
        if type(listmodels) is not list:
            finallist.append(listmodels)
        else:
            finallist = listmodels

        uid = session['uid']
        status = "NO"
        for i in finallist:
            query = "insert into model (model_name,file_name,user_id,url,status,type) values ('"+i['modelName']+"','"+i['fileName']+"',"+str(uid)+",'"+i['predURLStructure']+"','"+status+"','"+i['type']+"')"
            print(query)
            r=requests.post(url=URLd,data=query)
            query = "select model_id from model where model_name='"+i['modelName']+"'"
            print(query)
            r=requests.post(url=URLd,data=query)
            data = r.json()
            m_id = data[0][0]
            if "dependencies" in i.keys():
	            s_type = i['dependencies']['sensor-type']
	            final_s_type = []

	            if type(s_type) is not list:
	            	final_s_type.append(s_type)
	            else:
	            	final_s_type = s_type
	            for i_type in final_s_type:
	            	query = "select sensor_id from sensor where type='"+i_type+"'"
	            	print(query)
	            	r=requests.post(url=URLd,data=query)
	            	data = r.json()
	            	s_id = data[0][0]
	            	query = "select user_sensor_id from user_sensor where user_id="+str(uid)+" and sensor_id="+str(s_id)
	            	print(query)
	            	r=requests.post(url=URLd,data=query)
	            	data = r.json()
	            	u_s_id = data[0][0]
	            	query = "insert into model_sensor (model_id,user_sensor_id) values ("+str(m_id)+","+str(u_s_id)+")"
	            	print(query)
	            	r=requests.post(url=URLd,data=query)


def read_from_service_xml(path):
    print(path)
    with open(path, 'r') as f:
        xmlString = f.read()
             
        jsonString = json.dumps(xmltodict.parse(xmlString))
        actualJson = json.loads(jsonString)

        listservices = actualJson['main']['services']['service']
        print(listservices)

        finallist = []
        if type(listservices) is not list:
            finallist.append(listservices)
        else:
            finallist = listservices

        uid = session['uid']
        status = "NO"
        for i in finallist:
        	if "dependencies" in i.keys():
        		if "model-dependency" in i['dependencies'].keys():
		            model_name = i['dependencies']['model-dependency']['model-name']
		            query = "select model_id from model where model_name='"+model_name+"'"
		            r=requests.post(url=URLd,data=query)
		            data = r.json()
		            model_id = data[0][0]
		            query = "insert into services (service_name,user_id,type,model_id) values ('"+i['serviceName']+"',"+str(uid)+",'"+i['type']+"',"+str(model_id)+")"
		            print(query)
		        else:
		        	query = "insert into services (service_name,user_id,type) values ('"+i['serviceName']+"',"+str(uid)+",'"+i['type']+"')"
		        	print(query)
		        r=requests.post(url=URLd,data=query)
		        query = "select service_id from services where service_name='"+i['serviceName']+"'"
		        r=requests.post(url=URLd,data=query)
		        data = r.json()
		        service_id = data[0][0]

		        if "sensor-dependency" in i['dependencies'].keys():
		        	s_type = i['dependencies']['sensor-dependency']['sensor-type']
		        	final_s_type = []

		        	if type(s_type) is not list:
		        		final_s_type.append(s_type)
		        	else:
		        		final_s_type = s_type

		        	for i_type in final_s_type:
		        		query = "select sensor_id from sensor where type='"+i_type+"'"
		        		r=requests.post(url=URLd,data=query)
		        		data = r.json()
		        		sensor_id = data[0][0]
		        		query = "select user_sensor_id from user_sensor where user_id="+str(uid)+" and sensor_id="+str(sensor_id)
		        		r=requests.post(url=URLd,data=query)
		        		data = r.json()
		        		u_sensor_id = data[0][0]
		        		query = "insert into service_sensor_dep (service_id,user_sensor_id) values ("+str(service_id)+","+str(u_sensor_id)+")"
		        		r=requests.post(url=URLd,data=query)

		        if "service-dependency" in i['dependencies'].keys():
		            service_name = i['dependencies']['service-dependency']['service-name']

		            final_service_name = []
		            if type(service_name) is not list:
		            	final_service_name.append(service_name)
		            else:
		            	final_service_name = service_name

		            for i_name in final_service_name:
		            	query = "select service_id from services where service_name='"+i_name+"'"
		            	r=requests.post(url=URLd,data=query)
		            	data = r.json()
		            	dep_service_id = data[0][0]
		            	query = "insert into services_dep (service_id,dep_service_id) values ("+str(service_id)+","+str(dep_service_id)+")"
		            	r=requests.post(url=URLd,data=query)
        	else:
        		query = "insert into services (service_name,user_id,type) values ('"+i['serviceName']+"',"+str(uid)+",'"+i['type']+"')"
        		print(query)
        		r=requests.post(url=URLd,data=query)


def read_from_gateway_xml(path):
    print(path)
    with open(path, 'r') as f:
        xmlString = f.read()
             
        jsonString = json.dumps(xmltodict.parse(xmlString))
        actualJson = json.loads(jsonString)

        listgateway = actualJson['main']['gateways']['gateway']
        print(listgateway)

        finallist = []
        if type(listgateway) is not list:
            finallist.append(listgateway)
        else:
            finallist = listgateway

        uid = session['uid']
        status = "NO"
        for i in finallist:
            query = "insert into gateway (ip,uname,password,location,gatewayname) values ('"+i['gatewayIP']+"','"+i['gatewayUname']+"','"+i['gatewayPassword']+"','"+i['gatewayLocation']+"','"+i['name']+"')"
            print(query)
            r=requests.post(url=URLd,data=query)

            if "dependencies" in i.keys():
	            query = "select gateway_id from gateway where ip = '"+ i['gatewayIP'] +"'"
	            print(query)
	            r=requests.post(url=URLd,data=query)
	            data = r.json()
	            g_id = data[0][0]
	            s_type = i['dependencies']['sensor-dependency']['sensor-type']
	            final_s_type = []
	            if type(s_type) is not list:
	            	final_s_type.append(s_type)
	            else:
	            	final_s_type = s_type

	            for i_type in final_s_type:
		            query = "select sensor_id from sensor where type = '"+ i_type +"'"
		            print(query)
		            r=requests.post(url=URLd,data=query)
		            data = r.json()
		            s_id = data[0][0]
		            query = "select user_sensor_id from user_sensor where user_id="+str(uid)+" and sensor_id="+str(s_id)
		            print(query)
		            r=requests.post(url=URLd,data=query)
		            data = r.json()
		            u_s_id = data[0][0]
		            query = "insert into gateway_sensor (gateway_id,user_sensor_id) values ("+str(g_id)+","+str(u_s_id)+")"
		            print(query)
		            r=requests.post(url=URLd,data=query)

def read_from_schedule_xml(path):
    print(path)
    with open(path, 'r') as f:
        xmlString = f.read()
             
        jsonString = json.dumps(xmltodict.parse(xmlString))
        actualJson = json.loads(jsonString)

        i = actualJson['main']['models']['scheduling']['model']
        print(i)
        model_name = i['model-name']
        uid = session['uid']
        status = "NO"
        query = "select model_id from model where model_name='"+model_name+"'"
        r=requests.post(url=URLd,data=query)
        data = r.json()
        model_id = data[0][0]
        query = "insert into schedule (start_time,end_time,interval_,count_,repeat_,deploy_socket,deploy_loc,model_id,repeat_period,indefinately,uname,password) values ('"+i['start-time']+"','"+i['end-time']+"',"+str(i['interval'])+","+str(i['count'])+",'"+i['repeat']+"','"+i['socket']+"','"+i['gateway-loc']+"',"+str(model_id)+","+str(i['repeat-period'])+",'"+i['indefinately']+"','"+i['uname']+"','"+i['password']+"')"
        print(query)
        r=requests.post(url=URLd,data=query)

        return i['model-name'],i['gateway-loc'],i['socket']


def read_from_sensor_xml(path):
    print(path)
    with open(path, 'r') as f:
        xmlString = f.read()
             
        jsonString = json.dumps(xmltodict.parse(xmlString))
        actualJson = json.loads(jsonString)

        listsensors = actualJson['main']['sensors']['sensor']
        print(listsensors)

        finallist = []
        if type(listsensors) is not list:
            finallist.append(listsensors)
        else:
            finallist = listsensors

        uid = session['uid']
        for i in finallist:
            type_ = i['sensorType']
            query = "select sensor_id from sensor where type='"+type_+"'"
            r=requests.post(url=URLd,data=query)
            data = r.json()
            sensor_id = data[0][0]
            query = "insert into user_sensor (user_id,sensor_id,sensor_location) values ("+str(uid)+","+str(sensor_id)+",'"+i['sensorLocation']+"')"
            print(query)
            r=requests.post(url=URLd,data=query)


@app.route('/deploy', methods=['GET', 'POST'])
def deploy():
    if request.method == 'GET':
        return "Bad Request"
    else:
        if 'model_file' not in request.files:
            #flash('No file part')
            return "No model_file file uploaded"


        model_file = request.files['model_file']
        # model_file.save(secure_filename(model_file.filename))


        if model_file.filename == '':
            return "No model_file selected file"

        if model_file and allowed_file(model_file.filename):
            filename = secure_filename(model_file.filename)
            model_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            folder = filename

        cmd1 = "unzip "+UPLOAD_FOLDER+folder+" -d "+UPLOAD_FOLDER
        os.system(cmd1)

        filename = filename[:-4]

        read_from_sensor_xml(UPLOAD_FOLDER+filename+"/deploy_config.xml")
        read_from_gateway_xml(UPLOAD_FOLDER+filename+"/deploy_config.xml")
        read_from_model_xml(UPLOAD_FOLDER+filename+"/deploy_config.xml")
        read_from_service_xml(UPLOAD_FOLDER+filename+"/deploy_config.xml")
        
        return render_template('index.html')

@app.route('/schedule_model')
def schedule_model():
    return render_template('schedule.html')

@app.route('/schedule_model_1',methods=['GET','POST'])
def schedule_model_1():

    modelname = request.form['modelname']
    model_file = request.files['model_file']
    print("*************",model_file)

    if model_file.filename == '':
        return "No model_file selected file"

    # if model_file and allowed_file(model_file.filename):
    filename = secure_filename(model_file.filename)
    model_file.save(os.path.join(UPLOAD_FOLDER+modelname, filename))
    print("$$$$$$$$$$$$$",UPLOAD_FOLDER+modelname+"/runtime/model/", filename)
    folder = filename
    modelname1,deploy_loc,deploy_socket = read_from_schedule_xml(UPLOAD_FOLDER+modelname+"/"+filename)

    # print("#############",deploy_loc)
    deploydata = {'modelName':modelname1,'deploy_loc':deploy_loc,'deploy_socket':deploy_socket}
    URL = sdURL+"/get_service_ip/deployService"
    response=requests.get(url=URL)
    loaddata = response.json()

    ip = loaddata['ip']
    port = loaddata['port']
    deploy_soc=ip+":"+port

    # deploydata = {'modelName':"Sonar",'deploy_loc':"Gateway",'deploy_socket':"192.168.43.110:8900"}

    URL = "http://"+deploy_soc+"/deployService"
    requests.post(url=URL,data=json.dumps(deploydata))

    URL = sdURL+"/get_service_ip/scheduleService"
    response=requests.get(url=URL)
    loaddata = response.json()

    ip = loaddata['ip']
    port = loaddata['port']
    deploy_soc=ip+":"+port

    scheduledata = {'modelName':modelname1}
    URL = "http://"+deploy_soc+"/ScheduleService"
    requests.post(url=URL,data=json.dumps(scheduledata))

    return redirect(url_for('.schedule_model'))



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_1',methods=['POST','GET'])
def login_1():

    email = request.form['name']
    password = request.form['password']
    query = "select * from user where name='"+email+"' and password='"+password+"'"
    r=requests.post(url=URLd,data=query)
    data = r.json()
    session['uid'] = data[0][0]
    return redirect(url_for('.login'))


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route('/signup_1', methods=['POST'])
def signup_1():
        
    first = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    password = request.form['password']
    
    # print(first)
    query = "insert into user (name,mobile_no,email,password) values('"+first+"','"+mobile+"','"+email+"','"+password+"')"
    r=requests.post(url=URLd,data=query)

    return redirect(url_for('.login'))

@app.route('/model_status')
def model_status():
    if 'uid' not in session:
        return "Please Login"
    uid = session['uid']
    query = "select * from model where user_id="+str(uid)
    r=requests.post(url=URLd,data=query)
    data = r.json()
    # print(data)
    return render_template('modelstatus.html',data=data)

path = {}

@app.route('/Service_status')
def Service_status():
    global path
    path = {}
    if 'uid' not in session:
        return "Please Login"
    uid = session['uid']
    query = "select * from services where user_id="+str(uid)
    r = requests.post(url=URLd,data=query)
    data = r.json()
    URL = sdURL+"/get_all_services"
    r=requests.get(url=URL)
    datax = r.json()
    datax = datax['services']
    # print(datax)
    for i in datax:
        path[i['serviceName']] = i['instances'][0]

    return render_template('servicestatus.html',data=data,path=path)

def servicehandler(sname):
    URL = sdURL+"/get_service_ip/"+sname
    response = requests.get(url=URL)
    res = response.json()
    if res == "Service not registered":
        time.sleep(10)
        response = requests.get(url=URL)
        res = response.json()
        if res == "Service not registered":
          query = "update services set status=\"NO\" where service_name='"+sname+"'"
          r = requests.post(url=URLd, data=query)
        else:
            query = "update services set status=\"YES\" where service_name='"+sname+"'"
            r = requests.post(url=URLd, data=query)
            URL = sdURL+"/get_service_ip/"+sname
            response=requests.get(url=URL)
            loaddata = response.json()
            ip = loaddata['ip']
            port = loaddata['port']
            deploy_soc = ip+":"+port
            url = "http://"+deploy_soc+"/"
            path[sname]=url
    else:
        query = "update services set status=\"YES\" where service_name='"+sname+"'"
        r = requests.post(url=URLd, data=query)
        URL = sdURL+"/get_service_ip/"+sname
        response=requests.get(url=URL)
        loaddata = response.json()
        ip = loaddata['ip']
        port = loaddata['port']
        deploy_soc = ip+":"+port
        url = "http://"+deploy_soc+"/"
        path[sname]=url


@app.route('/start_stop_service',methods=['GET','POST'])
def start_stop_service():
    sname = request.form['sname']
    type_ = request.form['type']
    print(sname)
    print(type_)

    if type_ == "start":
        model_file = request.files[sname]
        filename = secure_filename(model_file.filename)
        model_file.save(os.path.join(UPLOAD_FOLDER, filename))
        path = UPLOAD_FOLDER + filename
        with open(path, 'r') as f:
            xmlString = f.read()
             
            jsonString = json.dumps(xmltodict.parse(xmlString))
            actualJson = json.loads(jsonString)

        listservices = actualJson['main']['services']['service']
        print(listservices)

        query = "update services set mininstance="+str(listservices['minInstances'])+",maxinstance="+str(listservices['maxInstances'])+",highmark="+str(listservices['highMark'])+",lowmark="+str(listservices['lowMark'])+",minresponsetime='"+listservices['minResponseTime']+"'"+" where service_name='"+sname+"'"
        print(query)
        r=requests.post(url=URLd,data=query)

        query = "select service_id,type,mininstance from services where service_name='"+sname+"'"
        r = requests.post(url=URLd, data=query)
        data = r.json()
        service_id = data[0][0]
        stype = data[0][1]
        mininstance = data[0][2]

        query = "select dep_service_id from services_dep where service_id="+str(service_id)
        r = requests.post(url=URLd, data=query)
        try:
          data = r.json()

          URL = sdURL+"/get_all_services"
          r = requests.get(url=URL)
          data1 = r.json()
          dep_data = []
          for i in data1:
            query = "select service_id from services where service_name='"+i['serviceName']+"'"
            r = requests.post(url=URLd, data=query)
            ids = r.json()
            dep_data.append(ids[0][0])
          for i in data:
              if i[0] not in dep_data:
                  return "Dependent Service is not running"
        except:
          pass

        query = "select model_id from services where service_id="+str(service_id)
        r = requests.post(url=URLd, data=query)
        try:
          data = r.json()
          model_id = data[0][0]
          if model_id!=None:
              query = "select status from model where model_id="+str(model_id)
              r = requests.post(url=URLd, data=query)
              data = r.json()
              status = data[0][0]

              if status != "YES":
                  return "Dependent model is not running"
        except:
          pass

        while mininstance > 0:
            if stype == "exclusive":
                URL = sdURL+"/get_exclusive_server"
                response=requests.get(url=URL)
                loaddata = response.json()
                if 'ip' not in loaddata.keys():
                    return "No exclusive server available"
                else:
                    ip = loaddata['ip']
            else:
                URL = sdURL+"/get_free_server"
                response=requests.get(url=URL)
                loaddata = response.json()
                ip = loaddata['ip']

            print(ip)
            port = 8899
            deploy_soc=ip+":"+str(port)
            URL = "http://"+deploy_soc+"/start_service/"+sname
            r=requests.get(url=URL)
            # thread = Thread(target=servicehandler,args=(sname,))
            # thread.start()
            mininstance = mininstance - 1
    else:
        URL = sdURL+"/get_all_services"
        r=requests.get(url=URL)
        data = r.json()
        instances = []
        print(data)
        data = data['services']
        for i in data:
            if i['serviceName'] == sname:
                instances = i['instances']
                break
        print(instances)
        for i in instances:
            deploy_soc = i
            ip_port = deploy_soc.split(":")
            ip = ip_port[0]
            port = ip_port[1]
            dt = {'IP':ip,'PORT':port,'serviceName':sname}
            r = requests.post(url=sdURL+"/unregister_service", json=dt)
            URL = "http://"+ip+":"+str(8899)+"/stop_service/"+sname
            r=requests.get(url=URL)

    return redirect(url_for('.Service_status'))

@app.route('/platform')
def platform():
    return render_template('platform.html')

@app.route('/platform_1',methods=['GET','POST'])
def platform_db_initialization():
    if request.method == 'GET':
        return "Bad Request"
    else:
        if 'model_file' not in request.files:
            #flash('No file part')
            return "No model_file file uploaded"


        model_file = request.files['model_file']
        # model_file.save(secure_filename(model_file.filename))


        if model_file.filename == '':
            return "No model_file selected file"

        # if model_file and allowed_file(model_file.filename):
        filename = secure_filename(model_file.filename)
        model_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        folder = filename

    path = UPLOAD_FOLDER+filename
    print(path)
    with open(path, 'r') as f:
        xmlString = f.read()
             
        jsonString = json.dumps(xmltodict.parse(xmlString))
        actualJson = json.loads(jsonString)

        listsensors = actualJson['main']['sensors']['sensor']
        print(listsensors)

        finallist = []
        if type(listsensors) is not list:
            finallist.append(listsensors)
        else:
            finallist = listsensors

        for i in finallist:
            query = "insert into sensor (type,name,maker,datatype,format,streamrate,sensorSupport) values ('"+i['sensorType']+"','"+i['sensorName']+"','"+i['sensorMake']+"','"+i['sensorDataType']+"','"+i['format']+"','"+i['streamRate']+"','"+i['sensorSupport']+"')"
            print(query)
            r=requests.post(url=URLd,data=query)

        listservices = actualJson['main']['services']['service']
        print(listservices) 

        finallist = []
        if type(listservices) is not list:
            finallist.append(listservices)
        else:
            finallist = listservices

        for i in finallist:
            if "dependencies" in i.keys():
                
                query = "insert into services (service_name,type,mininstance,highmark,lowmark,minresponsetime,maxinstance) values ('"+i['serviceName']+"','"+i['type']+"',"+str(i['minInstances'])+","+str(i['highMark'])+","+str(i['lowMark'])+",'"+i['minResponseTime']+"',"+str(i['maxInstances'])+")"
                print(query)
                r=requests.post(url=URLd,data=query)
                query = "select service_id from services where service_name='"+i['serviceName']+"'"
                r=requests.post(url=URLd,data=query)
                data = r.json()
                service_id = data[0][0]

                if "service-dependency" in i['dependencies'].keys():
                    service_name = i['dependencies']['service-dependency']['service-name']

                    final_service_name = []
                    if type(service_name) is not list:
                        final_service_name.append(service_name)
                    else:
                        final_service_name = service_name

                    for i_name in final_service_name:
                        query = "select service_id from services where service_name='"+i_name+"'"
                        r=requests.post(url=URLd,data=query)
                        data = r.json()
                        dep_service_id = data[0][0]
                        query = "insert into services_dep (service_id,dep_service_id) values ("+str(service_id)+","+str(dep_service_id)+")"
                        r=requests.post(url=URLd,data=query)
            else:
                query = "insert into services (service_name,type,mininstance,highmark,lowmark,minresponsetime,maxinstance) values ('"+i['serviceName']+"','"+i['type']+"',"+str(i['minInstances'])+","+str(i['highMark'])+","+str(i['lowMark'])+",'"+i['minResponseTime']+"',"+str(i['maxInstances'])+")"
                print(query)
                r=requests.post(url=URLd,data=query)  
    return render_template('platform.html')    


@app.route('/logout')
def logout():
    session.pop('uid', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=9001,debug=False,threaded=True)

