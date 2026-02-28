from fastapi import APIRouter, HTTPException, Depends
from app.schemas.payment_schema import Payment, VerifyPayment
from app.utils.depedencies import role_required
from app.utils.create_ticket_pdf import create_ticket_pdf
from app.utils.unique_ticket_number_generator import generate_ticket_number
from app.db.database import db
from bson import ObjectId
from datetime import datetime, time, timedelta, timezone
from fastapi.responses import FileResponse 
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

router = APIRouter(prefix='/payment', tags=['Payment'])

mail_conf = ConnectionConfig(
    MAIL_USERNAME = "sandeshshinde43210@gmail.com",
    MAIL_PASSWORD = "sfay yaxv bwfy ujht",
    MAIL_FROM = "sandeshshinde43210@gmail.com",
    MAIL_FROM_NAME="Travello",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

@router.post('/create-payment')
async def createPayment(payment: Payment, user=Depends(role_required('user'))):
    # 1. Access attributes using dot notation
    booking_id = payment.booking_id 

    booking = await db.bookings.find_one({
        "_id": ObjectId(booking_id)
    })

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    amount = booking["total_price"]

    paymentAlreadyDone = await db.payments.find_one({
        "booking_id" : booking_id,
        "status" : "COMPLETED"
    })

    if paymentAlreadyDone : 
        raise HTTPException(status_code=400, detail="Payment already done")

    # 2. Insert the payment
    new_payment = await db.payments.insert_one({
        "booking_id": booking_id,
        "amount": amount,
        "status": "COMPLETED", # Recommended: track payment status
        "createdAt": datetime.now(timezone.utc)
    })

    payment_id = new_payment.inserted_id

    # 3. CRITICAL: Update the booking in the database
    await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"payment_id": str(payment_id),
                  "status" : "CONFIRMED",
                  "updatedAt": datetime.now(timezone.utc)}}
    )

    return {
        "success": True,
        "message": "Payment Done and Email send",
        "payment_id": str(payment_id),
        "amount" : amount
    }

@router.post('/verify-payment-and-create-ticket')
async def verify_payment(payment: VerifyPayment):
    payment_dict = payment.model_dump()
    payment_id = payment_dict["payment_id"]
    booking_id = payment_dict["booking_id"]

    # 1. Verify Payment
    payment_record = await db.payments.find_one({
        "_id": ObjectId(payment_id),
        "status": "COMPLETED"
    })

    if not payment_record:
        raise HTTPException(status_code=400, detail="Payment not done yet")
    
    # 2. Fetch the Booking Data (Needed for the PDF)
    booking_data = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking_data:
        raise HTTPException(status_code=404, detail="Booking not found")
    
     # 2. FETCH USER INFO (Naya Step)
    user_id = booking_data.get("user_id")
    # Agar user_id string hai toh ObjectId mein convert karein
    user_data = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found for this booking")

    user_email = user_data.get("email") # Jo bhi field name aapne DB mein rakha ho
    user_name = user_data.get("name")

    # 3. Generate Ticket Info
    ticket_no = generate_ticket_number()
    
    # Add ticket_no to the data so the PDF generator has it
    booking_data["ticket_no"] = ticket_no 

    try:
        # 4. Create PDF
        file_path = create_ticket_pdf(booking_data)

        try:
           message = MessageSchema(
            subject=f"Ticket Confirmed - {ticket_no}",
            recipients=[user_email], # DB se nikala hua email
            body=f"Hi {user_name}, Your ticket is successfully generated.",
            attachments=[file_path],
            subtype=MessageType.html
            )
           fm = FastMail(mail_conf)
           await fm.send_message(message)
        except Exception as e:
         print(f"Email sending failed: {e}")
        
        # 5. Atomic Update (One call to rule them all)
        await db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {
                "$set": {
                    "ticket_no": ticket_no,
                    "ticket_url": file_path,
                    "updated_at": datetime.utcnow() # Good practice
                }
            }
        )
    except Exception as e:
        # Log the error properly
        print(f"Failed to generate ticket: {e}")
        raise HTTPException(status_code=500, detail="Error generating ticket file")

    return {
        "success": True,
        "message": "Ticket created successfully",
        "ticket_url": file_path # Helpful for the frontend
    }


import os

@router.get('/ticket/download/{booking_id}')
async def downloadTicket(booking_id: str):
    # 1. Database se booking dhoondhein
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    file_path = booking.get("ticket_url")

    # 2. Check kijiye ki file disk par exist karti hai ya nahi
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Ticket file not found on server")

    # 3. Seedha FileResponse bhejiye (No JSON wrapper)
    return FileResponse(
        path=file_path,
        media_type='application/pdf',
        filename=f"Ticket_{booking_id}.pdf" # Browser isi naam se save karega
    )





