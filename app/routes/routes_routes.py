from fastapi import APIRouter, HTTPException, Depends
from app.schemas.routes_schema import Cities, CityUpdate, Routes, RoutesUpdate
from app.db.database import db
from app.utils.depedencies import role_required
from bson import ObjectId

router = APIRouter(prefix='/city', tags=["City"])

@router.post('/add')
async def addCity(city: Cities, admin=Depends(role_required('admin'))):
    city_dict = city.model_dump()

    createRoute = await db.cities.insert_one(city_dict)

    city_id = str(createRoute.inserted_id)

    city_dict["_id"] = city_id

    return {
        "success" : True,
        "message" : "City added successfully",
        "city_data": city_dict,
        "city_id": city_id
    }


@router.get('/get-all-cities')
async def getAllCities():
    cursor = db.cities.find()
    cities = await cursor.to_list()

    for city in cities : 
        city["_id"] = str(city["_id"])
    
    return {
        "success" : True,
        "message" : "Fetched cities successfully",
        "city_data": cities



    }

@router.patch('/update/{city_id}')
async def updateCity(city_id: str, city: CityUpdate, admin=Depends(role_required('admin'))) : 
    update_data = {
        k:v for k , v in city.model_dump().items() if v is not None
    }

    if not update_data : 
        raise HTTPException(status_code=400, detail="No fields provide to update")
    
    result = await db.cities.update_one({
        "_id" : ObjectId(city_id)
    },{
        "$set": update_data
    })

    return {
        "success" : True,
        "message": "Successfully updated the city data"
    }

@router.delete('/delete/{city_id}')
async def deleteCity(city_id: str, admin=Depends(role_required('admin'))) : 
    result = await db.cities.delete_one({
        "_id": ObjectId(city_id)
    })

    if result.deleted_count == 0 : 
        raise HTTPException(status_code=400, detail="City not found")
    
    return {
        "success": True,
        "message" : "City deleted successfully"
    }



@router.post('/route/add')
async def addRoute(route:Routes, admin=Depends(role_required('admin'))):
    route_dict = route.model_dump()

    if(route_dict["source_city_id"]  == route_dict["destination_city_id"]):
        raise HTTPException(status_code=400, detail="Source and destination cant be same ")
    
    exitingRoute = await db.routes.find_one({
        "source_city_id" : route_dict["source_city_id"],
        "destination_city_id": route_dict["destination_city_id"]
    })

    if exitingRoute : 
        raise HTTPException(status_code=400, detail="Route already added")
    
    createRoute = await db.routes.insert_one(route_dict)

    print(createRoute)

    route_id = str(createRoute.inserted_id)
    
    route_dict["_id"] = route_id

    return {
        "success" : True,
        "message" : "Successfully added route",
        "route_data" : route_dict
    }



@router.get('/route/get-all-routes')
async def getRoutes():
    pipeline = [
        # 1. Join with cities for SOURCE
        {
            "$lookup": {
                "from": "cities",
                "let": {"source_id": "$source_city_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", {"$toObjectId": "$$source_id"}]}}}
                ],
                "as": "source_details"
            }
        },
        # 2. Join with cities for DESTINATION
        {
            "$lookup": {
                "from": "cities",
                "let": {"dest_id": "$destination_city_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", {"$toObjectId": "$$dest_id"}]}}}
                ],
                "as": "dest_details"
            }
        },
        # 3. $lookup returns an array; extract the first matching city object
        {"$addFields": {
            "source_city": {"$arrayElemAt": ["$source_details", 0]},
            "destination_city": {"$arrayElemAt": ["$dest_details", 0]}
        }},
        # 4. (Optional) Remove the temporary arrays
        {"$project": {"source_details": 0, "dest_details": 0}}
    ]

    # Run the aggregation
    routes = await db.routes.aggregate(pipeline).to_list(length=None)

    # Convert ObjectIds to strings for JSON compatibility
    for route in routes:
        route["_id"] = str(route["_id"])
        if "source_city" in route:
            route["source_city"]["_id"] = str(route["source_city"]["_id"])
        if "destination_city" in route:
            route["destination_city"]["_id"] = str(route["destination_city"]["_id"])

    return {
        "success": True,
        "message": "Fetched Routes successfully",
        "route_data": routes
    }



@router.patch('/route/update/{route_id}')
async def updateRoute(route_id:str ,route:RoutesUpdate, admin=Depends(role_required('admin'))):

    route_dict = route.model_dump()

    update_data = {
        k:v for k , v in route_dict.items() if v is not None
    }

    if not update_data : 
        raise HTTPException(status_code=400, detail="No fields provide to update")
    
    routeExist = await db.routes.find_one({
        "_id" : ObjectId(route_id)
    })

    if(not routeExist):
       raise HTTPException(status_code=400, detail="Route not found")
    
    result = await db.routes.update_one({
        "_id" : ObjectId(route_id)
    },{
        "$set": update_data
    })

    return {
        "success" : True,
        "message" : "Successfully updated route",
    }

@router.delete('/route/delete/{route_id}')
async def deleteRoute(route_id: str, admin=Depends(role_required('admin'))):

    routeExist = await db.routes.find_one({
        "_id": ObjectId(route_id)
    })

    if(not routeExist):
        raise HTTPException(status_code=400, detail="Route not found")
    
    result = await db.routes.delete_one({
        "_id" : ObjectId(route_id)
    })

    return {
        "success": True,
        "message": "Route deleted successfully"
    }