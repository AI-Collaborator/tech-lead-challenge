from fastapi import APIRouter
from .service import UserService
from .schema import UserDataResponse, UserCreateRequest
from .service import UserService


router = APIRouter()

@router.get("", response_model=UserDataResponse)
async def get_all_users_async():
    service = UserService()
    users = await service.get_all_users_async()
    return UserDataResponse(
        data=users, status_code=200, message="Users retrieved successfully"
    )

@router.post("", response_model=UserDataResponse)
async def create_user_async(user: UserCreateRequest):
    service = UserService()
    created_user = await service.create_user_async(user)
    return UserDataResponse(
        data=created_user, status_code=200, message="User created successfully"
    )