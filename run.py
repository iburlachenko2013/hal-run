import os, signal
from flask import Flask, jsonify, request, render_template
import shlex
from subprocess import Popen, PIPE
import psutil

root_dir = '/home/pi/hal-run/hal-run-app'
music_dir = root_dir + '/static/music'
effects_dir = root_dir + '/static/effects'



app = Flask(__name__)
app.config['curr_effect'] = "None"

def get_exitcode_stdout_stderr(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)
    p = psutil.Popen(args, stdout=PIPE)
    print('Proc STARTED - ' + p.name())

def clearEffects():
    print('Trying to delete -- ' + app.config["curr_effect"])
    procName = app.config["curr_effect"]
    for proc in psutil.process_iter():
        if proc.name() == procName:
            print(proc)
            proc.kill()
            os.kill(proc.pid, signal.SIGKILL)
    

@app.route('/')
@app.route('/home')
def index():
    clearEffects()
    return render_template("index.html",
                        title = 'Home' )

@app.route('/ef/<effect_name>')
def start_effect(effect_name=None):
    print('-new eff->' + effect_name)
    print('-old eff->' + app.config['curr_effect'])
    print((effect_name != app.config['curr_effect']))
    if (effect_name != app.config['curr_effect']):
        clearEffects()
        app_name = effect_name
        app.config["curr_effect"] = app_name
        cmd = "./static/effects/" + app_name
        get_exitcode_stdout_stderr(cmd);

    return jsonify(status = 'success')

@app.route('/voice-record/')
def voice_record():
    clearEffects()
    app_name = 'micarray_recorder'
    if (app_name != app.config['curr_effect']):
        app.config["curr_effect"] = app_name
        cmd = "./static/music/" + app_name
        get_exitcode_stdout_stderr(cmd);
        cmd = 'sox -r 16000 -c 1 -e signed -b 16 '+music_dir+'/mic_16000_s16le_channel_0.raw '+music_dir+'/channel_0.wav'

    music_files = [f for f in os.listdir(music_dir) if f.endswith('mp3')]
    music_files_number = len(music_files)
    return render_template("index.html",
                        title = 'Home',
                        music_files_number = music_files_number,
                        music_files = music_files)    

@app.route('/play/<filename>')
def song(filename):
    return render_template('play.html',
                        title = filename,
                        music_file = filename)

def sounds_cleaner():
    #while (true) monitoring sounds dir
    pass

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)
