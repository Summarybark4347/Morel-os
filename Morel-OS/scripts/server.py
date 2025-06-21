import socket
import threading

# Server constants
HOST = '127.0.0.1'  # Localhost
PORT = 12345
MAX_CLIENTS = 10
BUFFER_SIZE = 1024

# Global variables for managing clients
clients = []  # List of client socket objects
client_lock = threading.Lock()
client_data = {}  # Stores {'socket': {'address': address, 'username': username}}
client_data_lock = threading.Lock()


def broadcast(message_bytes, sender_socket, sender_username):
    """
    Broadcasts a message to all clients.
    If sender_username is "SERVER", message is sent as is.
    Otherwise, message is formatted with sender's username.
    Removes clients that cause an error during send.
    """
    if sender_username == "SERVER":
        full_message_to_send = message_bytes
    else:
        try:
            decoded_message = message_bytes.decode('utf-8')
            full_message_to_send = f"[{sender_username}]: {decoded_message}".encode('utf-8')
        except UnicodeDecodeError:
            # Handle cases where message might not be valid utf-8 (e.g. binary data)
            # For a simple chat, this is less likely, but good to be aware.
            # Alternatively, could send as raw bytes if that's intended.
            print(f"[WARNING] Could not decode message from {sender_username}. Broadcasting as is.")
            full_message_to_send = message_bytes # Or some error message

    with client_lock: # Lock for iterating 'clients' list
        disconnected_clients = []
        for client_socket_obj in clients:
            # Do not send the message back to the original sender if it's a user message
            if sender_username != "SERVER" and client_socket_obj is sender_socket:
                continue
            
            try:
                client_socket_obj.sendall(full_message_to_send)
            except Exception as e:
                # Using client_socket_obj directly to fetch address if needed
                with client_data_lock: # Lock for accessing client_data
                    cd = client_data.get(client_socket_obj)
                    client_display_name = cd['username'] if cd else str(client_socket_obj.getpeername() if client_socket_obj.fileno() != -1 else "Unknown Client")
                
                print(f"[ERROR] Failed to send to {client_display_name}: {e}. Removing client.")
                disconnected_clients.append(client_socket_obj)
                try:
                    client_socket_obj.close()
                except Exception:
                    pass 
        
        if disconnected_clients:
            for dc in disconnected_clients:
                if dc in clients: 
                    clients.remove(dc)
                with client_data_lock: # Also remove from client_data
                    if dc in client_data:
                        del client_data[dc]


def handle_client(client_socket, client_address):
    """
    Handles an individual client connection, including username registration.
    """
    username = None
    try:
        # First message from client should be the username
        username_bytes = client_socket.recv(BUFFER_SIZE)
        if not username_bytes:
            print(f"[DISCONNECTED] {client_address} disconnected before sending username.")
            return # Exit thread if no username sent

        username = username_bytes.decode('utf-8').strip()
        if not username:
            username = f"Guest_{client_address[1]}" # Assign a default username
            # Optionally, inform client of their default username
            # client_socket.send(f"[SERVER] You are connected as {username}".encode('utf-8'))

        with client_data_lock:
            client_data[client_socket] = {'address': client_address, 'username': username}
        
        print(f"[NEW CONNECTION] {username} ({client_address}) connected.")
        
        join_msg = f"[SERVER] {username} has joined the chat."
        broadcast(join_msg.encode('utf-8'), client_socket, "SERVER") # sender_socket is ignored for SERVER msgs

        while True:
            message_bytes = client_socket.recv(BUFFER_SIZE)
            if not message_bytes: 
                break # Graceful disconnect by client
            
            broadcast(message_bytes, client_socket, username)

    except ConnectionResetError:
        print(f"[ERROR] Connection reset by {username if username else client_address}.")
    except socket.timeout:
        print(f"[TIMEOUT] {username if username else client_address} timed out.")
    except Exception as e:
        print(f"[ERROR] An error occurred with {username if username else client_address}: {e}")
    finally:
        # Retrieve username for disconnect message, default to address if not found
        with client_data_lock:
            stored_user_info = client_data.get(client_socket)
            final_username = stored_user_info['username'] if stored_user_info else str(client_address)
            if client_socket in client_data:
                del client_data[client_socket]

        with client_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        
        if username: # Only broadcast if username was successfully set (i.e., connection was somewhat established)
            disconnect_notification_msg = f"[SERVER] {final_username} has left the chat."
            print(disconnect_notification_msg) 
            broadcast(disconnect_notification_msg.encode('utf-8'), client_socket, "SERVER")
        else: # If disconnect happened before username was set
            print(f"[DISCONNECTED] {client_address} disconnected before username was processed.")

        print(f"[STATUS] Client {final_username} ({client_address}) processing finished. Active clients: {len(clients)}")
        try:
            client_socket.close()
        except Exception as e:
            print(f"[ERROR] Error closing socket for {client_address}: {e}")

def start_server():
    """
    Starts the chat server.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow address reuse
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
    except socket.error as e:
        print(f"[ERROR] Failed to bind server socket: {e}")
        return

    server_socket.listen(MAX_CLIENTS)
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    try:
        while True:
            try:
                client_socket, client_address = server_socket.accept()
            except socket.error as e:
                print(f"[ERROR] Failed to accept connection: {e}")
                continue 

            # Client is added to 'clients' list after username is received in handle_client
            # This is a change from previous version.
            # However, for thread creation, we need the socket now.
            # Let's add to clients list here, and handle_client will add to client_data.
            with client_lock:
                 clients.append(client_socket)
            
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.daemon = True 
            thread.start()
            
            # Active connections count might be more accurately derived from len(clients) or len(client_data)
            # print(f"[ACTIVE CONNECTIONS] {len(clients)}") # Or use threading.active_count() -1

    except KeyboardInterrupt:
        print("[STOPPING] Server is shutting down...")
    finally:
        print("[CLEANUP] Closing all client sockets and clearing data...")
        with client_lock:
            for client_socket_obj in clients:
                try:
                    client_socket_obj.close()
                except Exception as e:
                    print(f"[ERROR] Error closing a client socket: {e}")
            clients.clear()
        with client_data_lock:
            client_data.clear()
            
        server_socket.close()
        print("[STOPPED] Server has stopped.")

if __name__ == "__main__":
    start_server()
