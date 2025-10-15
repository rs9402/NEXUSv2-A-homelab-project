import http.server
import socketserver
import os

PORT = 80
BIND_IP = "0.0.0.0"  # bind to all network interfaces

# Serve files from the directory where this script lives
web_dir = os.path.join(os.path.dirname(__file__))
os.chdir(web_dir)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer((BIND_IP, PORT), Handler) as httpd:
    print(f"Serving {web_dir} at http://{BIND_IP}:{PORT}")
    print("Your dashboard should now be accessible on your LAN!")
    httpd.serve_forever()
