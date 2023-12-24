import serial
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore
# db = firestore.Client.from_service_account_json('path/to/your/credentials.json')
cred = credentials.Certificate("parkmandu-4e7f1-firebase-adminsdk-29t9t-0380fec4c2.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Adjust the port accordingly
ser = serial.Serial('COM5', 9600)

# Variables
total_space = 3
occupied_space = 0
free_space = 0


def process_data(data):
    
    occupied_slot_count_and_update()
    print(free_space)
    # Process the received data from Arduino
    parts = data.split(",")
    if len(parts) >=2:
        rfid = parts[0]
        status = parts[1]
        print(rfid),

        if status == "isEntering":
            if occupied_space < total_space :
                check_and_update_firestore(rfid)
            else:
                print("Parking full")

        elif status == "isExiting":
            update_parking_status(rfid)
            decrease_occupied_slot()
        else:
            print("Error")
    else:
        print("Invalid data format received from Arduino: {}".format(data))

def check_and_update_firestore(rfid):
    # Assuming you have a Firestore collection named 'rfid_cards'
    rfid_collection = db.collection('users')

    # Check if the RFID exists in Firestore
    rfid_doc = rfid_collection.document(rfid).get()

    if rfid_doc.exists:
        # RFID exists, perform actions
        open_gate()
        # increase_occupied_slot()
        enter_vehicle_detail(rfid)
        occupied_slot_count_and_update()
        print("RFID {} is registered. Access granted.".format(rfid))
    else:
        print("RFID {} not registered in Firestore. Access denied.".format(rfid))

def open_gate():
    # Implement your code to control the servo motor and open the gate
    print("Opening gate...")

def occupied_slot_count_and_update():
    # Variables
    global total_space
    global occupied_space
    global free_space
    slot_ref = db.collection('parking_info').document('79yuoUXhcRdMJ32F3yyp').collection('vechile_details').where('status', '==', 'incomplete').stream()
    # Count the number of matching documents
    count = len(list(slot_ref))
    print(f'number of occupied slots {count}')
    # Set slot details
    occupied_space = count
    free_space = total_space-occupied_space

    # Update slot details to firestore
    parking_ref = db.collection('parkings').document('79yuoUXhcRdMJ32F3yyp')

    query = parking_ref.update({
        'availableslots' : free_space,
        'occupiedslots' : occupied_space,
    })



def increase_occupied_slot():
    # Assuming you have a Firestore document for slot counts
    slot_doc_ref = db.collection('parkings').document('79yuoUXhcRdMJ32F3yyp')
    global occupied_space
    # Atomically increment the occupied slot count by 1
    # slot_doc_ref.update({'occupiedslots': firestore.Increment(1)})
    # occupied_space = occupied_space+1,
    print(f"Occupied slots: {occupied_space}")
    # free_space = total_space-occupied_space
    # slot_doc_ref.update({
    #     'occupiedslots': occupied_space, 
    #     'availableslots': free_space,
    #     })
    
def decrease_occupied_slot():
    # Assuming you have a Firestore document for slot counts
    slot_doc_ref = db.collection('parkings').document('79yuoUXhcRdMJ32F3yyp')

    # Atomically decrement the occupied slot count by 1
    # slot_doc_ref.update({'occupiedslots': firestore.Increment(-1)})
    occupied_space-=1,    
    print("Occupied slots: "+occupied_space)
    free_space = total_space-occupied_space
    slot_doc_ref.update({
        'occupiedslots': occupied_space, 
        'availableslots': free_space,
        })

def enter_vehicle_detail(rfid):
    # Assuming you have a Firestore collection for vehicle details
    # parking_info = db.collection('parking_info')
    parking_info = db.collection('parking_info').document('79yuoUXhcRdMJ32F3yyp').collection('vechile_details')

    # Add a document with vehicle details
    parking_info.add({
        'userid': rfid,
        'parkingid': '79yuoUXhcRdMJ32F3yyp',
        'entry_time': firestore.SERVER_TIMESTAMP,
        'status': 'incomplete',
        # Add other details as needed
    })
    print("Vehicle details entered in Firestore.")

def update_parking_status(rfid):
    # Update the parking status to "completed" in Firestore
    rfid_collection = db.collection('parking_info')
    rfid_doc_ref = rfid_collection.document(rfid)

    rfid_doc_ref.update({
        'status': 'completed',
        'exit_time': firestore.SERVER_TIMESTAMP,
        })
    print("Parking status updated to 'completed' for RFID {}.".format(rfid))


if __name__ == "__main__":
    try:
        while True:
            # Read data from Arduino
            arduino_data = ser.readline().decode().strip()

            # Process the received data
            process_data(arduino_data)
            

            time.sleep(1)  # Adjust the delay as needed
    except KeyboardInterrupt:
        ser.close()
        print("Serial port closed.")
