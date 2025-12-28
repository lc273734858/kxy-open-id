from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DatabaseType(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"


class AddDatabaseRequest(BaseModel):
    system_code: str = Field(..., min_length=1, max_length=100, description="System code")
    db_type: DatabaseType = Field(..., description="Database type")
    db_address: str = Field(..., description="Database address (host:port)")
    db_user: str = Field(..., description="Database username")
    db_password: str = Field(..., description="Database password")
    db_name: Optional[str] = Field(None, description="Initial database name (optional)")


class DatabaseConfig(BaseModel):
    guid: str = Field(..., description="Unique identifier")
    system_code: str = Field(..., description="System code")
    db_type: DatabaseType = Field(..., description="Database type")
    db_address: str = Field(..., description="Database address")
    db_user: str = Field(..., description="Database username")
    db_password: str = Field(..., description="Database password")
    db_name: Optional[str] = Field(None, description="Database name")


class InitDatabaseRequest(BaseModel):
    guid: str = Field(..., description="Database config GUID")


class InitDatabaseResponse(BaseModel):
    initialized_count: int = Field(..., description="Number of segments initialized")
    segments: List[str] = Field(default_factory=list, description="List of segment keys")


class SegmentRequest(BaseModel):
    system_code: str = Field(..., description="System code")
    db_name: str = Field(..., description="Database name")
    table_name: str = Field(..., description="Table name")
    field_name: str = Field(..., description="Field name")
    segment_count: int = Field(10000, ge=1, le=9223372036854775807, description="Segment count (max: 2^63-1)")


class SegmentResponse(BaseModel):
    start: int = Field(..., description="Start ID of segment")
    end: int = Field(..., description="End ID of segment")


class AddConfigRequest(BaseModel):
    table_name: str = Field(..., description="Table name")
    field_name: str = Field(..., description="Field name for custom config")
    initial_value: int = Field(0, description="Initial value")


class DiscoveredTable(BaseModel):
    database: str = Field(..., description="Database name")
    table: str = Field(..., description="Table name")
    primary_key: str = Field(..., description="Primary key field")
    max_id: Optional[int] = Field(None, description="Current max ID")
