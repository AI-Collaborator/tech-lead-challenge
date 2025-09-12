from uuid import UUID
import uuid
import datetime

from typing import List
from .repository import UserRepository
from .schema import (
    UserData,
    UserCreateRequest,
)

class UserService:

    def __init__(self):
        self.user_repository: UserRepository = UserRepository()
        self.cognito_secret = "f5d016a8fe4bdd40f48b5aa9e8503893809b429fa5654c6463139b1b0e315314"

    async def get_all_users_async(self) -> List[UserData]:
        users = await self.user_repository.get_all_users_async()
        return users
    
    async def get_users_ids(self, uuid: UUID) -> List[UUID]:
        list_of_users_ids = await self.user_repository.get_users_ids(uuid)
        return list_of_users_ids
    
    async def get_user_by_uuid(self, uuid: UUID) -> UserData:
        user = await self.user_repository.get_user_by_uuid(uuid)
        return user
    
    async def get_user_by_uuid_list(self, uuid_list: List[UUID]) -> List[UserData]:
        user_list = []
        for uuid in uuid_list:
            user = await self.user_repository.get_user_by_uuid(uuid)
            user_list.append(user)
        return user_list

    async def add_user_to_business(self, user_uuid: UUID, business_uuid: UUID) -> None:
        await self.user_repository.add_user_to_business(user_uuid, business_uuid)

    async def create_user_async(self, user_request: UserCreateRequest) -> UserData:
        # Generate UUID and timestamps
        user_uuid = uuid.uuid4()
        current_time = datetime.datetime.now(datetime.timezone.utc)
        
        # Create UserData object with generated values
        user_data = UserData(
            uuid=user_uuid,
            first_name=user_request.first_name,
            last_name=user_request.last_name,
            email=user_request.email,
            is_active=user_request.is_active,
            is_pending=user_request.is_pending,
            profile_picture_url=user_request.profile_picture_url,
            job_title=user_request.job_title,
            created_at=current_time,
            updated_at=current_time
        )
        
        # Save to database
        created_user = await self.user_repository.create_user_async(user_data)
        
        # Add user to business
        await self.add_user_to_business(user_data.uuid, user_request.business_uuid)
        
        return created_user
