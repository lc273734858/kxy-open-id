import json
import uuid
from typing import List, Optional
from fastapi import HTTPException, status
from app.redis_client import RedisClient
from app.models.database import DatabaseConfig, AddDatabaseRequest, DiscoveredTable
from app.services.db_connector import DbConnectorFactory


class DbConfigService:
    DB_CONFIG_PREFIX = "kxy:id:db_config:"
    SEGMENT_PREFIX = "kxy:id:segment:"
    DISCOVERED_PREFIX = "kxy:id:discovered_tables:"

    @classmethod
    async def add_database(cls, config: AddDatabaseRequest) -> DatabaseConfig:
        """Add a new database configuration"""
        redis_client = await RedisClient.get_instance()

        guid = str(uuid.uuid4())

        db_config = DatabaseConfig(
            guid=guid,
            system_code=config.system_code,
            db_type=config.db_type,
            db_address=config.db_address,
            db_user=config.db_user,
            db_password=config.db_password,
            db_name=config.db_name
        )

        config_key = f"{cls.DB_CONFIG_PREFIX}{guid}"
        await redis_client.set(config_key, db_config.model_dump_json())

        return db_config

    @classmethod
    async def get_database_list(cls) -> List[DatabaseConfig]:
        """Get all database configurations"""
        redis_client = await RedisClient.get_instance()

        keys = []
        async for key in redis_client.scan_iter(match=f"{cls.DB_CONFIG_PREFIX}*"):
            keys.append(key)

        configs = []
        for key in keys:
            config_json = await redis_client.get(key)
            if config_json:
                configs.append(DatabaseConfig.model_validate_json(config_json))

        return configs

    @classmethod
    async def get_database(cls, guid: str) -> Optional[DatabaseConfig]:
        """Get a single database configuration by GUID"""
        redis_client = await RedisClient.get_instance()

        config_key = f"{cls.DB_CONFIG_PREFIX}{guid}"
        config_json = await redis_client.get(config_key)

        if not config_json:
            return None

        return DatabaseConfig.model_validate_json(config_json)

    @classmethod
    async def find_database_by_system_and_db(cls, system_code: str, db_name: str) -> Optional[DatabaseConfig]:
        """Find database configuration by system_code and db_name"""
        configs = await cls.get_database_list()

        for config in configs:
            if config.system_code.lower() == system_code.lower() and config.db_name and config.db_name.lower() == db_name.lower():
                return config

        return None

    @classmethod
    async def update_database(cls, guid: str, config: AddDatabaseRequest) -> DatabaseConfig:
        """Update an existing database configuration"""
        redis_client = await RedisClient.get_instance()

        existing = await cls.get_database(guid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Database config with guid {guid} not found"
            )

        updated_config = DatabaseConfig(
            guid=guid,
            system_code=config.system_code,
            db_type=config.db_type,
            db_address=config.db_address,
            db_user=config.db_user,
            db_password=config.db_password,
            db_name=config.db_name
        )

        config_key = f"{cls.DB_CONFIG_PREFIX}{guid}"
        await redis_client.set(config_key, updated_config.model_dump_json())

        return updated_config

    @classmethod
    async def delete_database(cls, guid: str):
        """Delete a database configuration and related segments"""
        redis_client = await RedisClient.get_instance()

        config = await cls.get_database(guid)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Database config with guid {guid} not found"
            )

        config_key = f"{cls.DB_CONFIG_PREFIX}{guid}"
        await redis_client.delete(config_key)

        segment_pattern = f"{cls.SEGMENT_PREFIX}{config.system_code.lower()}:*"
        segment_keys = []
        async for key in redis_client.scan_iter(match=segment_pattern):
            segment_keys.append(key)

        if segment_keys:
            await redis_client.delete(*segment_keys)

        discovered_key = f"{cls.DISCOVERED_PREFIX}{guid}"
        await redis_client.delete(discovered_key)

        return {"deleted": True, "guid": guid}

    @classmethod
    async def initialize_database(cls, guid: str) -> dict:
        """Initialize database by scanning all tables and storing max IDs"""
        config = await cls.get_database(guid)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Database config with guid {guid} not found"
            )

        redis_client = await RedisClient.get_instance()
        connector = DbConnectorFactory.create(config)

        initialized_count = 0
        segments = []

        try:
            databases = await connector.get_databases()

            for database in databases:
                tables = await connector.get_tables(database)

                for table in tables:
                    primary_key = await connector.get_primary_key(database, table)

                    if primary_key:
                        max_id = await connector.get_max_id(database, table, primary_key)

                        if max_id is not None:
                            segment_key = f"{config.system_code}:{database}:{table}:{primary_key}".lower()
                            redis_key = f"{cls.SEGMENT_PREFIX}{segment_key}"

                            await redis_client.set(redis_key, str(max_id))
                            initialized_count += 1
                            segments.append(segment_key)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize database: {str(e)}"
            )
        finally:
            await connector.close()

        return {
            "initialized_count": initialized_count,
            "segments": segments
        }

    @classmethod
    async def add_custom_config(cls, guid: str, table_name: str, field_name: str, initial_value: int = 0) -> dict:
        """Add a custom segment configuration"""
        config = await cls.get_database(guid)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Database config with guid {guid} not found"
            )

        if not config.db_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database name not configured"
            )

        redis_client = await RedisClient.get_instance()

        segment_key = f"{config.system_code}:{config.db_name}:{table_name}:{field_name}".lower()
        redis_key = f"{cls.SEGMENT_PREFIX}{segment_key}"

        # Check if already exists
        existing_value = await redis_client.get(redis_key)
        if existing_value is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Configuration already exists for {segment_key}"
            )

        await redis_client.set(redis_key, str(initial_value))

        return {
            "segment_key": segment_key,
            "initial_value": initial_value
        }

    @classmethod
    async def get_discovered_tables(cls, guid: str) -> List[DiscoveredTable]:
        """Get list of discovered new tables for a database config"""
        redis_client = await RedisClient.get_instance()

        discovered_key = f"{cls.DISCOVERED_PREFIX}{guid}"
        tables_json = await redis_client.smembers(discovered_key)

        discovered_tables = []
        for table_json in tables_json:
            discovered_tables.append(DiscoveredTable.model_validate_json(table_json))

        return discovered_tables

    @classmethod
    async def initialize_single_field(cls, config: DatabaseConfig, db_name: str, table_name: str, field_name: str) -> Optional[int]:
        """Initialize a single table field segment by checking database and getting max ID"""
        connector = DbConnectorFactory.create(config)

        try:
            # Check if table and field exist
            exists = await connector.table_field_exists(db_name, table_name, field_name)
            if not exists:
                return None

            # Get max ID for the field
            max_id = await connector.get_max_id(db_name, table_name, field_name)

            if max_id is not None:
                redis_client = await RedisClient.get_instance()
                segment_key = f"{config.system_code}:{db_name}:{table_name}:{field_name}".lower()
                redis_key = f"{cls.SEGMENT_PREFIX}{segment_key}"

                # Initialize the segment cache
                await redis_client.set(redis_key, str(max_id))
                return max_id

            return None
        finally:
            await connector.close()
