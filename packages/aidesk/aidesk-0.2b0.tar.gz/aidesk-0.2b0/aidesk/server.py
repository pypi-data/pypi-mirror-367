import datetime
import http.server
import socketserver
import os
import time
from urllib.parse import urlparse, parse_qs
import json
from .api_handlers import home, auth, file_handling, instance_management
from .instance_housekeeper import hook_state_for_cleanup
from .session import get_server_state, set_user_session, set_master_state
from .utils import load_template, get_session_id, validate_session, get_host_info


class AideskHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        # Check authentication status
        session_id = get_session_id(self.headers)
        is_authenticated = validate_session(session_id)

        # Route to appropriate handler
        if path == '/':
            home.handle_index(self, is_authenticated)
        elif path == '/login':
            auth.handle_login_form(self)
        elif path == '/logout':
            auth.handle_logout(self)
        elif self.path.startswith('/static/'):
            home.handle_static_file(self)
        elif self.path == '/manage-instances':
            instance_management.handle_manage_instances_page(self, get_server_state())
        elif self.path == '/api/instances':
            instance_management.handle_get_instances(self, get_server_state())
        elif self.path == '/health':
            home.handle_health_check(self, get_server_state())
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Get content length
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # Check authentication status for protected routes
        session_id = get_session_id(self.headers)
        is_authenticated = validate_session(session_id)

        # Route to appropriate handler
        if path == '/api/login':
            auth.handle_login_api(self, post_data, set_user_session)
        elif path == '/api/generate-file':
            if is_authenticated:
                file_handling.handle_generate_file(self, post_data)
            else:
                self.send_json_response({"success": False, "message": "Authentication required"}, 401)
        elif path == '/api/upload-file':
            if is_authenticated:
                file_handling.handle_upload_file(self, post_data, self.headers)
            else:
                self.send_json_response({"success": False, "message": "Authentication required"}, 401)
        elif self.path == '/api/instances/register':
            instance_management.handle_register_instance(self, get_server_state())
        elif self.path == '/api/instances/ping':
            instance_management.handle_ping_instance(self, get_server_state())
        else:
            self.send_error(404, "Not Found")

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def run_server(host, port, debug=False):
    set_master_state(port)
    hook_state_for_cleanup(get_server_state)
    handler = AideskHandler
    with socketserver.TCPServer((host, port), handler) as httpd:
        print(f'Starting aidesk server on {host}:{port}...')
        if debug:
            print('Debug mode enabled')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nServer stopped.')
            httpd.shutdown()
