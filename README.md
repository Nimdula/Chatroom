# Chat Application

This project is a real-time chat application built using Flask and Socket.IO. It allows users to join chat rooms, send messages, and interact in a seamless, responsive interface.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Project Structure](#project-structure)
- [How to Use](#how-to-use)
- [Function Explanations](#function-explanations)
- [Credits](#credits)

## Features
- Create or join chat rooms with unique codes.
- Real-time messaging using WebSockets.
- Auto-scroll in the chat room for new messages.
- User-friendly UI with responsive design.

## Technologies Used
- **Backend:** Python
- **Frontend:** HTML, CSS, JavaScript
- **Frameworks:** Flask
- **Libraries:** Socket.IO

## Setup and Installation

Clone the repository:
```bash
git clone https://github.com/Nimdula/Chatroom.git
cd Chatroom
```

Run the application:
```bash
python main.py
```

Open your browser and navigate to `http://127.0.0.1:5000`.

## Project Structure
```
Chatroom/
├── static/
│   ├── css/
│       ├── style.css
│       └── gradient.jpg
│   
├── templates/
│   ├── base.html
│   ├── home.html
│   └── room.html
├── main.py
└── README.md
```

## How to Use
1. Open the homepage.
2. Enter your name and a room code to join an existing room, or click "Create a Room" to generate a new room code.
3. Start chatting in real time!

## Function Explanations

### `generate_unique_code(length)`
Generates a unique room code consisting of uppercase letters. It ensures no duplicate codes are created by checking against the rooms dictionary.
```python
def generate_unique_code(length):
    while True:
        code = ''.join(random.choice(ascii_uppercase) for _ in range(length))
        if code not in rooms:
            return code
```

### `home()`
Handles requests to the homepage. Manages user input for joining or creating chat rooms and validates the input before redirecting users to the appropriate room.
```python
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
```

### `message(data)`
Handles incoming messages from users. Broadcasts the message to all users in the room and logs it in the room's message history.
```python
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
```

### `connect(auth)`
Manages new user connections to a room. Increments the member count for the room and notifies all users in the room of the new participant.
```python
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
```

### `disconnect()`
Handles user disconnections. Decrements the room's member count and removes the room if it becomes empty.
```python
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
```

## Credits
This project was developed by **Nimdula Perera**.
