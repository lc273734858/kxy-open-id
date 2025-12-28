from fastapi import HTTPException, status
from app.redis_client import RedisClient
from app.models.database import SegmentResponse
from app.services.db_config_service import DbConfigService


class SegmentService:
    SEGMENT_PREFIX = "kxy:id:segment:"
    FAILURE_PREFIX = "kxy:id:failure:"

    @classmethod
    async def allocate_segment(
        cls,
        system_code: str,
        db_name: str,
        table_name: str,
        field_name: str,
        segment_count: int = 10000
    ) -> SegmentResponse:
        """
        Allocate a segment of IDs atomically using Redis INCRBY.
        Returns the start and end of the allocated segment.

        If the segment cache doesn't exist:
        1. Check for failure marker (table doesn't exist)
        2. Try to find database config and initialize the field
        3. If table exists, initialize cache and allocate segment
        4. If table doesn't exist, set failure marker (1 minute TTL) and return error
        """
        redis_client = await RedisClient.get_instance()

        segment_key = f"{system_code}:{db_name}:{table_name}:{field_name}".lower()
        redis_key = f"{cls.SEGMENT_PREFIX}{segment_key}"
        failure_key = f"{cls.FAILURE_PREFIX}{segment_key}"

        # Check if segment cache exists
        exists = await redis_client.exists(redis_key)
        if not exists:
            # Check if there's a failure marker (table doesn't exist)
            failure_marker = await redis_client.get(failure_key)
            if failure_marker:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Table or field does not exist for key: {segment_key}. Please check your database configuration."
                )

            # Try to find database configuration
            db_config = await DbConfigService.find_database_by_system_and_db(system_code, db_name)
            if not db_config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Database configuration not found for system_code: {system_code}, db_name: {db_name}. Please add database configuration first."
                )

            # Try to initialize the field
            max_id = await DbConfigService.initialize_single_field(db_config, db_name, table_name, field_name)
            if max_id is None:
                # Table or field doesn't exist, set failure marker with 1 minute TTL
                await redis_client.setex(failure_key, 60, "1")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Table '{table_name}' or field '{field_name}' does not exist in database '{db_name}'. Please check your database schema."
                )

        # Allocate segment
        new_max = await redis_client.incrby(redis_key, segment_count)

        start = new_max - segment_count + 1
        end = new_max

        return SegmentResponse(start=start, end=end)
