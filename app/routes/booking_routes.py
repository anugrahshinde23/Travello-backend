from fastapi import APIRouter, HTTPException, Depends
from app.schemas.booking_schema import Booking
from app.db.database import db
from app.utils.depedencies import role_required
from bson import ObjectId


router = APIRouter(prefix='/booking', tags=['Booking'])


# ✅ Seat layout
@router.get("/seat-layout/{trip_id}")
async def seat_layout(trip_id: str, user=Depends(role_required('user'))):

    trip = await db.trips.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(404, "Trip not found")

    bookings = await db.bookings.find({
        "trip_id": trip_id
    }).to_list(100)

    booked_seats = []

    for b in bookings:
        booked_seats.extend(b["seats"])

    return {
        "success": True,
        "message": "Successfully fetched seatLayout",
        "total_seats": trip["total_seats"],
        "booked_seats": booked_seats,
        "price": trip["price"]
    }


# ✅ Book seats
@router.post("/book")
async def book_seat(data: Booking, user=Depends(role_required('user'))):

    # Step 1 → Check already booked
    existing = await db.bookings.find({
        "trip_id": data.trip_id,
        "seats": {"$in": data.seats}
    }).to_list(10)

    if existing:
        raise HTTPException(400, "Some seats already booked")

    # Step 2 → Get trip
    trip = await db.trips.find_one({"_id": ObjectId(data.trip_id)})

    if not trip:
        raise HTTPException(404, "Trip not found")

    # Update the database directly
    update_result = await db.trips.update_one(
    {"_id": ObjectId(data.trip_id), "available_seats": {"$gte": len(data.seats)}},
    {"$inc": {"available_seats": -len(data.seats)}}
)

    if update_result.modified_count == 0:
     raise HTTPException(400, "Not enough seats available")


    # Step 3 → Calculate price
    total_amount = len(data.seats) * trip["price"]

    # Step 4 → Create booking
    booking_dict = {
        "user_id": user["user_id"],
        "trip_id": data.trip_id,
        "seats": data.seats,
        "total_price": total_amount,
        "status": "PENDING",
    }

    result = await db.bookings.insert_one(booking_dict)

    return {
        "success": True,
        "message": "Successfully booked",
        "booking_id": str(result.inserted_id),
        "total_amount": total_amount
    }

@router.get('/get-user-bookings')
async def getUserBookings(user=Depends(role_required('user'))) : 

    cursor = db.bookings.find({
        "user_id" : user["user_id"]
    })
    booking = await cursor.to_list()

    

    if(not booking) : 
       raise HTTPException(status_code=400, detail="Booking not found")


    for b in booking :
        b["_id"] = str(b["_id"])
    


    return {
        "success":True,
        "message" : "Successfully fetched user bookings",
        "booking" : booking
    }


@router.get('/get-all-bookings')
async def getAllBookings(user=Depends(role_required('admin'))) : 

    cursor = db.bookings.find()
    booking = await cursor.to_list()

    if(not booking) : 
        raise HTTPException(status_code=400, detail="Bookings not found")
    
    for b in booking : 
        b["_id"] = str(b["_id"])

    return {
        "success" : True,
        "message" : "Successfully fetched bookings",
        "bookings" : booking 
    }