import pydantic
import datetime
from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship


class Org(Base):
    __tablename__ = "org"

    id = Column(Integer, primary_key=True, index=True)
    Ext_Provider = Column(String)
    Ext_Provider_Key = Column(String)
    Ext_Provider_URL = Column(String)
    Ext_Provider_UserName = Column(String)
    Manage_API_Key = Column(String)
    Manage_Org_Id = Column(String)
    Manage_Org_Name = Column(String)
    Manage_URL = Column(String)
    Manage_UserName = Column(String)

    floor = relationship("Floor", back_populates="org")
    zoner = relationship("ZoneRoom", back_populates="org")
    dataserver = relationship("DataServer", back_populates="org")
    dc_sessions = relationship("DCSessions", back_populates="org")


class Config:
    arbitrary_types_allowed = True


@pydantic.dataclasses.dataclass(config=Config)
class Dataclass:
    value: Org


class Floor(Base):
    __tablename__ = "floor"

    id = Column(Integer, primary_key=True, index=True)
    Ext_Building_Id = Column(String)
    Ext_Floor_Id = Column(String)
    Manage_Building_Id = Column(String)
    Manage_Building_Name = Column(String)
    Manage_Floor_Id = Column(String)
    Manage_Floor_Name = Column(String)
    Manage_Org_Id = Column(String)
    Manage_Site_Id = Column(String)
    Manage_Site_Name = Column(String)
    org_id = Column(Integer, ForeignKey("org.id"))

    org = relationship("Org", back_populates="floor")
    zoner = relationship("ZoneRoom", back_populates='floor')
    dc_sessions = relationship("DCSessions", back_populates="floor")


class Config:
    arbitrary_types_allowed = True


@pydantic.dataclasses.dataclass(config=Config)
class Dataclass:
    value: Floor


class ZoneRoom(Base):
    __tablename__ = "zone_room"

    id = Column(Integer, primary_key=True, index=True)
    Ext_Boundary_Points = Column(String)
    Ext_Floor_Id = Column(String)
    Ext_Room_Id = Column(String)
    Ext_Room_Name = Column(String)
    Ext_Zone_Id = Column(String)
    Ext_Zone_Name = Column(String)
    Ext_Zone_Room_Name = Column(String)
    floor_id = Column(Integer, ForeignKey("floor.id"))
    org_id = Column(Integer, ForeignKey("org.id"))

    floor = relationship("Floor", back_populates="zoner")
    org = relationship("Org", back_populates="zoner")
    dc_sessions = relationship("DCSessions", back_populates="zoner")


class Config:
    arbitrary_types_allowed = True


@pydantic.dataclasses.dataclass(config=Config)
class Dataclass:
    value: ZoneRoom


class DataServer(Base):
    __tablename__ = "data_server"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    org_id = Column(Integer, ForeignKey("org.id"))

    org = relationship("Org", back_populates="dataserver")
    dc_sessions = relationship("DCSessions", back_populates="dataserver")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    pwd_hash = Column(String, nullable=True)
    name = Column(String)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)
    dc_sessions_id = Column(ForeignKey("dc_sessions.id"))

    dc_sessions = relationship("DCSessions", back_populates="user")


class DCSessions(Base):
    __tablename__ = "dc_sessions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    org_id = Column(Integer, ForeignKey("org.id"))
    floor_id = Column(Integer, ForeignKey("floor.id"))
    zone_room_id = Column(Integer, ForeignKey("zone_room.id"))
    tag_ids = Column(Integer)
    session_name = Column(String)
    percent_completed = Column(Integer)
    dataServer_id = Column(Integer, ForeignKey("data_server.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    org = relationship("Org", back_populates="dc_sessions")
    user = relationship("User", back_populates="dc_sessions")
    dataserver = relationship("DataServer", back_populates="dc_sessions")
    floor = relationship("Floor", back_populates="dc_sessions")
    zoner = relationship("ZoneRoom", back_populates='dc_sessions')

