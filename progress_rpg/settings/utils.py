import socket


def is_vite_running(host="localhost", port=5173) -> bool:
    """Check if Vite dev server is up."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False
