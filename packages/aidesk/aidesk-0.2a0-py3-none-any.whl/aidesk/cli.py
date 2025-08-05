import argparse
import sys
import os
from .server import run_server

def main():
    parser = argparse.ArgumentParser(description='Start the aidesk web service')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on (default: 8000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    # Create necessary directories
    if not os.path.exists('generated_files'):
        os.makedirs('generated_files')
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    try:
        run_server(args.host, args.port, args.debug)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
