import serial
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore
cred = credentials.Certificate("e:/College/Final Project/Arduino code/parkmandu-4e7f1-firebase-adminsdk-29t9t-492b5e53a3.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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

        if status == "isEntering":
            print("Card detected: "+rfid),
            if occupied_space < total_space :
                check_and_update_firestore(rfid)
            else:
                print("Parking full")
                displayMessage('Parking_full')
        elif status == "isExiting":
            update_exiting_vehicle(rfid)
        else:
            print("Error")
    else:
        print("Invalid data format received from Arduino: {}".format(data))

def check_and_update_firestore(rfid):
    rfid_collection = db.collection('users')

    # Check if the RFID exists in Firestore
    rfid_doc = rfid_collection.document(rfid).get()

    if rfid_doc.exists:
        open_gate()
        vehicle_entry(rfid)
        occupied_slot_count_and_update()
        print("RFID {} is registered. Access granted.".format(rfid))
    else:
        # send_message_to_arduino('N')
        displayMessage('Not_registered');
        print("RFID {} not registered in Firestore. Access denied.".format(rfid))
        
def displayMessage(message):
    if(message == 'Not_registered'):
        ser.write(b'N')
    elif(message == 'Parking_full'):
        ser.write(b'F')
def open_gate():
    print("Opening gate")
    ser.write(b'O')

def occupied_slot_count_and_update():
    # Variables
    global total_space
    global occupied_space
    global free_space
    slot_ref = db.collection('parking_history').where('status', '==', 'incomplete').stream()

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
    parking_history = db.collection('parking_history')

    # Add a document with vehicle details
    parking_history.add({
        'userid': rfid,
        'parkingid': '79yuoUXhcRdMJ32F3yyp',
        'parkingName' : 'PCPS parking',
        'entry_time': firestore.SERVER_TIMESTAMP,
        'status': 'incomplete',
    })
    print("Vehicle details entered in Firestore.")

def update_exiting_vehicle(rfid):
    # Update the parking status to "completed" in Firestore
    parking_doc_ref = db.collection('parking_history')
    query = parking_doc_ref.where('userid', '==', rfid).where('status', '==', 'incomplete').where('userid', '==', rfid,)

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
        open_gate()
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
