import asyncio
import logging
from app.redis_client import RedisClient
from app.services.db_config_service import DbConfigService
from app.services.db_connector import DbConnectorFactory
from app.models.database import DiscoveredTable

logger = logging.getLogger(__name__)


class ScannerService:
    """Background service to scan databases for new tables"""

    SEGMENT_PREFIX = "kxy:id:segment:"
    DISCOVERED_PREFIX = "kxy:id:discovered_tables:"

    @classmethod
    async def scan_all_databases(cls):
        """
        Scan all configured databases for new tables.
        Stores discovered tables in Redis for manual approval.
        """
        try:
            configs = await DbConfigService.get_database_list()
            redis_client = await RedisClient.get_instance()

            for config in configs:
                try:
                    connector = DbConnectorFactory.create(config)

                    databases = await connector.get_databases()

                    for database in databases:
                        tables = await connector.get_tables(database)

                        for table in tables:
                            primary_key = await connector.get_primary_key(database, table)

                            if primary_key:
                                segment_key = f"{config.system_code}:{database}:{table}:{primary_key}".lower()
                                redis_key = f"{cls.SEGMENT_PREFIX}{segment_key}"

                                exists = await redis_client.exists(redis_key)

                                if not exists:
                                    max_id = await connector.get_max_id(database, table, primary_key)

                                    discovered_table = DiscoveredTable(
                                        database=database,
                                        table=table,
                                        primary_key=primary_key,
                                        max_id=max_id
                                    )

                                    discovered_key = f"{cls.DISCOVERED_PREFIX}{config.guid}"
                                    await redis_client.sadd(discovered_key, discovered_table.model_dump_json())

                                    logger.info(f"Discovered new table: {segment_key} with max_id={max_id}")

                    await connector.close()

                except Exception as e:
                    logger.error(f"Error scanning database config {config.guid}: {str(e)}")

        except Exception as e:
            logger.error(f"Error in scan_all_databases: {str(e)}")

    @classmethod
    async def start_background_scanner(cls):
        """Start the background scanner task"""
        while True:
            try:
                await cls.scan_all_databases()
            except Exception as e:
                logger.error(f"Error in background scanner: {str(e)}")

            await asyncio.sleep(36000)
