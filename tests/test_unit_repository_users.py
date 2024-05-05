import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User, Role
from src.schemas.user import UserSchema


from src.repository.users import create_user, get_user_by_email, confirmed_email, update_token, update_avatar_url


class TestRepositoryUsers(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.user = User(
            id=1,
            username='testuser',
            email='postgres@meail.com',
            password='12345678',
            avatar='avatar',
            role=Role.user,
            confirmed=False
        )
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user

        result = await get_user_by_email('postgres@meail.com',self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, "postgres@meail.com")

    async def test_create_user(self):
        body = UserSchema(username='testuser',email='postgres@meail.com',password='12345678',)
        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once()

    async def test_update_token(self):
        self.session = MagicMock(spec=AsyncSession)
        await update_token(self.user, 'new_token', self.session)
        self.assertEqual(self.user.refresh_token, 'new_token')
        self.session.commit.assert_awaited_once()

    async def test_confirmed_email(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user

        await confirmed_email('postgres@meail.com', self.session)
        self.assertTrue(self.user.confirmed)
        self.session.commit.assert_awaited_once()

    async def test_update_avatar_url(self):
        test_avatar = 'test_avatar'
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user

        result = await update_avatar_url('postgres@meail.com', test_avatar, self.session)
        self.assertIsInstance(result, User)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once()


if __name__ == '__name__':
    unittest.main()
