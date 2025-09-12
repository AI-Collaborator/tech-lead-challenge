from fastapi import FastAPI
from src.user.handler import router as user_router

import logging
import sys
import signal
import traceback
import multiprocessing
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Initialize the FastAPI application
app = FastAPI(
    title="MARCO PLATFORM API",
    description="MARCO PLATFORM API",
    version="1.0.0",
    redirect_slashes=True,
    swagger_ui_parameters={"displayRequestDuration": True},
)

# Include routers
app.include_router(user_router, prefix="/api/users", tags=["Users"])

# Run database migrations and checks before starting the server
if __name__ == "__main__":
    try:
        def handle_shutdown(signum, frame):
            logging.info("Received shutdown signal, gracefully shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)

        # Convert config values - mocked for testing
        port_number = 8000
        num_cpus = multiprocessing.cpu_count()
        num_cpus = min(num_cpus, 4)  # Mock MAX_CPU_CORES to 4
        host_addr = "0.0.0.0"
        logging.info(
            f"Starting FastAPI server at {host_addr}:{port_number} with {num_cpus} workers."
        )

        # Add reload option for development environments
        reload_enabled = True  # Mock ENV to enable reload for testing

        uvicorn.run(
            "main:app",
            host=host_addr,
            port=port_number,
            workers=(
                1 if reload_enabled else num_cpus
            ),  # Use only 1 worker when reload is enabled
            log_level="info",  # Mock LOG_LEVEL
            timeout_graceful_shutdown=10,  # Add graceful shutdown timeout
            reload=reload_enabled,  # Enable auto-reload
        )

    except Exception as e:
        logging.error(f"Unhandled exception during server startup: {e}")
        logging.error(traceback.format_exc())  # Log the full stack trace
        sys.exit(1)  # Exit the application with error code
