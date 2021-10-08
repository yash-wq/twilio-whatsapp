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



cred = credentials.Certificate("test-report-atomicloops-firebase-adminsdk-qrnrn-0dc0bafa96.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
docs = db.collection('users').stream()


json_file_name  = 'test_report.json'

def get_image():
    return request.form.get('MediaUrl0')

app = Flask(__name__)
global_var = ''
global_dict = {'img_url':'','patient_name':'','doct_name':'','date':''}


def uploading_to_db(phone_number, patient_name, doct_name,img_url, date):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    data_to_DB = {
        phone_number:{
            'patient_name':patient_name,
            'doctor_name':doct_name,
            'image':img_url,
            'date':date
        }
    }
    db.collection('test_report').document(current_time).set(data_to_DB)



@app.route('/bot', methods=['POST'])
def bot():
    global global_list
    recently_updated = False

    global global_var
    incoming_msg = request.values.get('Body', '').lower()
    phone_number = request.values.get('From', '').lower().split(':')[-1]

    print('image',get_image())

    print('media',request.values.get('subresource_uris', ''))
    resp = MessagingResponse()
    msg = resp.message()
    if "report" in incoming_msg:
        msg.body('Welcome to test report section. Type anything to continue with the process')
        global_var = 'welcomed'
        recently_updated = True
    if global_var == 'welcomed' and not recently_updated:
        msg.body('Please upload the image')
        global_var = "asked_for_image"
        recently_updated = True
        
    if global_var == 'asked_for_image' and not recently_updated:
        img_url = get_image()
        print("got image", img_url)
        msg.body('Please enter the full name of the patient')

        image_url = img_url
        filename = image_url.split("/")[-1]

        r = requests.get(image_url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True

            with open(f'{filename}.jpg','wb') as f:
                shutil.copyfileobj(r.raw, f)
        img_name = f'{filename}.jpg'
        global_var = 'asked_for_name'
        recently_updated =True
        print('00000000000000000000000000',img_name)


        global_dict['img_url'] = img_name


    if global_var == 'asked_for_name' and not recently_updated:
        patient_name = incoming_msg
        msg.body('Please enter the name of the doctor')
        recently_updated = True
        global_var = 'asked_for_doct_name'

        global_dict['patient_name'] = patient_name

    if global_var == 'asked_for_doct_name' and not recently_updated:
        doct_name = incoming_msg
        msg.body('Please enter the date')
        global_var ='asked_for_date'
        recently_updated = True

        global_dict['doct_name'] = doct_name

    if global_var=='asked_for_date' and not recently_updated:
        date = incoming_msg
        global_var = ''
        recently_updated = True

        global_dict['date'] = date

#######3###DB writing

# test_report
        uploading_to_db(phone_number, global_dict['patient_name'], global_dict['doct_name'],global_dict['img_url'], global_dict['date'])
        msg.body("successfully saved")




###########

##########Json writing:
        # now = datetime.now()

        # current_time = now.strftime("%H:%M:%S")
        # new_obj_name = current_time

        # new_object_contents = {phone_number:{
        #     "patient_name":global_dict['patient_name'],
        #     "doct_name":global_dict['doct_name'],
        #     "img_url":global_dict['img_url'],
        #     "date":global_dict['date']
        # }}
        # with open(json_file_name,'r+') as file:
        #     file_data = json.load(file)
        #     file_data[new_obj_name]=new_object_contents
        #     file.seek(0)
        #     json.dump(file_data, file, indent = 4)
###########3


    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)