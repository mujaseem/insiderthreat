# from app import create_app

# app = create_app()

# if __name__ == "__main__":
#     app.run(debug=True)

import eventlet
eventlet.monkey_patch()

from app import create_app
from flask_socketio import SocketIO

app = create_app()
socketio = SocketIO(app)

if __name__ == "__main__":
    socketio.run(app)