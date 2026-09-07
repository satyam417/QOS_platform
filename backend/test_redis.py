import asyncio

from app.api.deps import get_redis
from app.services.otp import OTPService


async def main():
    redis = get_redis()

    print("PING:", await redis.ping())

    service = OTPService(redis)

    otp = await service.send_otp("customer4@test.com")

    print("OTP:", otp)

    value = await redis.get("otp:customer4@test.com")

    print("Redis:", value)

    await redis.close()


asyncio.run(main())