Chat Application

This project is a real-time chat application built using Flask and Socket.IO. It allows users to join chat rooms, send messages, and interact in a seamless, responsive interface.

Table of Contents

Features

Technologies Used

Setup and Installation

Project Structure

How to Use

Function Explanations

Credits

Features

Create or join chat rooms with unique codes.

Real-time messaging using WebSockets.

Auto-scroll in the chat room for new messages.

User-friendly UI with responsive design.

Technologies Used

Backend: Python, Flask, Flask-SocketIO

Frontend: HTML, CSS, JavaScript

Libraries: socket.io.js

Setup and Installation

Clone the repository:

git clone https://github.com/yourusername/chat-app.git
cd chat-app

Install the required dependencies:

pip install -r requirements.txt

Run the application:

python main.py

Open your browser and navigate to http://127.0.0.1:5000.

Project Structure

chat-app/
├── static/
│   ├── css/
│   │   └── style.css
│   └── gradient.jpg
├── templates/
│   ├── base.html
│   ├── home.html
│   └── room.html
├── main.py
├── requirements.txt
└── README.md

How to Use

Open the homepage.

Enter your name and a room code to join an existing room, or click "Create a Room" to generate a new room code.

Start chatting in real time!

Function Explanations

generate_unique_code(length)

This function generates a unique room code consisting of uppercase letters. It ensures no duplicate codes are created by checking against the rooms dictionary.

def generate_unique_code(length):
    while True:
        code = ''.join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            return code

home()

This function handles requests to the homepage. It manages user input for joining or creating chat rooms and validates the input before redirecting users to the appropriate room.

@app.route("/", methods=["POST", "GET"])
def home():
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

        session["room"] = room
        session["name"] = name

        return redirect(url_for("room"))

    return render_template("home.html")

message(data)

This function handles incoming messages from users. It broadcasts the message to all users in the room and logs it in the room's message history.

@socketio.on("message")
def message(data):
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

connect(auth)

This function manages new user connections to a room. It increments the member count for the room and notifies all users in the room of the new participant.

@socketio.on("connect")
def connect(auth):
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

disconnect()

This function handles user disconnections. It decrements the room's member count and removes the room if it becomes empty.

@socketio.on("disconnect")
def disconnect():
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

Credits

This project was developed by [Your Name]. Contributions and feedback are always welcome!

