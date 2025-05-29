# Cloud Environment Simulation

A web-based cloud computing environment simulator that provides three core cloud services: Storage, Database, and Compute services.

## Features

- User Authentication and Management
- Cloud Storage Service (File upload/download/delete)
- Database-as-a-Service (SQLite-based)
- Compute-as-a-Service (Python code execution)
- Modern Web Interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cloud-environment-simulation
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the application:
```bash
flask run
```

## Project Structure

```
cloud-environment-simulation/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── static/
│   └── templates/
├── instance/
├── migrations/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

## Usage

1. Register a new account or login with existing credentials
2. Access the dashboard to use cloud services
3. Upload files, create databases, or run Python code through the web interface

## Security

- All user data is stored securely
- File operations are sandboxed
- Code execution is restricted to prevent system access

## License

MIT License 