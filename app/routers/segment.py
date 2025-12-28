from fastapi import APIRouter, HTTPException
from app.models.database import SegmentRequest, SegmentResponse
from app.models.common import ApiResponse
from app.services.segment_service import SegmentService

router = APIRouter(prefix="/api/segment", tags=["ID Segment Allocation"])


@router.post("/allocate", response_model=ApiResponse[SegmentResponse])
async def allocate_segment(request: SegmentRequest):
    """
    Allocate an ID segment (NO authentication required).
    Returns start and end IDs for the allocated segment.
    """
    try:
        segment = await SegmentService.allocate_segment(
            system_code=request.system_code,
            db_name=request.db_name,
            table_name=request.table_name,
            field_name=request.field_name,
            segment_count=request.segment_count
        )
        return ApiResponse.success(segment, msg=f"Allocated segment: {segment.start} to {segment.end}")
    except HTTPException as e:
        return ApiResponse.error(code=e.status_code, msg=e.detail)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))
