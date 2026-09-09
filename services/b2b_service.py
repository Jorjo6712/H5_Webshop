import bcrypt
import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.b2b_client import B2BClient


class B2BService:
    def __init__(self, session: Session):
        self.session = session

    def authenticate(
        self,
        api_key: str,
        api_secret: str
    ) -> B2BClient | None:

        client = self.session.scalar(
            select(B2BClient)
            .where(B2BClient.api_key == api_key)
        )

        if client is None:
            return None

        if not bcrypt.checkpw(
            api_secret.encode("utf-8"),
            client.api_secret_hash.encode("utf-8")
        ):
            return None

        return client

    
    def create_client(self, company_name: str) -> tuple[B2BClient, str]:
        api_key = secrets.token_urlsafe(32)
        api_secret = secrets.token_urlsafe(48)

        api_secret_hash = bcrypt.hashpw(
            api_secret.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        client = B2BClient(
            company_name=company_name,
            api_key=api_key,
            api_secret_hash=api_secret_hash
        )

        self.session.add(client)
        self.session.commit()

        return client, api_secret