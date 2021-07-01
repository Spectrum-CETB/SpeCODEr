from flask import Flask, render_template, request,jsonify
import subprocess
import datetime
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


def generate_txt(url):
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
        fname=datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        fname=fname.replace(" ","_")
        fname=fname.replace(":","_")
        fname=fname+ext
        file1 = open(fname, 'w')
        file1.write(code)
        file1.close()

        return fname


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run/',methods = ['POST'])
def run():
   if request.method == 'POST':
        code = request.json['code']
        lang = request.json['lang']
        custom = request.json['custom']
        rv=''
        print(custom)
        if(custom !=''):
            testcase = createFile(custom,".txt")
        if lang=="python":
            fname=createFile(code,".py")
            if(custom!=''):
                with open(testcase, 'rb', 0) as a:
                    rv = subprocess.run(['python',fname],stdin=a,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                os.remove(testcase)
            else:
                rv = subprocess.run(['python',fname],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

        elif lang=="javascript":
            fname=createFile(code,".js")
            if(custom!=''):
                with open(testcase, 'rb', 0) as a:
                    rv = subprocess.run(['node',fname],stdin=a,stdout=subprocess.PIPE,text=True)
                os.remove(testcase)
            else:
                rv = subprocess.run(['node',fname],stdout=subprocess.PIPE,text=True)
        
        os.remove(fname)    
        return jsonify({'out':rv.stdout,'err':rv.stderr})

if __name__ == '__main__':
   app.run(debug = True)