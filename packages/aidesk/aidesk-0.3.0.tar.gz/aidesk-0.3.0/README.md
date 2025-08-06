# aidesk

A simple web service with file operations, authentication and instance management.

## Features

- Web service based on Python's built-in `http.server`
- User authentication (login/logout)
- API endpoint to generate files from text content
- API endpoint to upload files
- Instance registration and management
- CLI to start the service with custom host and port
- Web interface for API documentation and instance management

## Installation
pip install aidesk

## Usage

Start the web service:
# Default host (localhost) and port (8000)
aidesk

# Custom host and port
aidesk --host 0.0.0.0 --port 8080

# Debug mode
aidesk --debug

Once the service is running, you can access the API documentation at http://localhost:8000

Default credentials:
- Username: admin
- Password: admin

## API

### Authentication

**POST /api/login**

Parameters:
- `username`: Your username
- `password`: Your password

Example:
curl -X POST http://localhost:8000/api/login \
  -d "username=admin&password=admin"

**POST /api/logout**

Example:
curl -X POST http://localhost:8000/api/logout \
  -b "session_id=your_session_id"

### File Operations

**POST /api/generate-file** (Requires authentication)

Parameters:
- `filename`: Name of the file to generate
- `content`: Multi-line text content for the file

Example:
curl -X POST http://localhost:8000/api/generate-file \
  -b "session_id=your_session_id" \
  -d "filename=example.txt&content=First line%0ASecond line%0AThird line"

**POST /api/upload-file** (Requires authentication)

Parameters:
- File data as multipart/form-data

Example:
curl -X POST http://localhost:8000/api/upload-file \
  -b "session_id=your_session_id" \
  -F "file=@localfile.txt"

### Instance Management

**POST /api/instances/register** (No authentication required)

Registers another aidesk instance with this server.

Parameters:
- `hostname`: Instance hostname
- `ip`: Instance IP address
- `port`: Instance port number
- `start_time`: Instance start time (ISO format)

Example:
curl -X POST http://localhost:8000/api/instances/register \
  -d "hostname=worker1&ip=192.168.1.100&port=8001&start_time=$(date -Iseconds)"

**POST /api/instances/ping** (No authentication required)

Updates instance status (heartbeat).

Parameters:
- `instance_id`: ID of the instance (format: ip:port)

Example:
curl -X POST http://localhost:8000/api/instances/ping \
  -d "instance_id=192.168.1.100:8001"

**GET /api/instances** (Requires authentication)

Gets all registered instances.

Example:
curl -X GET http://localhost:8000/api/instances \
  -b "session_id=your_session_id"

**DELETE /api/instances/{instance_id}** (Requires authentication)

Removes a registered instance.

Example:
curl -X DELETE http://localhost:8000/api/instances/192.168.1.100:8001 \
  -b "session_id=your_session_id"

## Web Interface

- Home/API Documentation: http://localhost:8000
- Login: http://localhost:8000/login
- Instance Management: http://localhost:8000/manage-instances

## License

MIT
