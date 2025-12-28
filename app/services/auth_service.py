from app.redis_client import RedisClient
from app.utils.auth_utils import encrypt_password, decrypt_password, create_jwt_token
from fastapi import HTTPException, status


class AuthService:
    SYSTEM_INIT_KEY = "kxy:id:system:init"
    SYSTEM_USERNAME_KEY = "kxy:id:system:username"
    SYSTEM_PASSWORD_KEY = "kxy:id:system:password"

    @classmethod
    async def check_system_initialized(cls) -> bool:
        """Check if the system has been initialized"""
        redis_client = await RedisClient.get_instance()
        init_value = await redis_client.get(cls.SYSTEM_INIT_KEY)
        return init_value == "1"

    @classmethod
    async def initialize_system(cls, username: str, password: str):
        """Initialize the system with admin user credentials"""
        redis_client = await RedisClient.get_instance()

        is_initialized = await cls.check_system_initialized()
        if is_initialized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System already initialized"
            )

        hashed_password = encrypt_password(password)

        await redis_client.set(cls.SYSTEM_USERNAME_KEY, username)
        await redis_client.set(cls.SYSTEM_PASSWORD_KEY, hashed_password)
        await redis_client.set(cls.SYSTEM_INIT_KEY, "1")

        return {"username": username}

    @classmethod
    async def login(cls, username: str, password: str) -> dict:
        """Login with username and password, return JWT token"""
        redis_client = await RedisClient.get_instance()

        is_initialized = await cls.check_system_initialized()
        if not is_initialized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System not initialized. Please initialize first."
            )

        stored_username = await redis_client.get(cls.SYSTEM_USERNAME_KEY)
        stored_password = await redis_client.get(cls.SYSTEM_PASSWORD_KEY)

        if not stored_username or not stored_password:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="System configuration error"
            )

        if username != stored_username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        if encrypt_password(password)!= stored_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        token = create_jwt_token(username)

        return {"token": token, "username": username}
