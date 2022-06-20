from pydantic import BaseModel, Field
from models import *
from typing import List, Optional


class OrgBase(BaseModel):
    Ext_Provider: Optional[str] = Field(None)
    Ext_Provider_Key: Optional[str]
    Ext_Provider_URL: Optional[str]
    Ext_Provider_UserName: Optional[str]
    Manage_API_Key: Optional[str]
    Manage_Org_Id: Optional[str]
    Manage_Org_Name: Optional[str]
    Manage_URL: Optional[str]
    Manage_UserName: Optional[str]


class Org(OrgBase):
    id: int = Field(...)
    floors: List[Floor] = Field(None)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


@pydantic.dataclasses.dataclass(config=Config)
class Dataclass:
    value: Org


class FloorBase(BaseModel):
    Ext_Building_Id: Optional[str]
    Ext_Floor_Id: Optional[str]
    Manage_Building_Id: Optional[str]
    Manage_Building_Name: Optional[str]
    Manage_Floor_Id: Optional[str]
    Manage_Floor_Name: Optional[str]
    Manage_Org_Id: Optional[str]
    Manage_Site_Id: Optional[str]
    Manage_Site_Name: Optional[str]
    org_id: int


class Floor(FloorBase):
    id: int
    org_id: int

    class Config:
        orm_mode = True


class ZoneRoomBase(BaseModel):
    Ext_Boundary_Points: Optional[str] = Field(None)
    Ext_Floor_Id: Optional[str]
    Ext_Room_Id: Optional[str]
    Ext_Room_Name: Optional[str]
    Ext_Zone_Id: Optional[str]
    Ext_Zone_Name: Optional[str]
    Ext_Zone_Room_Name: Optional[str]


class ZoneRoom(ZoneRoomBase):
    id: int
    floor_id: Optional[str]

    class Config:
        orm_mode = True


class DataServerBase(BaseModel):
    id: int
    name: Optional[str] = Field(None)
    address: str


    class Config:
        orm_mode = True


'''

User Schemas

'''


class UserSchema(BaseModel):
    name: str = Field(...)
    username: str = Field(...)
    pwd_hash: str = Field(None)
    role: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "Your Name",
                "username": "Username_example",
                "pwd_hash": "your hash password",
                "role": "Admin/ Clinician/ Nurse"
            }
        }


class SetUserCredentialsSchema(BaseModel):
    name: str = Field(...)
    pwd_hash: str = Field(...)
    role: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "Username_example",
                "pwd_hash": "your hash password",
                "role": "your role"
            }
        }


class ValidateCredentialSchema(BaseModel):
    username: str = Field(...)
    pwd_hash: str = Field(...)

    class Config:
        the_schema = {
            "user_example": {
                "username": "sample_username",
                "pwd_hash": "Password123"
            }
        }
'''

Sessions Schema

'''


class InitializeSessionSchema(BaseModel):
    dataServer_id: int = Field(...)
    username: str = Field(...)
    org_id: int = Field(...)
    floor_id: int = Field(...)
    tag_ids: str = Field(...)
    session_name: str = Field(...)

    class Config:
        orm_mode = True
        the_schema = {
            "session_example": {
                "dataServer_id": "dataServer_id",
                "username": "username",
                "org_id" : " org_id",
                "floor_id": "floor_id",
                "tag_ids": "tag_ids",
                "session_name": "session_name"
            }
        }

