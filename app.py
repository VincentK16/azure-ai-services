from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import azure.cognitiveservices.speech as speechsdk
import time

app = Flask(__name__)
socketio = SocketIO(app)

speech_key, service_region = "<replace with your speech key>", "<replace with your speech region>"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language="en-SG")
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

def stop_cb(evt):
    print('CLOSING on {}'.format(evt))
    speech_recognizer.stop_continuous_recognition()
    speech_recognizer.session_started.disconnect_all()
    speech_recognizer.recognized.disconnect_all()
    speech_recognizer.session_stopped.disconnect_all()

speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
speech_recognizer.session_stopped.connect(lambda evt: print('\nSESSION STOPPED {}'.format(evt)))

# Emit the recognized text to the client
speech_recognizer.recognized.connect(lambda evt: socketio.emit('recognized', {'text': evt.result.text}))

speech_recognizer.canceled.connect(lambda evt: print('CANCELED: {} ({})'.format(evt.cancellation_details.reason, evt.cancellation_details.error_details)))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_recognition')
def handle_start_recognition():
    print('Say a few words\n\n')
    socketio.emit('message', {'text': 'Say a few words\n\n'})
    speech_recognizer.start_continuous_recognition()

    while True:
        time.sleep(.5)

if __name__ == '__main__':
    socketio.run(app,port=5001)
