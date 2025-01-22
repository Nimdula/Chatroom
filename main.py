from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "08312005"  # Secret key for sessions
socketio = SocketIO(app)

rooms = {}  # Dictionary to store active rooms

def generate_unique_code(length): # Generate a unique room code
    while True:
        code = ''.join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            return code


@app.route("/", methods=["POST", "GET"])
def home(): # Handle requests to the home page
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join")
        create = request.form.get("create")

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join is not None and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)

        room = code

        if create is not None:  # Create a new room
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}

        elif code not in rooms:  # Check if room exists
            return render_template("home.html", error="Room does not exist.", code=code, name=name)

        # Store room and user name in session
        session["room"] = room
        session["name"] = name

        return redirect(url_for("room"))

    return render_template("home.html")


@app.route("/room")
def room(): # Render the room page if the user is in a valid room.
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])


@socketio.on("message")
def message(data): # Handle incoming messages and broadcast them to the room.
    room = session.get("room")
    name = session.get("name")

    if room not in rooms or not name:
        return

    content = {
        "name": name,
        "message": data["data"],
        "timestamp": datetime.now().isoformat()
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"\n{name} said: {data['data']}")


@socketio.on("connect")
def connect(auth): # Handle a new connection to the room.
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return

    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"\n{name} has joined {room}\n")


@socketio.on("disconnect")
def disconnect(): # Handle disconnection from the room.
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return

    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"\n{name} has left {room}\n")


if __name__ == '__main__':
    socketio.run(app, debug=True)