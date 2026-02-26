from fastapi import APIRouter, HTTPException,Depends
from app.db.database import db
from app.schemas.bus_schema import BusRegister, BusUpdatee
from app.utils.depedencies import role_required
from bson import ObjectId
from datetime import datetime, timezone


router = APIRouter(prefix='/bus', tags=["Bus"])

@router.post('/register')
async def registerBus(bus: BusRegister, admin=Depends(role_required('admin'))):
    bus_dict = bus.model_dump()

    # 1. Insert into MongoDB
    createdBus = await db.buses.insert_one(bus_dict)

    # 2. Get the string ID
    bus_id = str(createdBus.inserted_id)

    # 3. Add the ID to your dictionary so the frontend gets it
    bus_dict["_id"] = bus_id

    return {
        "success": True,
        "message": "Bus created successfully",
        "bus": bus_dict,  # Use the DICTIONARY here, not 'createdBus'
        "bus_id": bus_id
    }


@router.get('/get-all-bus')
async def getAllBuses(admin=Depends(role_required('admin'))) :
    cursor =  db.buses.find()
    buses = await cursor.to_list()

    for bus in buses : 
        bus["_id"] = str(bus["_id"])

    return {
        "success" : True,
        "message" : "Fetched buses successfully",
        "bus_data" : buses
}


@router.patch('/update/{bus_id}')
async def updateBus(bus_id: str, bus : BusUpdatee, admin=Depends(role_required('admin'))):
    update_data = {
        k:v for k, v in bus.model_dump().items() if v is not None
    }

    if not update_data : 
        raise HTTPException(status_code=400, detail="No fields provided to update")


    result = await db.buses.update_one(
        {
            "_id" : ObjectId(bus_id)
        },
        {
            "$set" : update_data
        }
    )

 

    return {
        "success" : True,
        "message" : "Successfully updated the bus data",

    }

@router.delete('/delete/{bus_id}')
async def deleteBus(bus_id:str, admin=Depends(role_required('admin'))) : 
    result = await db.buses.delete_one({
        "_id" : ObjectId(bus_id)
    })

    if result.deleted_count == 0 : 
        raise HTTPException(status_code=400, detail="Bus not found")
    
    return {
        "success" : True,
        "message" : "Successfully deleted bus"
    }

@router.patch('/assign-route/{bus_id}')
async def assignRouteToBus(bus_id: str, route_data: dict, admin=Depends(role_required('admin'))):
    routeId = route_data.get('route_id')

    if(not routeId):
        raise HTTPException(status_code=400, detail="Route id not provided")

    result = await db.buses.update_one({
        "_id": ObjectId(bus_id),
        
    }, {
        "$set": {"route_id": routeId, "updatedAt": datetime.now(timezone.utc)}
    })

    if(result.modified_count == 0):
        raise HTTPException(status_code=400, detail="Failed to update route id")
    
    return {
        "success" : True,
        "message" : "Successfully update the route id"
    }