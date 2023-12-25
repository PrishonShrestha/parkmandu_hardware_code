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
            update_exiting_vehicle(rfid)
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
        vehicle_entry(rfid)
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
    slot_ref = db.collection('parking_info').document('79yuoUXhcRdMJ32F3yyp').collection('vehicle_details').where('status', '==', 'incomplete').stream()
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


def vehicle_entry(rfid):
    # Assuming you have a Firestore collection for vehicle details
    # parking_info = db.collection('parking_info')
    parking_info = db.collection('parking_info').document('79yuoUXhcRdMJ32F3yyp').collection('vehicle_details')

    # Add a document with vehicle details
    parking_info.add({
        'userid': rfid,
        'parkingid': '79yuoUXhcRdMJ32F3yyp',
        'entry_time': firestore.SERVER_TIMESTAMP,
        'status': 'incomplete',
        # Add other details as needed
    })
    print("Vehicle details entered in Firestore.")

def update_exiting_vehicle(rfid):
    # Update the parking status to "completed" in Firestore
    parking_doc_ref = db.collection('parking_info').document('79yuoUXhcRdMJ32F3yyp').collection('vehicle_details')
    query = parking_doc_ref.where('userid', '==', rfid).where('status', '==', 'incomplete')
    # query = parking_doc_ref.where(
    #     'userid', '==', rfid,
    #     filter=('status', '==', 'incomplete')
    # )
    matching_docs = query.stream()
    
    if matching_docs:
        print("Doc found")
        try:
            for doc in matching_docs:
                # print("Doc" +doc)
                doc.reference.update({
                    'status': 'completed',
                    'exit_time': firestore.SERVER_TIMESTAMP,
                    })
        except Exception as e:
            print(f"Error updating document: {e}")
        print("Parking status updated to 'completed' for RFID {}.".format(rfid))
        occupied_slot_count_and_update()
    else:
        print("No data found")

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
