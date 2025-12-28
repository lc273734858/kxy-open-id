from fastapi import APIRouter, HTTPException
from app.models.auth import InitUserRequest, LoginRequest, TokenResponse, CheckInitResponse
from app.models.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.get("/check-init", response_model=ApiResponse[CheckInitResponse])
async def check_init():
    """Check if the system has been initialized"""
    try:
        initialized = await AuthService.check_system_initialized()
        return ApiResponse.success(CheckInitResponse(initialized=initialized))
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/init-user", response_model=ApiResponse[dict])
async def init_user(request: InitUserRequest):
    """Initialize the system with admin user credentials (first-time setup)"""
    try:
        result = await AuthService.initialize_system(request.username, request.password)
        return ApiResponse.success(result, msg="System initialized successfully")
    except HTTPException as e:
        return ApiResponse.error(code=e.status_code, msg=e.detail)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(request: LoginRequest):
    """Login with username and password, returns JWT token"""
    try:
        result = await AuthService.login(request.username, request.password)
        token_response = TokenResponse(token=result["token"], username=result["username"])
        return ApiResponse.success(token_response, msg="Login successful")
    except HTTPException as e:
        return ApiResponse.error(code=e.status_code, msg=e.detail)
    except Exception as e:
        return ApiResponse.error(code=500, msg=str(e))
