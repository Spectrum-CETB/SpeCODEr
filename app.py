'''
    Import Modules
'''

from email import message
from flask import Flask, render_template, request,jsonify,redirect,url_for,session
import subprocess
import datetime
import os
import requests
from bs4 import BeautifulSoup
from flask_socketio import SocketIO,emit,join_room,leave_room
from flask_session import Session
from flask_cors import CORS, cross_origin


def generate_txt(url):

    '''
    Function to webscrape Data from given url
    '''

    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    parts = url.split('/')
    num, lev = parts[-2], parts[-1]
    ip_op = []
    for i in soup.find_all("pre"):
        if '<br/>' in str(i):
            data = str(i).split('<br/>')
            data[0] = data[0].split('<pre>')[1]
            data = data[:-1]
            ip_op.append(data)
        else:
            data = str(i).split('\n')
            data = data[1:-1]
            ip_op.append(data)
    input, output = [], []
    for i in range(2):
        if i % 2 == 0:
            input.append("\n".join(ip_op[i]))
        else:
            output.append("\n".join(ip_op[i]))
    input_name, output_name = "input" + num + lev + ".txt", "output" + num + lev + ".txt"
    textfile = open(input_name, "w")
    for element in input:
        textfile.write(element + "\n")
    textfile.close()
    textfile = open(output_name, "w")
    for element in output:
        textfile.write(element + "\n")
    textfile.close()
    return input_name, output_name

  
def createFile(code,ext):

    '''
    Function to Create File
    '''

    fname=datetime.datetime.now().strftime("%m%d%Y%H%M%S")
    fname=fname.replace(" ","_")
    fname=fname.replace(":","_")
    fname=fname+ext
    file1 = open(fname, 'w')
    file1.write(code)
    file1.close()

    return fname


def runFile(l,inp):
    '''
    Run the given file
    '''
    with open(inp, 'rb', 0) as a:
        output = subprocess.run(l,stdin=a,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    os.remove(inp)
    return output.stdout,output.stderr


'''
    Initiate the app
'''
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'Innovate.Accelerate.Elevate.'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)
socketio = SocketIO(app, manage_session=False)


'''
Processing Requests
'''
   
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/ide',methods=['GET','POST'])
def ide():
    if(request.method=='POST'):
        username = request.form['username']
        room = request.form['room']
        #Store the data in the session
        session['username'] = username
        session['room'] = room
        return render_template('ide.html',session=session)
    else:
        if(session.get('username') is not None):
            return render_template('ide.html',session=session)
        else:
            return redirect(url_for('index'))

@socketio.on('join',namespace='/ide')
def join(message):
    room = session.get('room')
    join_room(room)

@socketio.on('text',namespace='/ide')
def text(message):
    room = session.get('room')
    emit('message',{'msg': message['msg']},room=room)

@socketio.on('left', namespace='/ide')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()

@app.route('/compile/',methods = ['POST'])
def compile():
   if request.method == 'POST':
        #Fetch Parameters
        code = request.json['code']
        lang = request.json['lang']
        custom = request.json['custom']
        url = request.json['url']

        #To Display Results
        status = 'Compiled'
        if url!='':
            #Generate Files
            iptxt,optxt=generate_txt(url)
            testcase = iptxt
            file = open(optxt,mode='r')
            expop = file.read()
            file.close()
            os.remove(optxt)
        else:
            testcase = createFile(custom,".txt")

        if lang=="python":
            fname=createFile(code,".py")
            output,err = runFile(['python',fname],testcase)

        elif lang=="javascript":
            fname=createFile(code,".js")
            output,err = runFile(['node',fname],testcase)

        os.remove(fname)
        if url!='':
            if output==expop:
                status = "Passed"
            else:
                status = "Failed"
        
        return jsonify({'out':output,'err':err,'status':status})



if __name__ == '__main__':
   app.run()
