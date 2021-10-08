import re
from flask import Flask, request
import requests, json
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import requests 
import shutil 
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db, firestore

json_file_name = 'data.json'

app = Flask(__name__)
global_flag = ''
data_dict = {'name':'','date_of_reading':'','type_of_reading':'','time':''}
@app.route('/bot', methods = ['POST'])
def bot():
    global global_flag
    recently_updated = False
    incoming_msg = request.values.get('Body', '').lower()
    phone_number = request.values.get('From', '').lower().split(':')[-1]
    resp = MessagingResponse()
    msg = resp.message()
    if 'blood sugar' in incoming_msg:
        msg.body("Welcome to the blood sugar section, please enter the full name of the patient")
        global_flag = 'asked_for_name'
        recently_updated = True
    if global_flag == 'asked_for_name' and not recently_updated:
        name = incoming_msg
        print(name,'nameeeeeeeeeeee')
        data_dict['name'] = name
        msg.body("What is the date of test?")
        recently_updated = True
        global_flag = 'asked_for_date'
    if global_flag == 'asked_for_date' and not recently_updated:
        date = incoming_msg
        print(date,'dateeeeeee')
        data_dict['date_of_reading'] = date
        msg.body("""
Type of Reading
1. For Fasting
2. PP
3. Random
        """)
        recently_updated = True
        global_flag = 'asked_for_type_of_reading'
    if global_flag == 'asked_for_type_of_reading' and not recently_updated:
        if '1' in incoming_msg:
            type_of = 'Fasting'
        elif '2' in incoming_msg:
            type_of = 'PP'
        elif '3' in incoming_msg:
            type_of = 'Random'
        else:
            type_of = incoming_msg
        data_dict['type_of_reading'] = type_of
        msg.body("Enter the time of reading")
        recently_updated = True
        global_flag = "asked_for_time"
    
    if global_flag == 'asked_for_time' and not recently_updated:
        time = incoming_msg
        global_flag = ''
        recently_updated = True
        data_dict['time'] = time
        msg.body(data_dict)

################3 writing to json
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        new_obj_name = current_time

        new_object_contents = {phone_number:{
            "patient_name":data_dict['name'],
            "date_of_reading":data_dict['date_of_reading'],
            "type_of_reading":data_dict['type_of_reading'],
            "time":data_dict['time']
        }}
        with open(json_file_name,'r+') as file:
            file_data = json.load(file)
            file_data[new_obj_name]=new_object_contents
            file.seek(0)
            json.dump(file_data, file, indent = 4)
#################
        


         

    return str(resp)


if __name__ == '__main__':
    app.run(debug = True)