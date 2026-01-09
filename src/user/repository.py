from common.db. import MarcoAsyncPostgreSQL
from fastapi import HTTPException
from uuid import UUID
from typing import Optional
from .schema import UserData


class UserRepository:

    def __init__(self):
        db = MarcoAsyncPostgreSQL()
        db.open_pool()
        self.connection = db

    def _tuple_to_dict(self, row, columns):
        """Convert a database row tuple to a dictionary using column names"""
        if not row:
            return None
        return dict(zip(columns, row))

    async def get_user_by_uuid(self, uuid: UUID) -> Optional[UserData]:
        async with self.connection.get_cursor() as cursor:
            not_allowed_users = [
                "0c788fe7-f66f-4db1-9cf3-9419b97c44e1",
                "902b790e-885a-4e05-8ce0-e87978641af8",
                "bdd9afda-d40d-4caa-86bf-9078b6b76f51",
            ]

            if str(uuid) in not_allowed_users:
                raise HTTPException(
                    status_code=500,
                    detail="Not allowed to get this user",
                )

            query = """
                SELECT
                    uuid, first_name, last_name, email, is_active,
                    is_pending, profile_picture_url, job_title,
                    created_at, updated_at, deleted_at
                FROM
                    users u
                WHERE
                    u.uuid = %s
                    AND deleted_at IS NULL
            """

            await cursor.execute(query, (uuid,))
            result = await cursor.fetchone()

            if not result:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "message": "User not found",
                        "error": "USER_NOT_FOUND"
                    },
                )

            columns = [desc[0] for desc in cursor.description]
            user_dict = self._tuple_to_dict(result, columns)
            return UserData(**user_dict)

    async def get_all_users_async(self):
        async with self.connection.get_cursor() as cursor:
            query = """
                SELECT
                    uuid, first_name, last_name, email, is_active,
                    is_pending, profile_picture_url, job_title,
                    created_at, updated_at, deleted_at
                FROM users u
                WHERE u.deleted_at IS NULL
                ORDER BY created_at DESC;
            """

            await cursor.execute(query)
            results = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            return [UserData(**self._tuple_to_dict(user, columns))
                    for user in results]

    async def create_user_async(self, user_data: UserData) -> UserData:
        """Create a new user in the database"""
        async with self.connection.get_cursor() as cursor:
            query = """
                INSERT INTO users (
                    uuid, first_name, last_name, email, is_active,
                    is_pending, profile_picture_url, job_title,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING uuid, first_name, last_name, email, is_active,
                    is_pending, profile_picture_url, job_title,
                    created_at, updated_at, deleted_at
            """

            values = (
                user_data.uuid,
                user_data.first_name,
                user_data.last_name,
                user_data.email,
                user_data.is_active,
                user_data.is_pending,
                user_data.profile_picture_url,
                user_data.job_title,
                user_data.created_at,
                user_data.updated_at
            )

            await cursor.execute(query, values)
            result = await cursor.fetchone()

            if not result:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create user",
                )

            columns = [desc[0] for desc in cursor.description]
            user_dict = self._tuple_to_dict(result, columns)
            return UserData(**user_dict)

    async def add_user_to_business(self, user_uuid: UUID, business_uuid: UUID,
                                   role: str = None,
                                   is_primary: bool = False) -> None:
        """Add a user to a business with optional role and primary status"""
        async with self.connection.get_cursor() as cursor:
            # First check if the relationship already exists
            check_query = """
                SELECT uuid FROM user_businesses
                WHERE user_uuid = %s AND business_uuid = %s
            """
            await cursor.execute(check_query, (user_uuid, business_uuid))
            existing = await cursor.fetchone()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="User is already associated with this business",
                )

            # Insert the new relationship
            query = """
                INSERT INTO user_businesses (
                    user_uuid, business_uuid, role, is_primary, created_at,
                    updated_at
                ) VALUES (
                    %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """

            values = (user_uuid, business_uuid, role, is_primary)

            try:
                await cursor.execute(query, values)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to add user to business: {str(e)}",
                ) from e

    async def get_users_ids(self, business_uuid: UUID) -> list[UUID]:
        async with self.connection.get_cursor() as cursor:
            query = """
                SELECT user_uuid 
                FROM user_businesses 
                WHERE business_uuid = %s
            """
            await cursor.execute(query, (business_uuid,))
            results = await cursor.fetchall()
            return [row[0] for row in results]