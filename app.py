import os
import sys
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from flask import Flask, render_template, Response, request

app = Flask(__name__)

# Config
MODEL_PATH = "model"
SAMPLE_RATE = 16000
BLOCK_SIZE = 512  # ~32ms block size for ultra-low latency

# Globals
audio_queue = queue.Queue()
is_recording = False
model = None

import numpy as np

def load_model():
    global model
    if not os.path.exists(MODEL_PATH):
        print(f"Please download a model from https://alphacephei.com/vosk/models and unpack as '{MODEL_PATH}' in the current folder.")
        sys.exit(1)
    model = Model(MODEL_PATH)
    # Debug: List devices to console once
    # print(sd.query_devices())

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    
    if is_recording:
        audio_queue.put(bytes(indata))

def gen_audio():
    """Generator function that yields SSE events."""
    global is_recording
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    
    # Send ready signal
    yield "data: {\"partial\": \"Listening...\"}\n\n"

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, dtype='int16', channels=1, callback=audio_callback):
            while is_recording:
                try:
                    data = audio_queue.get(timeout=0.05) 
                    if rec.AcceptWaveform(data):
                        result = rec.Result()
                        # Vosk returns multi-line JSON. Must be single line for SSE 'data:' field
                        # OR we need to sanitize it.
                        result_dict = json.loads(result)
                        clean_json = json.dumps(result_dict)
                        print(f"Sending Final: {clean_json}", file=sys.stderr)
                        yield f"data: {clean_json}\n\n"
                    else:
                        partial = rec.PartialResult()
                        partial_dict = json.loads(partial)
                        clean_json = json.dumps(partial_dict)
                        # yield f"data: {partial}\n\n" # OLD BUGGY WAY
                        yield f"data: {clean_json}\n\n"
                        
                except queue.Empty:
                    # Keep-alive
                    pass
    except Exception as e:
        print(f"Stream error: {e}")
        yield f"data: {{\"error\": \"Streaming Error: {str(e)}\"}}\n\n"
    
    yield "data: {\"text\": \"[STOPPED]\"}\n\n"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    global is_recording
    if not is_recording:
        is_recording = True
        # Clear queue
        while not audio_queue.empty():
            audio_queue.get()
    return "started"

@app.route('/stop')
def stop():
    global is_recording
    is_recording = False
    return "stopped"

@app.route('/listen')
def listen():
    if not is_recording:
        return Response("data: {\"text\": \"\"}\n\n", mimetype='text/event-stream')
    return Response(gen_audio(), mimetype='text/event-stream')

if __name__ == '__main__':
    load_model()
    print("Model loaded. Starting Server...")
    # Threaded=True is default in newer Flask, but good to be explicit for dev server responsiveness
    app.run(debug=True, threaded=True, port=5000)
