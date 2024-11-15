import socket
import threading
import json
from datetime import datetime
import argparse
import logging
import sys
import random
import os

# ANSI Colors and Styles
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'reset': '\033[0m',
    'bold': '\033[1m',
    'dim': '\033[2m'
}

# Available Commands
COMMANDS = {
    '!help': 'Show available commands',
    '!active': 'Show active users in the chat',
    '!clear': 'Clear the screen',
    '!whoami': 'Show your current username',
    '!time': 'Show current server time',
    '!room': 'Show current room name'
}

# Box drawing characters
BOX_CHARS = {
    'top_left': '╭',
    'top_right': '╮',
    'bottom_left': '╰',
    'bottom_right': '╯',
    'horizontal': '─',
    'vertical': '│'
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_box(text, width=60):
    lines = []
    lines.append(f"{COLORS['dim']}{BOX_CHARS['top_left']}{BOX_CHARS['horizontal'] * (width-2)}{BOX_CHARS['top_right']}{COLORS['reset']}")
    lines.append(f"{COLORS['dim']}{BOX_CHARS['vertical']}{COLORS['reset']} {text}{' ' * (width-len(text)-4)}{COLORS['dim']}{BOX_CHARS['vertical']}{COLORS['reset']}")
    lines.append(f"{COLORS['dim']}{BOX_CHARS['bottom_left']}{BOX_CHARS['horizontal'] * (width-2)}{BOX_CHARS['bottom_right']}{COLORS['reset']}")
    return '\n'.join(lines)

class ChatServer:
    def __init__(self, host='0.0.0.0', port=55555, room_name='main'):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = []
        self.nicknames = []
        self.room_name = room_name
        self.user_colors = {}
        self.available_colors = list(COLORS.keys())[:-3]  # Exclude reset, bold, and dim
        
        logging.basicConfig(
            level=logging.INFO,
            format=f'{COLORS["cyan"]}%(asctime)s - %(levelname)s - %(message)s{COLORS["reset"]}'
        )
        self.logger = logging.getLogger(__name__)

    def get_user_color(self, nickname):
        if nickname not in self.user_colors:
            if self.available_colors:
                color = random.choice(self.available_colors)
                self.available_colors.remove(color)
            else:
                color = list(COLORS.keys())[len(self.user_colors) % (len(COLORS) - 3)]
            self.user_colors[nickname] = color
        return self.user_colors[nickname]
        
    def format_username(self, nickname):
        """Format username in the style nickname@chatroom#"""
        color = self.get_user_color(nickname)
        return f"{COLORS[color]}{nickname}@{self.room_name}#{COLORS['reset']}"

    def get_active_users(self):
        """Get list of active users"""
        return [f"{COLORS[self.get_user_color(nick)]}{nick}{COLORS['reset']}" for nick in self.nicknames]
        
    def broadcast(self, message, is_system_message=False):
        """Send message to all connected clients"""
        message_dict = {
            'type': 'message',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'is_system': is_system_message
        }
        for client in self.clients:
            try:
                client.send(json.dumps(message_dict).encode('utf-8'))
            except:
                self.handle_disconnect(client)

    def handle_disconnect(self, client):
        """Handle client disconnection"""
        try:
            index = self.clients.index(client)
            self.clients.remove(client)
            client.close()
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            # Modified to show just the nickname with its color
            self.broadcast(f"{COLORS['yellow']}root: {COLORS[self.get_user_color(nickname)]}{nickname}{COLORS['reset']} left the chat!", True)
            self.logger.info(f'Client {nickname} disconnected')
        except:
            pass

    def get_active_users(self):
        """Get list of active users"""
        # Return just the nickname
        return [f"{COLORS[self.get_user_color(nick)]}{nick}{COLORS['reset']}" for nick in self.nicknames]

    def handle_command(self, command, client):
        """Handle chat commands"""
        try:
            nickname = self.nicknames[self.clients.index(client)]
            formatted_username = self.format_username(nickname)
            
            if command == '!help':
                help_text = f"{COLORS['yellow']}Available commands:{COLORS['reset']}\n"
                for cmd, desc in COMMANDS.items():
                    help_text += f"{COLORS['cyan']}{cmd}{COLORS['reset']}: {desc}\n"
                client.send(json.dumps({
                    'type': 'command_response',
                    'content': help_text,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }).encode('utf-8'))
                
            elif command == '!active':
                active_users = self.get_active_users()
                response = f"{COLORS['yellow']}Active users ({len(active_users)}):{COLORS['reset']}\n"
                for user in active_users:
                    response += f"• {user}\n"
                client.send(json.dumps({
                    'type': 'command_response',
                    'content': response,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }).encode('utf-8'))
                
            elif command == '!whoami':
                response = f"You are {formatted_username}"
                client.send(json.dumps({
                    'type': 'command_response',
                    'content': response,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }).encode('utf-8'))
                
            elif command == '!time':
                time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                response = f"Server time: {time_now}"
                client.send(json.dumps({
                    'type': 'command_response',
                    'content': response,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }).encode('utf-8'))
                
            elif command == '!room':
                response = f"Current room: {self.room_name}"
                client.send(json.dumps({
                    'type': 'command_response',
                    'content': response,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }).encode('utf-8'))
                
            else:
                client.send(json.dumps({
                    'type': 'command_response',
                    'content': f"{COLORS['red']}Unknown command. Type !help for available commands.{COLORS['reset']}",
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }).encode('utf-8'))
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")

    def handle_client(self, client, address):
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    break
                
                try:
                    msg_dict = json.loads(message.decode('utf-8'))
                    if msg_dict['type'] == 'message':
                        content = msg_dict['content']
                        if content.startswith('!'):
                            # Handle as command
                            self.handle_command(content.strip(), client)
                        else:
                            # Handle as regular message
                            nickname = self.nicknames[self.clients.index(client)]
                            formatted_username = self.format_username(nickname)
                            self.broadcast(f"{formatted_username} {content}")
                            self.logger.info(f"Message from {formatted_username}: {content}")
                except json.JSONDecodeError:
                    continue
                    
            except:
                self.handle_disconnect(client)
                break

    def start(self):
        """Start the chat server"""
        print(create_box(f"Server running on port {self.server.getsockname()[1]}"))
        while True:
            try:
                client, address = self.server.accept()
                self.logger.info(f"New connection from {address}")

                client.send(json.dumps({'type': 'nickname_request'}).encode('utf-8'))
                nickname = json.loads(client.recv(1024).decode('utf-8'))['content']
                self.nicknames.append(nickname)
                self.clients.append(client)

                #  shows the nickname 
                self.logger.info(f'Client {nickname} connected from {address}')
                self.broadcast(f"{COLORS['yellow']}root: {COLORS[self.get_user_color(nickname)]}{nickname}{COLORS['reset']} joined the chat!", True)

                client.send(json.dumps({
                    'type': 'room_info',
                    'room_name': self.room_name
                }).encode('utf-8'))

                thread = threading.Thread(target=self.handle_client, args=(client, address))
                thread.daemon = True
                thread.start()

            except Exception as e:
                self.logger.error(f"Error accepting connection: {e}")

class ChatClient:
    def __init__(self, host, port=55555):
        clear_screen()
        print(create_box("Welcome to Backdoor"))
        self.nickname = input(f"{COLORS['cyan']}Choose an alias: {COLORS['reset']}")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.room_name = None
        
        try:
            self.client.connect((host, port))
            print(create_box(f"Connected to {host}:{port}"))
        except ConnectionRefusedError:
            print(f"{COLORS['red']}Could not connect to the server. Please check the address and port.{COLORS['reset']}")
            sys.exit(1)
        except socket.gaierror:
            print(f"{COLORS['red']}Invalid server address. Please check the address.{COLORS['reset']}")
            sys.exit(1)
            
        self.running = True

    def format_message(self, msg_dict):
        """Format the message for display"""
        timestamp = f"{COLORS['dim']}[{msg_dict['timestamp']}]{COLORS['reset']}"
        content = msg_dict['content']
        
        if msg_dict.get('is_system', False):
            return f"\r{timestamp} {content}"
        return f"\r{timestamp} {content}"

    def receive(self):
        while self.running:
            try:
                message = self.client.recv(1024)
                if not message:
                    print(f"\n{COLORS['red']}Disconnected from server{COLORS['reset']}")
                    self.running = False
                    break

                msg_dict = json.loads(message.decode('utf-8'))
                
                if msg_dict['type'] == 'nickname_request':
                    self.client.send(json.dumps({
                        'type': 'nickname',
                        'content': self.nickname
                    }).encode('utf-8'))
                elif msg_dict['type'] == 'room_info':
                    self.room_name = msg_dict['room_name']
                    clear_screen()
                    print(create_box(f"Connected as {self.nickname} on Backdoor"))
                    print(create_box("Type !help for available commands"))
                    print(f"{COLORS['dim']}" + "─" * 60 + f"{COLORS['reset']}\n")
                elif msg_dict['type'] == 'command_response':
                    print(f"\r{COLORS['dim']}[{msg_dict['timestamp']}]{COLORS['reset']} {msg_dict['content']}")
                    print(f"{COLORS['cyan']}You:{COLORS['reset']} ", end='', flush=True)
                elif msg_dict['type'] == 'clear_screen':
                    clear_screen()
                    print(create_box(f"Connected as {self.nickname} on Backdoor"))
                    print(f"{COLORS['dim']}" + "─" * 60 + f"{COLORS['reset']}\n")
                elif msg_dict['type'] == 'message':
                    formatted_message = self.format_message(msg_dict)
                    print(formatted_message)
                    print(f"{COLORS['cyan']}You:{COLORS['reset']} ", end='', flush=True)
                    
            except json.JSONDecodeError:
                continue
            except:
                print(f"\n{COLORS['red']}Lost connection to server{COLORS['reset']}")
                self.running = False
                break

    def write(self):
        while self.running:
            try:
                message = input(f"{COLORS['cyan']}You:{COLORS['reset']} ")
                if message.lower() == 'quit':
                    self.running = False
                    self.client.close()
                    break
                    
                if message:
                    msg_dict = {
                        'type': 'message',
                        'content': message,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
                    self.client.send(json.dumps(msg_dict).encode('utf-8'))
            except:
                break

    def start(self):
        receive_thread = threading.Thread(target=self.receive)
        write_thread = threading.Thread(target=self.write)
        
        receive_thread.daemon = True
        write_thread.daemon = True
        
        receive_thread.start()
        write_thread.start()
        
        try:
            receive_thread.join()
            write_thread.join()
        except KeyboardInterrupt:
            print(f"\n{COLORS['yellow']}Disconnecting from server...{COLORS['reset']}")
            self.running = False
            self.client.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enhanced CLI Chat Application')
    parser.add_argument('--server', action='store_true', help='Run as server')
    parser.add_argument('--host', default='127.0.0.1', help='Host address to connect to or bind on')
    parser.add_argument('--port', type=int, default=55555, help='Port number')
    parser.add_argument('--room', default='backdoor', help='Chat room name')
    
    args = parser.parse_args()
    
    try:
        if args.server:
            server = ChatServer(host=args.host, port=args.port, room_name=args.room)
            server.start()
        else:
            client = ChatClient(host=args.host, port=args.port)
            client.start()
    except KeyboardInterrupt:
        print(f"\n{COLORS['yellow']}Shutting down...{COLORS['reset']}")
        sys.exit(0)