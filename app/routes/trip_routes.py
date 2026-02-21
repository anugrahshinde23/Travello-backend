from fastapi import APIRouter, HTTPException, Depends
from app.schemas.trip_schema import TripCreate, SearchTrip
from app.utils.depedencies import role_required
from app.db.database import db
from bson import ObjectId
from datetime import datetime, time , date

router = APIRouter(prefix='/trip', tags=["Trip"] )



@router.post('/create')
async def createTripForBus(trip: TripCreate, admin=Depends(role_required('admin'))):
    trip_dict = trip.model_dump()
    
    # 1. Fetch the bus details
    bus = await db.buses.find_one({
        "_id": ObjectId(trip_dict["bus_id"])
    })

    if not bus:
        raise HTTPException(status_code=400, detail="Bus not found")
    
    # 2. CONVERT DATA TYPES FOR MONGODB
    # Convert 'date' to 'datetime' (MongoDB doesn't support 'date' alone)
    mongo_date = datetime.combine(trip_dict["date"], time.min)
    
    # Convert 'time' objects to strings (or leave as datetime if preferred)
    # If they are already strings from Pydantic, you can skip .strftime()
    dep_time = trip_dict["departure_time"]
    arr_time = trip_dict["arrival_time"]
    
    if isinstance(dep_time, time):
        dep_time = dep_time.strftime("%H:%M")
    if isinstance(arr_time, time):
        arr_time = arr_time.strftime("%H:%M")

    # 3. INSERT INTO DB
    createTrip = await db.trip.insert_one({
        "bus_id": trip_dict["bus_id"],
        "route_id": bus["route_id"],
        "date": mongo_date,            # Fixed: Now a datetime object
        "departure_time": dep_time,    # Fixed: Now a string or datetime
        "arrival_time": arr_time,      # Fixed: Now a string or datetime
        "price": trip_dict["price"],
        "total_seats": bus["total_seats"],
        "available_seats": bus["total_seats"]
    })

    return {
        "success": True,
        "message": "Successfully created trip", # Changed 'route' to 'trip' for clarity
        "trip_id": str(createTrip.inserted_id)
    }
    

from bson import ObjectId

@router.get('/get-all-trips')
async def getAllSearchTrips(sTrip: SearchTrip):
    sTrip_dict = sTrip.model_dump()

    # 1. First, find the route to get the correct route_id
    routeExist = await db.routes.find_one({
        "source_city_id": sTrip_dict["from_city_id"],
        "destination_city_id": sTrip_dict["to_city_id"]
    })

    if not routeExist:
        raise HTTPException(status_code=404, detail="No route found between these cities")

    query_date = datetime.combine(sTrip_dict["date"], time.min)

    # 2. Use Aggregation to "Join" Bus and Route data
    pipeline = [
        {
            "$match": {
                "route_id": str(routeExist["_id"]),
                "date": query_date,
                "isActive": True
            }
        },
        {
            # Join with Buses collection
            "$lookup": {
                "from": "buses",
                "localField": "bus_id",      # Field in 'trips'
                "foreignField": "_id",       # Note: if your bus_id in trip is a String, 
                                             # you might need to convert it to ObjectId first
                "as": "bus_details"
            }
        },
        { "$unwind": "$bus_details" },       # Turn array into an object
        {
            # Join with Routes collection
            "$lookup": {
                "from": "routes",
                "localField": "route_id",
                "foreignField": "_id",
                "as": "route_details"
            }
        },
        { "$unwind": "$route_details" }
    ]

    cursor = db.trips.aggregate(pipeline)
    trips = await cursor.to_list(None)

    # 3. Clean up IDs for JSON response
    for trip in trips:
        trip["_id"] = str(trip["_id"])
        trip["bus_id"] = str(trip["bus_id"])
        trip["route_id"] = str(trip["route_id"])
        # Clean up nested IDs too
        trip["bus_details"]["_id"] = str(trip["bus_details"]["_id"])
        trip["route_details"]["_id"] = str(trip["route_details"]["_id"])

    return {
        "success": True,
        "message": "Trips fetched with full details",
        "trip_data": trips
    }

    


