from fastapi import APIRouter, HTTPException, Depends
from app.schemas.trip_schema import TripCreate, SearchTrip, UpdateTrip
from app.utils.depedencies import role_required
from app.db.database import db
from bson import ObjectId
from datetime import datetime, time, timedelta

router = APIRouter(prefix='/trip', tags=["Trip"])

# -------------------------
# CREATE TRIP
# -------------------------
@router.post('/create')
async def createTripForBus(trip: TripCreate, admin=Depends(role_required('admin'))):
    trip_dict = trip.model_dump()

    bus = await db.buses.find_one({"_id": ObjectId(trip_dict["bus_id"])})
    if not bus:
        raise HTTPException(status_code=400, detail="Bus not found")

    # Convert date to datetime
    mongo_date = datetime.combine(trip_dict["date"], time.min)

    dep_time = trip_dict["departure_time"]
    arr_time = trip_dict["arrival_time"]
    if isinstance(dep_time, time):
        dep_time = dep_time.strftime("%H:%M")
    if isinstance(arr_time, time):
        arr_time = arr_time.strftime("%H:%M")

    # Insert trip
    createTrip = await db.trips.insert_one({
        "bus_id": ObjectId(trip_dict["bus_id"]),
        "route_id": ObjectId(bus["route_id"]),  # ensure this is ObjectId in DB!
        "date": mongo_date,
        "departure_time": dep_time,
        "arrival_time": arr_time,
        "price": trip_dict["price"],
        "total_seats": bus["total_seats"],
        "available_seats": bus["total_seats"],
        "isActive": True
    })

    return {"success": True, "message": "Trip created", "trip_id": str(createTrip.inserted_id)}

# -------------------------
# SEARCH TRIPS
# -------------------------
@router.get('/get-all-trips')
async def getAllSearchTrips(sTrip: SearchTrip = Depends()):
    sTrip_dict = sTrip.model_dump()

    # Find route
    routeExist = await db.routes.find_one({
        "source_city_id": sTrip_dict["from_city_id"],
        "destination_city_id": sTrip_dict["to_city_id"]
    })
    if not routeExist:
        raise HTTPException(status_code=404, detail="No route found")

    # Date range for the query
    start_date = datetime.combine(sTrip_dict["date"], time.min)
    end_date = start_date + timedelta(days=1)

    pipeline = [
        {
            "$match": {
                "route_id": ObjectId(routeExist["_id"]),  # Must be ObjectId
                "date": {"$gte": start_date, "$lt": end_date},
                "isActive": True
            }
        },
        {
            "$lookup": {
                "from": "buses",
                "localField": "bus_id",
                "foreignField": "_id",
                "as": "bus_details"
            }
        },
        {"$unwind": "$bus_details"},
       
        {
            "$lookup": {
                "from": "routes",
                "localField": "route_id",
                "foreignField": "_id",
                "as": "route_details"
            }
        },
        {"$unwind": "$route_details"},
        {
        # Use $addFields to keep arrival_time, price, seats, etc.
        "$addFields": {
            "bus_name": "$bus_details.name",
            "bus_type": "$bus_details.bus_type",
            "route_name": "$route_details.route_name"
        }
    },
    
    ]

    trips = await db.trips.aggregate(pipeline).to_list(None)

    # Convert ObjectIds to string
    for trip in trips:
        trip["_id"] = str(trip["_id"])
        trip["bus_id"] = str(trip["bus_id"])
        trip["route_id"] = str(trip["route_id"])
        trip["bus_details"]["_id"] = str(trip["bus_details"]["_id"])
        trip["route_details"]["_id"] = str(trip["route_details"]["_id"])

    return {"success": True, "message": "Trips fetched", "trip_data": trips}

# -------------------------
# GET ALL TRIPS (USERS)
# -------------------------
@router.get('/all-trips')
async def getAllTrips(admin=Depends(role_required('admin'))):
    trips = await db.trips.find().to_list(None)
    enriched_trips = []

    for trip in trips:
        trip["_id"] = str(trip["_id"])
        trip["bus_id"] = str(trip["bus_id"])
        trip["route_id"] = str(trip["route_id"])

        # Fetch bus details using bus_id
        bus = await db.buses.find_one({"_id": ObjectId(trip["bus_id"])})
        if bus:
            bus["_id"] = str(bus["_id"])
            trip["bus_details"] = bus
        else:
            trip["bus_details"] = None

        enriched_trips.append(trip)

    return {"success": True, "message": "All trips fetched", "trip_data": enriched_trips}


@router.patch('/update/{trip_id}')
async def updateTrip(trip_id: str, trip: UpdateTrip, admin=Depends(role_required('admin'))):
    trip_dict = trip.model_dump(exclude_none=True)

    update_data = {
        k:v for k, v in trip_dict.items() if v is not None
    }

    if not update_data : 
        raise HTTPException(status_code=400, detail="No fields provide to update")
    
    if "date" in update_data : 
        update_data["date"] = datetime.combine(update_data["date"], datetime.min.time())

    
    if "departure_time" in update_data:
         update_data["departure_time"] = update_data["departure_time"].strftime("%H:%M")

    if "arrival_time" in update_data:
         update_data["arrival_time"] = update_data["arrival_time"].strftime("%H:%M")

    trip_exist = await db.trips.find_one({
        "_id" : ObjectId(trip_id)
    })

    if(not trip_exist) : 
        raise HTTPException(status_code=400, detail="Trip not found")
    
    result = await db.trips.update_one({
        "_id" : ObjectId(trip_id)
    }, {
        "$set": update_data
    })

    return {
        "success": True,
        "message" : "Successfully updated trip"
    }
 


@router.delete('/delete/{trip_id}')
async def deleteTrip(trip_id: str, admin=Depends(role_required('admin'))):

    tripExist = await db.trips.find_one({
        "_id": ObjectId(trip_id)
    })

    if(not tripExist) : 
        raise HTTPException(status_code=400, detail="Trip not found")
    
    result = await db.trips.delete_one({
        "_id" : ObjectId(trip_id)
    })


    return {
        "success" : True,
        "message" : "Successfully deleted trip"
    }