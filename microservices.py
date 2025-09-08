#!/usr/bin/env python3
"""
ShopQuote Microservices Integration
Local testing and development of file processing microservices
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ShopQuote Microservices", description="File Processing Microservices")

# Microservice configurations
MICROSERVICES = {
    "dxf": {
        "name": "DXF Parser",
        "port": 8001,
        "path": "uploaders/DXF",
        "endpoint": "/parse-dxf"
    },
    "pdf": {
        "name": "PDF Parser",
        "port": 8002,
        "path": "uploaders/PDF",
        "endpoint": "/parse-pdf"
    },
    "step": {
        "name": "STEP Parser",
        "port": 8003,
        "path": "uploaders/step",
        "endpoint": "/parse-step"
    },
    "trace": {
        "name": "Trace Logger",
        "port": 8004,
        "path": "uploaders/trace",
        "endpoint": "/log-trace"
    }
}

class MicroserviceManager:
    """Manages local microservice instances"""

    def __init__(self):
        self.running_services = {}
        self.base_path = Path(__file__).parent

    async def start_service(self, service_name: str) -> bool:
        """Start a specific microservice"""
        if service_name not in MICROSERVICES:
            logger.error(f"Unknown service: {service_name}")
            return False

        service_config = MICROSERVICES[service_name]
        service_path = self.base_path / service_config["path"]

        if not service_path.exists():
            logger.error(f"Service path not found: {service_path}")
            return False

        try:
            # Check if requirements.txt exists
            requirements_file = service_path / "requirements.txt"
            if requirements_file.exists():
                logger.info(f"Installing requirements for {service_name}")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True, capture_output=True)

            # Start the service
            main_file = service_path / "main.py"
            if not main_file.exists():
                # Try alternative main files
                alternatives = ["app.py", "server.py", "run.py"]
                main_file = None
                for alt in alternatives:
                    alt_file = service_path / alt
                    if alt_file.exists():
                        main_file = alt_file
                        break

            if not main_file:
                logger.error(f"No main file found for {service_name}")
                return False

            logger.info(f"Starting {service_name} service on port {service_config['port']}")

            # Start service in background
            process = subprocess.Popen([
                sys.executable, str(main_file)
            ], cwd=str(service_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.running_services[service_name] = {
                "process": process,
                "config": service_config,
                "port": service_config["port"]
            }

            # Wait a moment for service to start
            await asyncio.sleep(2)

            return True

        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            return False

    async def stop_service(self, service_name: str) -> bool:
        """Stop a specific microservice"""
        if service_name not in self.running_services:
            return False

        try:
            service_info = self.running_services[service_name]
            service_info["process"].terminate()
            service_info["process"].wait(timeout=5)
            del self.running_services[service_name]
            logger.info(f"Stopped {service_name} service")
            return True
        except Exception as e:
            logger.error(f"Failed to stop {service_name}: {e}")
            return False

    async def start_all_services(self) -> Dict[str, bool]:
        """Start all available microservices"""
        results = {}
        for service_name in MICROSERVICES.keys():
            results[service_name] = await self.start_service(service_name)
        return results

    async def stop_all_services(self) -> Dict[str, bool]:
        """Stop all running microservices"""
        results = {}
        for service_name in list(self.running_services.keys()):
            results[service_name] = await self.stop_service(service_name)
        return results

    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {}
        for service_name, config in MICROSERVICES.items():
            if service_name in self.running_services:
                service_info = self.running_services[service_name]
                process = service_info["process"]
                is_running = process.poll() is None
                status[service_name] = {
                    "status": "running" if is_running else "stopped",
                    "port": config["port"],
                    "pid": process.pid if is_running else None
                }
            else:
                status[service_name] = {
                    "status": "stopped",
                    "port": config["port"],
                    "pid": None
                }
        return status

# Global microservice manager
manager = MicroserviceManager()

@app.get("/")
async def root():
    """Root endpoint with service status"""
    return {
        "message": "ShopQuote Microservices Hub",
        "services": manager.get_service_status(),
        "endpoints": {
            "start_service": "/start/{service_name}",
            "stop_service": "/stop/{service_name}",
            "start_all": "/start-all",
            "stop_all": "/stop-all",
            "status": "/status"
        }
    }

@app.post("/start/{service_name}")
async def start_service(service_name: str):
    """Start a specific microservice"""
    success = await manager.start_service(service_name)
    if success:
        return {"message": f"Started {service_name} service", "status": "success"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to start {service_name}")

@app.post("/stop/{service_name}")
async def stop_service(service_name: str):
    """Stop a specific microservice"""
    success = await manager.stop_service(service_name)
    if success:
        return {"message": f"Stopped {service_name} service", "status": "success"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to stop {service_name}")

@app.post("/start-all")
async def start_all_services():
    """Start all microservices"""
    results = await manager.start_all_services()
    return {
        "message": "Started all services",
        "results": results,
        "summary": {
            "total": len(results),
            "successful": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r)
        }
    }

@app.post("/stop-all")
async def stop_all_services():
    """Stop all microservices"""
    results = await manager.stop_all_services()
    return {
        "message": "Stopped all services",
        "results": results,
        "summary": {
            "total": len(results),
            "successful": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r)
        }
    }

@app.get("/status")
async def get_status():
    """Get status of all services"""
    return {
        "services": manager.get_service_status(),
        "timestamp": "2025-01-01T00:00:00Z"
    }

@app.post("/test-file-processing")
async def test_file_processing(file: UploadFile = File(...)):
    """Test file processing with available microservices"""
    filename = file.filename.lower()

    # Determine which service to use based on file extension
    if filename.endswith('.dxf'):
        service_name = 'dxf'
    elif filename.endswith('.pdf'):
        service_name = 'pdf'
    elif filename.endswith(('.step', '.stp')):
        service_name = 'step'
    else:
        return {"error": "Unsupported file type", "supported": [".dxf", ".pdf", ".step", ".stp"]}

    # Check if service is running
    status = manager.get_service_status()
    if status[service_name]["status"] != "running":
        return {"error": f"{service_name} service is not running", "status": status}

    # Read file content
    content = await file.read()

    # Simulate processing (in real implementation, this would call the actual service)
    result = {
        "filename": file.filename,
        "service": service_name,
        "file_size": len(content),
        "processed": True,
        "extracted_data": {
            "part_number": "SIMULATED-PART-001",
            "material": "SIMULATED-MATERIAL",
            "dimensions": "SIMULATED-DIMENSIONS"
        }
    }

    return result

if __name__ == "__main__":
    print("🚀 Starting ShopQuote Microservices Hub...")
    print("📱 Open your browser to: http://localhost:8005")
    print("🎯 Available endpoints:")
    print("  GET  /           - Service status and endpoints")
    print("  POST /start/{service} - Start specific service")
    print("  POST /stop/{service}  - Stop specific service")
    print("  POST /start-all   - Start all services")
    print("  POST /stop-all    - Stop all services")
    print("  GET  /status      - Get all service statuses")
    print("  POST /test-file-processing - Test file processing")

    uvicorn.run(app, host="0.0.0.0", port=8005)