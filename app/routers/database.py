from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.database import (
    AddDatabaseRequest,
    DatabaseConfig,
    InitDatabaseResponse,
    AddConfigRequest,
    DiscoveredTable
)
from app.models.common import ApiResponse
from app.services.db_config_service import DbConfigService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/database", tags=["Database Configuration"])


@router.get("/list", response_model=ApiResponse[List[DatabaseConfig]], dependencies=[Depends(get_current_user)])
async def get_database_list():
    """Get all database configurations"""
    try:
        configs = await DbConfigService.get_database_list()
        return ApiResponse.success(configs)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/add", response_model=ApiResponse[DatabaseConfig], dependencies=[Depends(get_current_user)])
async def add_database(request: AddDatabaseRequest):
    """Add a new database configuration"""
    try:
        config = await DbConfigService.add_database(request)
        return ApiResponse.success(config, msg="Database configuration added successfully")
    except HTTPException as e:
        return ApiResponse.error(code=e.status_code, msg=e.detail)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.get("/{guid}", response_model=ApiResponse[DatabaseConfig], dependencies=[Depends(get_current_user)])
async def get_database(guid: str):
    """Get a single database configuration by GUID"""
    try:
        config = await DbConfigService.get_database(guid)
        if not config:
            return ApiResponse.error(code=404, msg=f"Database config with guid {guid} not found")
        return ApiResponse.success(config)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.put("/{guid}", response_model=ApiResponse[DatabaseConfig], dependencies=[Depends(get_current_user)])
async def update_database(guid: str, request: AddDatabaseRequest):
    """Update an existing database configuration"""
    try:
        config = await DbConfigService.update_database(guid, request)
        return ApiResponse.success(config, msg="Database configuration updated successfully")
    except HTTPException as e:
        return ApiResponse.error(code=e.status_code, msg=e.detail)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.delete("/{guid}", response_model=ApiResponse[dict], dependencies=[Depends(get_current_user)])
async def delete_database(guid: str):
    """Delete a database configuration and related segments"""
    try:
        result = await DbConfigService.delete_database(guid)
        return ApiResponse.success(result, msg="Database configuration deleted successfully")
    except HTTPException as e:
        return ApiResponse.error(code=e.status_code, msg=e.detail)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/initialize/{guid}", response_model=ApiResponse[InitDatabaseResponse], dependencies=[Depends(get_current_user)])
async def initialize_database(guid: str):
    """Initialize database by scanning all tables and storing max IDs"""
    try:
        result = await DbConfigService.initialize_database(guid)
        response = InitDatabaseResponse(
            initialized_count=result["initialized_count"],
            segments=result["segments"]
        )
        return ApiResponse.success(response, msg=f"Initialized {result['initialized_count']} segments")
    except HTTPException as e:
        return ApiResponse.error(code=e.status_code, msg=e.detail)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/{guid}/add-config", response_model=ApiResponse[dict], dependencies=[Depends(get_current_user)])
async def add_custom_config(guid: str, request: AddConfigRequest):
    """Add a custom segment configuration"""
    try:
        result = await DbConfigService.add_custom_config(
            guid=guid,
            table_name=request.table_name,
            field_name=request.field_name,
            initial_value=request.initial_value
        )
        return ApiResponse.success(result, msg="Custom configuration added successfully")
    except HTTPException as e:
        return ApiResponse.error(code=e.status_code, msg=e.detail)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.get("/{guid}/discovered-tables", response_model=ApiResponse[List[DiscoveredTable]], dependencies=[Depends(get_current_user)])
async def get_discovered_tables(guid: str):
    """Get list of discovered new tables for a database config"""
    try:
        tables = await DbConfigService.get_discovered_tables(guid)
        return ApiResponse.success(tables)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))
