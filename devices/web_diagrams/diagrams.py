import json
import random
import time
from datetime import datetime

from flask import Flask, Response, render_template

application = Flask(__name__)
random.seed()  # Initialize the random number generator


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/chart-data')
def chart_data():
    def generate_random_data():
        while True:
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'door1': 0 if random.randint(0, 100) == 0 else 1,
                 'door2': 0 if random.randint(0, 100) == 0 else 1,
                 'door3': 0 if random.randint(0, 100) == 0 else 1,
                 'ir': 0 if random.randint(0, 50) == 0 else 1,
                 'rotator': 0 if random.randint(0, 100) == 0 else 1,
                 'destroyer': 0 if random.randint(0, 100) == 0 else 1,
                 })
            yield f"data:{json_data}\n\n"
            time.sleep(0.02)

    return Response(generate_random_data(), mimetype='text/event-stream')


if __name__ == '__main__':
    application.run(debug=True, threaded=True)
