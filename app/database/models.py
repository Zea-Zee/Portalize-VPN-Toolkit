from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Text, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)                 #user's telegram ID
    enter_date = Column(DateTime, nullable=False)                           #date when user made /start
    referral_balance = Column(Integer, default=0)                           #ruble balance of referal program
    referral_id = Column(Integer, ForeignKey('users.id'), nullable=True, default=None)    #id of referal who invinted user
    referrals = relationship("User", backref="referrer", remote_side=[id])  #relation to all invited users
    subscription = relationship("Subscription", back_populates="user")      #link to user's subscription
    config = relationship("Config", back_populates="user", uselist=False)   #ref to confgis

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Integer, nullable=False)                                  #0-none, 1-trial, 2-5: 1-12m, 6-9: present 1-12m
    start_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)       #id of owner
    user = relationship("User", back_populates="subscription")
    status = Column(Enum('active', 'expired', 'archived'), default='active')

class Config(Base):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)                                   #example: openvpn
    start_date = Column(DateTime, nullable=True)
    config_file = Column(Text, nullable=False)                              #config name in filesystem
    vpn_server_id = Column(Integer, ForeignKey('vpn_servers.id'), nullable=False)
    vpn_server = relationship("VPNServer", back_populates="configs")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)       #ref to owner
    user = relationship("User", back_populates="config")

class VPNServer(Base):
    __tablename__ = 'vpn_servers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    total_slots = Column(Integer, nullable=False)
    free_slots = Column(Integer, nullable=False)
    speed_tests = relationship("SpeedTest", back_populates="vpn_server")    #refs to speedtests
    configs = relationship("Config", back_populates="vpn_server")           #refs to server's configs

class SpeedTest(Base):
    __tablename__ = 'speed_tests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vpn_id = Column(Integer, ForeignKey('vpn_servers.id'), nullable=False)
    ping = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    vpn_server = relationship("VPNServer", back_populates="speed_tests")

class PromoCode(Base):
    __tablename__ = 'promo_codes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.tg_id'), nullable=True)     #tgid of allowed for this promo
    user_tag = Column(String, nullable=True)                                #tgtag of allowed for this promo
    expiration_date = Column(DateTime, nullable=True)
    type = Column(String, nullable=False)                                   #just comment like 'friend' 'birthday' etc

class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    duration = Column(String, nullable=False)   # 7_d, 3_m, 1y etc
    price = Column(Integer, nullable=False)
    discount = Column(Integer, nullable=True, default=None)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
