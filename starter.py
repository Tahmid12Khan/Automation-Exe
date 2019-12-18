command_python = "cd Bengali-Spell-Checker && venv\\Scripts\\activate.bat && python server.py"
command_npm = "cd Bengali-Spell-Checker-Word-Add-in && node server.js"

python = ''
npm = ''

import threading
import os
import subprocess
from subprocess import Popen, PIPE
import sys
from win10toast import ToastNotifier
toaster = ToastNotifier()
icon_path = 'icon.ico'
notification_title = 'Bengali Spell Checker'
import time
def show_notification(message = ''):
    while toaster.notification_active(): 
        time.sleep(1)
    toaster.show_toast(notification_title, message, threaded=True, duration=5, icon_path = icon_path)

show_notification('Starting...')
from infi.systray import SysTrayIcon
def on_quit_callback(systray):
    kill_process_on_port(8088)
    kill_process_on_port(5000)
    print('Quiting Now...')
    show_notification('Server has been shut down')
    systray.shutdown()
    
systray = SysTrayIcon(icon_path, "Bengali Spell Checker", on_quit = on_quit_callback)
systray.start()
def run_npm_thread():
    npm_process = subprocess.Popen(command_npm.split(), stdout=PIPE, stderr=PIPE, shell=True)
    cnt = 0
    print(command_npm)
    for line in iter(npm_process.stdout.readline, ''):  # replace '' with b'' for Python 3
        if len(line) < 6:
            cnt += 1
        else: cnt = 0
        if cnt > 100:
            break
        print('CNT ', cnt)
        try:
            sys.stdout.write(line.decode('utf-8'))
        except:
            sys.stdout.write('Could not Decode')
def run_npm():
    global npm
    npm = threading.Thread(target=run_npm_thread)
    npm.start()
    print('Running NPM command')

def run_python_thread():
#    python_process = subprocess.Popen(command_python.split(), stdout=PIPE, stderr=PIPE, shell=True)
    subprocess.Popen(command_python, shell=True)

def run_python():
    global python
    python = threading.Thread(target=run_python_thread)
    python.start()
    print('Running Python command')

def find_pid_of_process(port):
    process = Popen(["netstat", "-ano", "|", "findstr", ":{0}".format(port)], stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    for line in str(stdout.decode("utf-8")).split("\n"): 
        data = [x for x in line.split() if x != '']
        print(data)
        if (len(data) <= 1):
            continue
        pid = data[-1].strip()
        print('Found ', pid)
        if pid == 0:
            continue
        return pid
    return 0

def wait_till_server_started():
    while True:
        pid = find_pid_of_process(5000)
        if pid == 0:
            time.sleep(5)
            
        else:
            show_notification('Server has started. ')
            break
            

def kill_process_on_port(port):
    process = Popen(["netstat", "-ano", "|", "findstr", ":{0}".format(port)], stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    for line in str(stdout.decode("utf-8")).split("\n"): 
        print(line)
        data = [x for x in line.split() if x != '']
        print(data)
        if (len(data) <= 1):
            continue
        pid = data[-1].strip()
        print('Found ', pid)
        if pid == 0:
            continue
        os.system('taskkill /pid {0} /f'.format(pid))

kill_process_on_port(8088)
kill_process_on_port(5000)
run_npm()
run_python()
wait_till_server_started()
    

#menu_options = (("Say Hello", None, say_hello), )

#subprocess.run(["pip", "install", "nltk"], shell=True, check=True)
#command = 'pip download -r requirements.txt -d libraries'
#subprocess.run(command.split(), shell=True, check=True)

