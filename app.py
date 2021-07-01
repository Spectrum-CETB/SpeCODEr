'''
    Import Modules
'''

from flask import Flask, render_template, request,jsonify
import subprocess
import datetime
import os
import requests
from bs4 import BeautifulSoup

'''
    Initiate the app
'''
app = Flask(__name__)


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
Processing Requests
'''
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run/',methods = ['POST'])
def run():
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
   app.run(debug = True)