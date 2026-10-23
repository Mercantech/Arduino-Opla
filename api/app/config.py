import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://opla:opla@opla-db:5432/opla",
)

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "https://opla.mercantec.tech,http://localhost:3000",
    ).split(",")
    if o.strip()
]
