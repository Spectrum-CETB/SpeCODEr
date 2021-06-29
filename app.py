from flask import Flask, render_template, request,jsonify
import subprocess
import datetime
import os

app = Flask(__name__)

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