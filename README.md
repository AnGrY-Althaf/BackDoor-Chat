# BackDoor CLI Chat Server

A secure command-line interface chat server with authentication, private messaging, file transfers, and comprehensive logging.

![BackDoor Chat Demo](demo.gif)

## Features

### Core Features
- 🔐 Role-based authentication system (admin/user)
- 💬 Real-time messaging
- 📝 Private messaging system
- 📁 File transfer support (up to 5MB)
- 📊 Comprehensive logging system
- 🛡️ Advanced admin controls

### Security Features
- User authentication with access keys
- IP banning system
- User muting capability
- Connection attempt logging
- Maximum login attempts (3)

### Admin Commands
- `!kick <user>` - Kick a user from the chat
- `!ban <user>` - Ban a user's IP address
- `!mute <user>` - Mute a user
- `!unmute <user>` - Unmute a user
- `!logs` - View recent server logs

### User Commands
- `!help` - Show available commands
- `!active` - Show active users
- `!clear` - Clear screen
- `!whoami` - Show your username and role
- `!time` - Show server time
- `!room` - Show current room name
- `!pm <user> <message>` - Send private message
- `!sendfile <user> <filepath>` - Send file to user
- `!receivefile` - Accept pending file transfer
- `!quit` - Exit chat

## Requirements

- Python 3.6+
- No external dependencies required (uses standard library)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/backdoor-chat.git
cd backdoor-chat
```

2. Make sure you have Python 3.6 or higher installed:
```bash
python --version
```

## Usage

### Starting the Server

```bash
# Basic server start (default port: 55555)
python chat.py --server

# Custom port and room name
python chat.py --port 5000 --room hackroom

# Bind to specific IP
python chat.py --host 0.0.0.0 --port 5000
```

### Connecting to the Server

Users can connect using standard terminal tools:
```bash
nc localhost 55555
# or
telnet localhost 55555
```

### Authentication

Default access keys:
- Admin: `backdoor123`
- User: `user123`

### File Transfer

The server supports file transfers up to 5MB:
1. Sender: `!sendfile username filepath`
2. Receiver: `!receivefile`

Files are automatically renamed with timestamps to prevent conflicts.

## Logging System

The server maintains two types of logs in the `logs` directory:
- `chat_YYYYMMDD.log`: Chat messages and commands
- `events_YYYYMMDD.log`: Server events and actions

Logs older than 7 days are automatically cleaned up.

### Log Format
```json
// Chat log entry
{
    "timestamp": "2024-01-16T10:15:30.123",
    "type": "message",
    "nickname": "user",
    "message": "Hello everyone!"
}

// Event log entry
{
    "timestamp": "2024-01-16T10:15:00.000",
    "type": "user_connected",
    "details": {
        "nickname": "user",
        "ip": "192.168.1.100",
        "role": "user"
    }
}
```


## Future Features

- [ ] End-to-end encryption
- [ ] Multiple chat rooms
- [ ] Custom user profiles
- [ ] File encryption
