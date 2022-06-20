import httpx
import uvicorn
from fastapi import Body, Depends, FastAPI, HTTPException, requests
from sqlalchemy import exc
from sqlalchemy.orm import Session

import models
import schemas
from auth_bearer import JWTBearer
from auth_handler import signJWT
from database import SessionLocal, engine
from schemas import OrgBase, FloorBase, ZoneRoomBase, DataServerBase
from schemas import UserSchema, SetUserCredentialsSchema, ValidateCredentialSchema

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Org",
    docs_url="/onboarding/v1/")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/org", dependencies=[Depends(JWTBearer())], tags=["Org"])
def get_org(db: Session = Depends(get_db)):
    return db.query(models.Org).all()


@app.post("/org/{org_id}/addDataServer", response_model=schemas.DataServerBase, dependencies=[Depends(JWTBearer())],
          tags=["Org"])
def add_data_server(org_id: int, dataserver: DataServerBase, db: Session = Depends(get_db)):
    add_server = models.DataServer()

    add_server.name = dataserver.name
    add_server.address = dataserver.address
    add_server.org_id = org_id

    db.add(add_server)
    db.commit()

    return dataserver


@app.get("/org/{org_id}/getDataServers", dependencies=[Depends(JWTBearer())], tags=["Org"])
def get_data_server(org_id: int, db: Session = Depends(get_db)):
    org_check = db.query(models.DataServer).filter(models.DataServer.org_id == org_id).first()

    if org_check is None:
        raise HTTPException(
            status_code=404,
            detail=f" The Data server with given id :{org_id} does not exists..!"
        )
    get_server = db.query(models.DataServer.name, models.DataServer.address).distinct().all()

    return get_server


@app.post("/org", response_model=schemas.OrgBase, dependencies=[Depends(JWTBearer())], tags=["Org"])
def create_org(org: OrgBase, db: Session = Depends(get_db)):
    org_model = models.Org()
    org_model.Ext_Provider = org.Ext_Provider
    org_model.Ext_Provider_Key = org.Ext_Provider_Key
    org_model.Ext_Provider_URL = org.Ext_Provider_URL
    org_model.Ext_Provider_UserName = org.Ext_Provider_UserName
    org_model.Manage_API_Key = org.Manage_API_Key
    org_model.Manage_Org_Id = org.Manage_Org_Id
    org_model.Manage_Org_Name = org.Manage_Org_Name
    org_model.Manage_URL = org.Manage_URL
    org_model.Manage_UserName = org.Manage_UserName

    db.add(org_model)
    db.commit()
    db.refresh(org_model)
    return org


@app.delete("/Org/deleteOrg/{org_id}", dependencies=[Depends(JWTBearer())], tags=["Org"])
async def delete_org(org_id: int, db: Session = Depends(get_db)):
    book_model = db.query(models.Org).filter(models.Org.id == org_id).first()

    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail=f" The org with ID {org_id} Does not exists"
        )

    db.query(models.Org).filter(models.Org.id == org_id).delete()
    db.commit()
    return f" The Org with ID {org_id}, has been deleted successfully..!"


@app.post("/org/{org_id}/createFloor", response_model=schemas.FloorBase, dependencies=[Depends(JWTBearer())],
          tags=["Org"])
async def create_floor(org_id: int, floor: FloorBase, db: Session = Depends(get_db)):
    floor_model = models.Floor()

    floor_model.Ext_Building_Id = floor.Ext_Building_Id
    floor_model.Ext_Floor_Id = floor.Ext_Floor_Id
    floor_model.Manage_Building_Id = floor.Manage_Building_Id
    floor_model.Manage_Building_Name = floor.Manage_Building_Name
    floor_model.Manage_Floor_Id = floor.Manage_Floor_Id
    floor_model.Manage_Floor_Name = floor.Manage_Floor_Name
    floor_model.Manage_Org_Id = floor.Manage_Org_Id
    floor_model.Manage_Site_Id = floor.Manage_Site_Id
    floor_model.Manage_Site_Name = floor.Manage_Site_Name
    floor_model.org_id = org_id

    db.add(floor_model)
    db.commit()
    db.refresh(floor_model)
    return floor


@app.delete("/org/{org_id}/deleteFloor/{floor_id}", dependencies=[Depends(JWTBearer())], tags=["Org"])
async def delete_floor(org_id: int, floor_id: int, db: Session = Depends(get_db)):
    org_floor_model = db.query(models.Floor).filter(models.Floor.org_id == org_id, models.Floor.id == floor_id).first()

    if org_floor_model is None:
        raise HTTPException(
            detail=f" The org id: {org_id} with given floor id : {floor_id} does not exists..!",
            status_code=404
        )
    else:
        db.query(models.Floor).filter(models.Floor.org_id == org_id, models.Floor.id == floor_id).delete()
    db.commit()
    return f" The floor with given ID {floor_id}, has been deleted successfully..!"


@app.get("/org/{org_id}/getFloor", dependencies=[Depends(JWTBearer())], tags=["Org"])
async def get_floor(org_id: int, db: Session = Depends(get_db)):
    org_floor = db.query(models.Floor).filter(
        models.Floor.org_id == org_id).all()

    if org_floor is None:
        raise HTTPException(
            status_code=404,
            detail=f" The Org with given id :{org_id} does not exists..!"
        )

    return org_floor


@app.get("/org/{org_id}/getSites", dependencies=[Depends(JWTBearer())], tags=["Org"])
async def get_sites(org_id: int, db: Session = Depends(get_db)):
    org_check = db.query(models.Floor).filter(models.Floor.org_id == org_id).first()
    if org_check is None:
        raise HTTPException(
            status_code=404,
            detail=f" The Org with given id :{org_id} does not exists..!"
        )
    get_site = db.query(models.Floor.Manage_Site_Id, models.Floor.Manage_Site_Name).distinct().all()

    return get_site


@app.post("/org/{org_id}/{floor_id}/createZoneRoom", response_model=schemas.ZoneRoomBase,
          dependencies=[Depends(JWTBearer())], tags=["Org"])
async def create_zone_room(org_id: int, floor_id: int, zone: ZoneRoomBase, db: Session = Depends(get_db)):
    zone_model = models.ZoneRoom()

    zone_model.Ext_Boundary_Points = zone.Ext_Boundary_Points
    zone_model.Ext_Floor_Id = zone.Ext_Floor_Id
    zone_model.Ext_Room_Id = zone.Ext_Room_Id
    zone_model.Ext_Room_Name = zone.Ext_Room_Name
    zone_model.Ext_Zone_Id = zone.Ext_Zone_Id
    zone_model.Ext_Zone_Name = zone.Ext_Zone_Name
    zone_model.Ext_Zone_Room_Name = zone.Ext_Zone_Room_Name
    zone_model.floor_id = floor_id
    zone_model.org_id = org_id

    db.add(zone_model)
    db.commit()
    db.refresh(zone_model)
    return zone


@app.delete("/org/{org_id}/{floor_id}/deleteZoneRoom/{zone_room_id}", dependencies=[Depends(JWTBearer())], tags=["Org"])
async def delete_zone_room(org_id: int, floor_id: int, zone_room_id=int, db: Session = Depends(get_db)):
    org_floor_zone = db.query(models.ZoneRoom).filter(models.ZoneRoom.org_id == org_id,
                                                      models.ZoneRoom.floor_id == floor_id,
                                                      models.ZoneRoom.id == zone_room_id).first()

    if org_floor_zone is None:
        raise HTTPException(
            detail=f" The org id: {org_id} with given floor id : {floor_id} does not exists..!",
            status_code=404
        )
    else:
        db.query(models.ZoneRoom).filter(models.ZoneRoom.org_id == org_id,
                                         models.ZoneRoom.floor_id == floor_id,
                                         models.ZoneRoom.id == zone_room_id).delete()
    db.commit()
    return f" The ZoneRoom {zone_room_id} with org id: {org_id} and floor id: {floor_id} has been deleted " \
           f"successfully..! "


@app.get("/org/{org_id}/{floor_id}/getZoneRooms", dependencies=[Depends(JWTBearer())], tags=["Org"])
async def get_zone_rooms(org_id: int, floor_id: int, db: Session = Depends(get_db)):
    org_floor_zone = db.query(models.ZoneRoom).filter(models.ZoneRoom.org_id == org_id,
                                                      models.ZoneRoom.floor_id == floor_id).all()

    if org_floor_zone is None:
        raise HTTPException(
            status_code=404,
            detail=f"The ZoneRoom with org id: {org_id} and  floor id : {floor_id} does not exists..!"
        )

    return org_floor_zone


@app.get("/org/{org_id}/{site_id}/getBuildings", dependencies=[Depends(JWTBearer())], tags=["Org"])
async def Read_Buildings(org_id: str, site_id: str, db: Session = Depends(get_db)):
    org_site_check = db.query(models.Floor).filter(models.Floor.org_id == org_id,
                                                   models.Floor.Manage_Site_Id == site_id).first()

    if org_site_check is None:
        raise HTTPException(
            status_code=404,
            detail=f" The Building with given org id : {org_id} and site_id {site_id} does not exists..!"
        )

    get_building = db.query(models.Floor.Manage_Building_Id,
                            models.Floor.Manage_Building_Name
                            ).filter(models.Floor.Manage_Site_Id == site_id).distinct().all()

    return get_building


'''

User Object

'''


@app.get("/user", tags=["user"])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.post("/user/", tags=["user"])
async def create_new_user(user: UserSchema, db: Session = Depends(get_db)):
    new_user = models.User()
    new_user.name = user.name
    new_user.username = user.username
    new_user.pwd_hash = user.pwd_hash
    new_user.role = user.role

    try:
        db.add(new_user)
        db.commit()
        return f' New user added successfully..!'
    except exc.IntegrityError:
        db.rollback()
        return f" The user with given username already exists..!"


@app.get("/user/getUserCredentials", tags=["user"])
def get_user_credentials(username: str, db: Session = Depends(get_db)):
    user_check = db.query(models.User).filter(models.User.username == username)

    if user_check is None:
        raise HTTPException(
            detail=f" User with given username : {username} does not exists..!",
            status_code=404
        )
    get_cred = db.query(models.User.username, models.User.id, models.User.pwd_hash, models.User.role, models.User.name) \
        .filter(models.User.username == username).all()
    return get_cred


@app.put("/user/setUserCredentials", tags=["user"])
async def set_user_credentials(username: str, pwd_hash: str, user: SetUserCredentialsSchema,
                               db: Session = Depends(get_db)):
    set_user = db.query(models.User).filter(models.User.username == username).first()

    if set_user is None:
        raise HTTPException(
            detail=f" User with given username : {username} does not exists..!",
            status_code=404
        )

    check_pwd = db.query(models.User).filter(pwd_hash == models.User.pwd_hash).first()

    if not check_pwd:
        set_user.name = user.name
        set_user.pwd_hash = user.pwd_hash
        set_user.role = user.role
    else:
        return f' User is already having password..!'

    db.add(set_user)
    db.commit()

    return user


@app.post("/User/{username}/validateCredential/{hash}", tags=["user"])
async def user_validate(user: ValidateCredentialSchema = Body(...), db: Session = Depends(get_db)):
    def check_user(data: ValidateCredentialSchema):
        user_check = db.query(models.User).filter(models.User.username == data.username,
                                                  models.User.pwd_hash == data.pwd_hash).first()
        if not user_check:
            return False
        return True

    if check_user(user):
        return signJWT(user.username)
    return {
        "error": "Invalid pwd_hash submitted...!"
    }


'''
dataCollection API

'''


@app.get("/getSessions/{username}", dependencies=[Depends(JWTBearer())], tags=["Data Collection"])
async def getSessions(username: str, db: Session = Depends(get_db)):
    user_check = db.query(models.DCSessions.id).filter(models.DCSessions.username == username).all()

    if user_check is None:
        raise HTTPException(
            status_code=404,
            detail=f" The Session with given username :{username} does not exists..!"
        )
    return db.query(models.DCSessions).all()


@app.delete("/deleteSession/{dcsession_id}", dependencies=[Depends(JWTBearer())], tags=["Data Collection"])
async def delete_session(dcsession_id: int, db: Session = Depends(get_db)):
    session_check = db.query(models.DCSessions).filter(models.DCSessions.id == dcsession_id).first()

    if session_check is None:
        raise HTTPException(
            status_code=404,
            detail=f" The session with id: {dcsession_id} does not exists..!"
        )

    db.query(models.DCSessions).filter(models.DCSessions.id == dcsession_id).delete()
    db.commit()
    return f" The session with given id  {dcsession_id}, has been deleted successfully..!"


def format_tag_ids(tag_ids):
    if tag_ids:
        tag_ids = tag_ids.replace(" ", "")
        tag_ids = tag_ids[:-1] if tag_ids[-1] == "," else tag_ids
        tag_ids = tag_ids.lower()

    return tag_ids


@app.get("/initializeSession/{dataServer_id}/{username}/{org_id}/{floor_id}/{zone_room_id}/{tag_ids}/{session_name}",
         dependencies=[Depends(JWTBearer())], tags=["Data Collection"])
async def initializeSession(dataServer_id: int, username: str, org_id: int,
                            floor_id: int, zone_room_id: int, tag_ids: str, session_name: str,
                            db: Session = Depends(get_db)):
    org_name = db.query(models.Org.Manage_Org_Name).filter(models.Org.id == org_id).one_or_none()
    org_name = org_name[0]

    if org_name is None:
        raise HTTPException(
            detail=f" The organization with given id: {org_id} does not exists..!",
            status_code=404
        )

    floor_name = db.query(models.Floor.Manage_Floor_Name).filter(models.Floor.id == floor_id).one_or_none()

    if floor_name is None:
        raise HTTPException(
            detail=f" The organization with given floor id: {floor_id} does not exists..!",
            status_code=404

        )

    server_address = db.query(models.DataServer.address).filter(models.DataServer.id == dataServer_id).one_or_none()

    if server_address is None:
        raise HTTPException(
            detail=f" The server with given  server id: {dataServer_id} does not exists..!",
            status_code=404
        )
    session_model = models.DCSessions()
    session_model.dataServer_id = dataServer_id
    session_model.username = username
    session_model.org_id = org_id
    session_model.floor_id = floor_id
    session_model.zone_room_id = zone_room_id
    session_model.tag_ids = format_tag_ids(tag_ids)
    session_model.session_name = session_name

    db.add(session_model)
    db.commit()

    dcsession_id = db.query(models.DCSessions).filter(models.DCSessions.id).first()

    URL = f"http://{server_address.address}/initialize-session".format(server_address=server_address)

    payload = {
        "org_name": org_name,
        "session_uid": dcsession_id.id,
        "tag_ids": format_tag_ids(tag_ids),
        "floor": floor_name.Manage_Floor_Name,
    }

    async def task():
        async with httpx.AsyncClient() as client:
            result = await client.get(URL, params=payload)
            print(result)

    await task()

    return session_model.id


@app.get("/startDataCollection/{dcsession_id}", dependencies=[Depends(JWTBearer())], tags=["Data Collection"])
async def startDataCollection(org_id: int, dcsession_id: int, db: Session = Depends(get_db)):
    dcsession_id = db.query(models.DCSessions).filter(models.DCSessions.id == dcsession_id).one_or_none()

    if dcsession_id is None:
        raise HTTPException(
            detail=f" The session with given  session id: {dcsession_id} does not exists..!",
            status_code=404
        )
    org_name = db.query(models.Org.Manage_Org_Name).filter(models.Org.id == org_id).one_or_none()
    org_name = org_name[0]

    if org_name is None:
        raise HTTPException(
            detail=f" The organization with given id: {org_id} does not exists..!",
            status_code=404
        )

    current_zone = db.query(models.DCSessions.zone_room_id).filter(
        models.DCSessions.id == dcsession_id.id).one_or_none()
    current_zone = current_zone[0]

    payload = {
        "org_name": org_name,
        "session_uid": dcsession_id.id,
        "current_zone": current_zone,
    }

    server_address = db.query(models.DataServer).filter(models.DataServer.org_id == org_id).one_or_none()

    URL = f"http://{server_address.address}/start-data-collection".format(server_address=server_address)

    async def task():
        async with httpx.AsyncClient() as client:
            result = await client.get(URL, params=payload)
            print(result)

    await task()

    return f'Data Collection has been started..!'


@app.get("/checkDataCollection/{dcsession_id}",dependencies=[Depends(JWTBearer())], tags=["Data Collection"])
async def checkDataCollection(org_id: int, dcsession_id: int, db: Session = Depends(get_db)):
    dcsession_id = db.query(models.DCSessions).filter(models.DCSessions.id == dcsession_id).one_or_none()

    if dcsession_id is None:
        raise HTTPException(
            detail=f" The session with given  session id: {dcsession_id} does not exists..!",
            status_code=404
        )
    org_name = db.query(models.Org.Manage_Org_Name).filter(models.Org.id == org_id).one_or_none()
    org_name = org_name[0]

    if org_name is None:
        raise HTTPException(
            detail=f" The organization with given id: {org_id} does not exists..!",
            status_code=404
        )

    payload = {
        "org_name": org_name,
        "session_uid": dcsession_id.id,
    }
    server_address = db.query(models.DataServer).filter(models.DataServer.org_id == org_id).one_or_none()
    URL = f"http://{server_address.address}/check-data-collection".format(server_address=server_address)

    async def task():
        async with httpx.AsyncClient() as client:
            result = await client.get(URL, params=payload)
            print(result)

    await task()

    return


@app.get("/stopDataCollection/{dcsession_id}", dependencies=[Depends(JWTBearer())], tags=["Data Collection"])
async def stopDataCollection(org_id: str, dcsession_id: int, db: Session = Depends(get_db)):
    dcsession_id = db.query(models.DCSessions).filter(models.DCSessions.id == dcsession_id).one_or_none()

    if dcsession_id is None:
        raise HTTPException(
            detail=f" The session with given  session id: {dcsession_id} does not exists..!",
            status_code=404
        )
    org_name = db.query(models.Org.Manage_Org_Name).filter(models.Org.id == org_id).one_or_none()
    org_name = org_name[0]

    if org_name is None:
        raise HTTPException(
            detail=f" The organization with given id: {org_id} does not exists..!",
            status_code=404
        )

    payload = {
        "org_name": org_name,
        "session_uid": dcsession_id.id,
    }

    server_address = db.query(models.DataServer).filter(models.DataServer.org_id == org_id).one_or_none()

    URL = f"http://{server_address.address}/stop-data-collection".format(server_address=server_address)

    async def task():
        async with httpx.AsyncClient() as client:
            result = await client.get(URL, params=payload)
            print(result)

    await task()

    return


if __name__ == '__main__':
    uvicorn.run(app, port=8050, host="0.0.0.0")
