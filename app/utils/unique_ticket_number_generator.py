import random

def generate_ticket_number() : 
    return "TKT" + str(random.randint(100000,999999))