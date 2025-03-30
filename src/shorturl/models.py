from sqlalchemy import Table, Column, Integer, Boolean, MetaData, String
metadata = MetaData()

short_link = Table(
    "short_link",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("username", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
    Column("is_active", Boolean, default=False, nullable=False)
)
