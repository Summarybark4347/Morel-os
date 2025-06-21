import socket
import threading
import sys

# Server constants (should match server.py)
HOST = '127.0.0.1'
PORT = 12345
BUFFER_SIZE = 1024

# Event to signal threads to terminate
shutdown_event = threading.Event()
# Lock for ensuring print statements and input prompt don't overlap badly
stdout_lock = threading.Lock()


def receive_messages(client_socket, username_for_prompt): # username_for_prompt passed for re-printing prompt
    """
    Listens for messages from the server and prints them.
    """
    while not shutdown_event.is_set():
        try:
            message_bytes = client_socket.recv(BUFFER_SIZE)
            if not message_bytes:
                with stdout_lock:
                    sys.stdout.write('\r' + ' ' * (len(username_for_prompt) + 2 + 20) + '\r') # Clear line
                    print("[INFO] Server closed the connection.")
                break 
            
            decoded_message = message_bytes.decode('utf-8')
            
            with stdout_lock:
                # Erase the current input line (prompt + anything typed)
                # The +20 is a buffer for potentially typed characters
                sys.stdout.write('\r' + ' ' * (len(username_for_prompt) + 2 + 20) + '\r')
                print(decoded_message) # Print the received message
                sys.stdout.write(f"{username_for_prompt}> ") # Reprint the prompt
                sys.stdout.flush()

        except (ConnectionAbortedError, ConnectionResetError, OSError) as e:
            if not shutdown_event.is_set(): 
                with stdout_lock:
                    sys.stdout.write('\r' + ' ' * (len(username_for_prompt) + 2 + 20) + '\r')
                    print(f"[INFO] Disconnected from server or connection error: {e}")
            break
        except Exception as e:
            if not shutdown_event.is_set():
                print(f"[ERROR] Error receiving message: {e}")
            break
    
    if not shutdown_event.is_set(): # If loop broke due to error/server disconnect
        shutdown_event.set() # Signal main thread to also shut down
    # print("[DEBUG] Receive thread terminating.")
    # Add a final newline if loop broke, to not overwrite the prompt line
    if not shutdown_event.is_set():
        with stdout_lock: # Ensure this print is clean too
             sys.stdout.write('\n')
             sys.stdout.flush()
        shutdown_event.set()


def start_client():
    """
    Starts the chat client.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
        print(f"[INFO] Connected to the server at {HOST}:{PORT}")
    except ConnectionRefusedError:
        print(f"[ERROR] Connection refused. Ensure the server is running at {HOST}:{PORT}.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to connect to server: {e}")
        sys.exit(1)

    username = ""
    while not username:
        username = input("Enter your username: ").strip()
        if not username:
            print("Username cannot be empty.")
    
    try:
        client_socket.send(username.encode('utf-8'))
    except socket.error as e:
        print(f"[ERROR] Failed to send username: {e}. Disconnecting.")
        client_socket.close()
        sys.exit(1)

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, username))
    receive_thread.daemon = True 
    receive_thread.start()

    try:
        while not shutdown_event.is_set():
            # The prompt is now handled by receive_messages for incoming messages
            # For the initial prompt and after sending a message:
            with stdout_lock:
                sys.stdout.write(f"{username}> ")
                sys.stdout.flush()
            
            message_to_send = input() 
            
            if shutdown_event.is_set(): 
                break
            
            if message_to_send:
                if message_to_send.lower() == '/quit':
                    with stdout_lock: # Lock before printing and setting event
                        print("[INFO] Quitting...")
                        shutdown_event.set() 
                    break
                try:
                    client_socket.send(message_to_send.encode('utf-8'))
                except socket.error as e:
                    with stdout_lock: # Lock before printing and setting event
                        print(f"[ERROR] Failed to send message: {e}. Disconnecting.")
                        shutdown_event.set()
                    break
            
            if not receive_thread.is_alive() and not shutdown_event.is_set():
                with stdout_lock:
                    print("[INFO] Server connection lost. Exiting.")
                    shutdown_event.set() 
                break
                
    except KeyboardInterrupt:
        with stdout_lock:
            # Erase current input line before printing Ctrl+C message
            sys.stdout.write('\r' + ' ' * (len(username) + 2 + 20) + '\r') 
            print("\n[INFO] Ctrl+C detected. Disconnecting...")
            shutdown_event.set() 
    finally:
        # Ensure a final print statement to move to a new line after input prompt potentially cut off
        with stdout_lock:
            sys.stdout.write('\r' + ' ' * (len(username) + 2 + 50) + '\r') # Clear line generously
            print("[INFO] Shutting down client...")
        shutdown_event.set() 
        
        if receive_thread.is_alive():
             receive_thread.join(timeout=1.0) 

        try:
            client_socket.shutdown(socket.SHUT_RDWR) 
        except (socket.error, OSError):
            pass 
        finally:
            client_socket.close()
            with stdout_lock: # Ensure this final print is also clean
                print("[INFO] Connection closed.")

if __name__ == "__main__":
    start_client()
