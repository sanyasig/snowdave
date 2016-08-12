from bottle import static_file
from bottle import get, post, request, route, run
from voicecontroller import VoiceController
from threading import Thread

VC = None

@route('/')
def index():
    return static_file("index.html", root='templates')

@post('/login') # or @route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login(username, password):
        return "<p>Your login information was correct.</p>"
    else:
        return "<p>Login failed.</p>"

@route('/object/<id:int>')
def callback(id):
    assert isinstance(id, int)

@route('/show/<name:re:[a-z]+>')
def callback(name):
    assert name.isalpha()

def start_voice_controller():
    while startVoice:
        VC = VoiceController()
        try:
            VC.main()
        except Exception: VC = None

if __name__ == "__main__":
    run(host='0.0.0.0', port=8000, reloader=True)
