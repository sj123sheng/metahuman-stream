from flask import Flask, Response
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # 或按需设置 CORS

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            time.sleep(1)
            yield f'data: The server time is: {time.ctime()} \n\n'
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
