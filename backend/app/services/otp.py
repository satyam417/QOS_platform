import secrets

from redis.asyncio import Redis

from app.core.config import settings

import random
from datetime import datetime, timedelta, timezone


class OTPService:

    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def generate_otp() -> str:
        max_value = 10 ** settings.OTP_LENGTH

        otp_number = secrets.randbelow(max_value)

        return f"{otp_number:0{settings.OTP_LENGTH}d}"

    async def send_otp(
        self,
        identifier: str,
    ) -> str:

        identifier = identifier.lower().strip()

        otp = self.generate_otp()

        key = f"otp:{identifier}"

        await self.redis.set(
            key,
            otp,
            ex=settings.OTP_EXPIRE_SECONDS,
        )

        # Development only.
        # Do NOT log OTPs in production.
        if settings.ENVIRONMENT == "development":
            print(
                f"[DEV OTP] {identifier}: {otp}"
            )

        return otp

    async def verify_otp(
        self,
        identifier: str,
        otp: str,
    ) -> bool:

        identifier = identifier.lower().strip()

        key = f"otp:{identifier}"

        stored_otp = await self.redis.get(key)

        if not stored_otp:
            return False

        if isinstance(stored_otp, bytes):
            stored_otp = stored_otp.decode()

        if not secrets.compare_digest(
            stored_otp,
            otp,
        ):
            return False

        await self.redis.delete(key)

        return True

#customer Registeration and OTP verification service

# Temporary in-memory OTP storage.
# Later this should be moved to Redis.
otp_store: dict[str, dict] = {}


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def create_otp(contact: str) -> str:
    otp = generate_otp()

    otp_store[contact] = {
        "otp": otp,
        "expires_at": (
            datetime.now(timezone.utc)
            + timedelta(minutes=5)
        ),
    }

    # Development only.
    # In production, send this through SMS/email.
    print(f"OTP for {contact}: {otp}")

    return otp


def verify_otp(
    contact: str,
    otp: str,
) -> bool:

    record = otp_store.get(contact)

    if not record:
        return False

    if datetime.now(timezone.utc) > record["expires_at"]:
        del otp_store[contact]
        return False

    if record["otp"] != otp:
        return False

    del otp_store[contact]

    return True