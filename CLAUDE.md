# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python FastAPI application named "kxy-open-id" with integrated frontend. The project is a monolithic application where the backend serves both API endpoints and the frontend static files. This is part of the yudao-python workspace ecosystem.

## Development Commands

### Running the Application (Production Mode)

```bash
# Build frontend first (required before running)
cd frontend && npm install && npm run build && cd ..

# Run the FastAPI server (serves both API and frontend)
uvicorn app.main:app --reload --host 0.0.0.0 --port 5801
```

Access the application at: http://localhost:5801

### Development Mode (Frontend Only)

If you need to develop the frontend separately:

```bash
# Terminal 1: Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 5801

# Terminal 2: Run frontend dev server
cd frontend && npm run dev
```

Frontend dev server: http://localhost:3000 (with hot reload)
Backend API: http://localhost:5801

### Debugging

The project is configured for debugging with VSCode:
- **FastAPI Debug**: Launches the application on port 5801 with hot reload enabled
- **Current File Debug**: Runs the currently open Python file

## Project Structure

The application follows a standard FastAPI structure:
- `app/main.py` - Main application entry point
- `log/` - Application logs (gitignored)
- `export_excels/` - Excel export directory (gitignored)
- `testImage/` - Test image directory (gitignored)
- `.venv` - Python virtual environment (gitignored)

## Development Rules

This project follows the 驿氪 (Ezr) internal development standards. Key MCP servers are configured with development rules for:
- Backend development base rules
- API request specifications
- MySQL database design and operations
- Redis usage specifications
- ClickHouse query specifications
- Elasticsearch usage and best practices
- Message center integration
- SpiderConn microservice specifications
- GRPC to dual-protocol migration
- Python development standards

When implementing features or making changes, refer to these development standards using the available MCP server tools.

## Notes

- The application uses port 5801 by default
- Hot reload is enabled during development
- All Python bytecode files (.pyc) and log files are gitignored
