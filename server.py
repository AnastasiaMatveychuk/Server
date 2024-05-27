import socket
import os
import datetime
import json

# Конфигурация сервера по умолчанию
CONFIG = {
    'PORT': 80,
    'WORKING_DIR': './www',
    'MAX_REQUEST_SIZE': 8192
}


def load_config():
    global CONFIG
    config_path = 'server_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            user_config = json.load(f)
            CONFIG.update(user_config)


def get_content_type(file_path):
    if file_path.endswith(".html"):
        return "text/html"
    elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        return "image/jpeg"
    elif file_path.endswith(".png"):
        return "image/png"
    elif file_path.endswith(".css"):
        return "text/css"
    elif file_path.endswith(".js"):
        return "application/javascript"
    else:
        return "application/octet-stream"


def handle_request(request):
    lines = request.split('\r\n')
    if not lines:
        return None, None
    request_line = lines[0]
    parts = request_line.split()
    if len(parts) != 3:
        return None, None
    method, path, version = parts
    if path == '/':
        path = '/index.html'
    return method, path


def create_response(status_code, content, content_type):
    status_messages = {200: 'OK', 404: 'Not Found'}
    response_line = f"HTTP/1.1 {status_code} {status_messages[status_code]}"
    headers = [
        response_line,
        f"Date: {datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        f"Server: SimplePythonServer",
        f"Content-Length: {len(content)}",
        f"Content-Type: {content_type}",
        "Connection: close",
        "",
        ""
    ]
    response_headers = "\r\n".join(headers)
    return response_headers.encode() + content


def run_server():
    load_config()
    sock = socket.socket()
    try:
        sock.bind(('', CONFIG['PORT']))
        print(f"Using port {CONFIG['PORT']}")
    except OSError:
        CONFIG['PORT'] = 8080
        sock.bind(('', CONFIG['PORT']))
        print("Using port 8080")

    sock.listen(5)

    while True:
        conn, addr = sock.accept()
        print("Connected", addr)
        data = conn.recv(CONFIG['MAX_REQUEST_SIZE'])
        request = data.decode()

        method, path = handle_request(request)
        if method is None or path is None:
            conn.close()
            continue

        file_path = CONFIG['WORKING_DIR'] + path
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            response = create_response(200, content, get_content_type(file_path))
        else:
            response = create_response(404, b'404 Not Found', 'text/html')

        conn.send(response)
        conn.close()


if __name__ == "__main__":
    run_server()
#localhost:8080
#curl http://localhost:8080
#curl http://localhost:8080/about.html
#curl http://localhost:8080/nonexistent.html