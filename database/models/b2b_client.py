from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class B2BClient(Base):
    __tablename__ = "b2b_clients"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    api_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    api_secret_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )