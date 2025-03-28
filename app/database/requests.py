from datetime import datetime

from database.models import async_session
from database.models import User, Subscription, Config, VPNServer, PromoCode, SpeedTest, SubscriptionPlan
from sqlalchemy import select


async def set_user(tg_id: int, tg_username: str, ref=None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            new_user = User(
                tg_id=tg_id,
                tg_username=tg_username,
                enter_date=datetime.utcnow(),  # Добавьте текущее время
                referral_balance=0,
                referral_id=None
            )
            session.add(new_user)
            await session.commit()


async def get_plans(type):
    async with async_session() as session:
        return await session.scalars(select(SubscriptionPlan).where(SubscriptionPlan.type == type))


async def get_plan(id=None):
    async with async_session() as session:
        return await session.scalar(select(SubscriptionPlan).where(SubscriptionPlan.id == id))


async def get_user_subscriptions(tg_user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_user_id))
        query = select(Subscription).where(
            Subscription.tg_user_id == user.tg_id
        ).order_by(Subscription.expiration_date.desc())

        result = await session.scalars(query)
        return result.all()
