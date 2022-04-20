from frontend.app import  app
from flask import request
from backend_files import eliza
import subprocess


@app.route('/', methods = ['POST', 'GET'])
def home():
    if request.method == 'POST':
        usrInput = request.form['userInput']
        outText=""
        el_start = subprocess.run([eliza.main(), "-p", "doctor.txt"], stdin=usrInput, stdout=outText)

    return el_start

if __name__ == '__main__':
    app.run()
    
