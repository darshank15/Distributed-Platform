from flask import Flask,request, render_template
from flaskext.mysql import MySQL
import json
import requests
import socket
import sys

app = Flask(__name__)

app.config.from_pyfile('dbconfig.py')

mysql = MySQL()
mysql.init_app(app)

ip=sys.argv[3]

port="9005"

serviceName = "dbService"
sdURL = sys.argv[1]

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


@app.route('/health')
def health():
	return "OK"

@app.route('/db_interaction',methods=['GET','POST'])
def db_interaction():
    query = request.data
    db = mysql.connect()
    cursor = db.cursor()
    query = query.decode("utf-8") 
    print(query)
    cursor.execute(query)
    db.commit()

    data = []
    for i in cursor.fetchall():
    	print(i)
    	data.append(i)

    dt = json.dumps(data)
    print("@@@@@@@@@@@@@@@@@@")
    print(dt)
    return dt

register(ip,port,serviceName,sdURL)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=9005,debug=False,threaded=True)