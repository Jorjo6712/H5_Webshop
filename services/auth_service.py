import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import User
from dtos.user_dto import UserDTO


class AuthService:

    def __init__(self, session: Session):
        self.session = session

    def register_user(self, dto: UserDTO) -> User:
        password_hash = bcrypt.hashpw(
            dto.password.encode("UTF-8"),
            bcrypt.gensalt()
        ).decode("UTF-8")

        user = User(
            username=dto.username,
            password_hash=password_hash
        )

        self.session.add(user)
        self.session.commit()

        return user

    def authenticate_user(
        self,
        username: str,
        password: str
    ) -> User | None:

        user = self.session.scalar(
            select(User).where(User.username == username)
        )

        if user is None:
            return None

        password_matches = bcrypt.checkpw(
            password.encode("UTF-8"),
            user.password_hash.encode("UTF-8")
        )

        if not password_matches:
            return None

        return user