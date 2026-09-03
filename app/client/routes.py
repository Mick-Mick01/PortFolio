from flask import *
import pymongo
from . import client_bp
import smtplib
from email.mime.text import MIMEText
import gridfs
from io import BytesIO  #For Return send_file()
from dotenv import load_dotenv
import os
from threading import Thread

load_dotenv()

Atlas_string1 = os.getenv("Atlas_string1")
local_client = pymongo.MongoClient(Atlas_string1)
# local_client = pymongo.MongoClient("mongodb://localhost:27017")
local_db = local_client['PortFolio']
fsDB = local_client["PortFolio-Confidential"]
fs = gridfs.GridFS(fsDB)

'''
=======================================================================================================================================================================================================
                                                    HOME FUNCTIONALITY
=======================================================================================================================================================================================================
'''
# THIS ROUTE IS NECESSARY AFTER SENDING TUNNELING LINK PEOPLE CAN SEE MY PORTFOLIO
@client_bp.route('/', methods=['GET', 'POST']) 
def Default():
    return redirect("/TeamPortFolio")

# HOME PAGE FOR ALL THE MEMBERS
@client_bp.route('/Home/<memberCode>')
def Home(memberCode):
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    categories = member['categories']
    return render_template("portFolio_Home_Page_Dynamic.html", member=member, categories=categories, memberName=member['memberName'])


# RENDER THE PROJECT-VIEW ONCE A USER CLICKS ON A PROJECT-BUTTON THE JS TAKES HTML FROM HERE AND PASTES ON THE HTML PAGE
@client_bp.route('/render_projectView/<project_category>/<memberCode>', methods=['POST', 'GET'])
def render_projectView(project_category, memberCode):
    collection = local_db[project_category]
    all_projects = collection.find()
    projects = list()
    for project in all_projects:
        if project['memberCode'] == memberCode:
            projects.append(project)
    return render_template("partials/projectView.html", projects=projects)

# ROUTE FOR PEOPLES TOO SEE MY WHOLE TEAM AND THEIR PORTFOLIO
@client_bp.route('/TeamPortFolio', methods=['POST', 'GET'] )
def TeamPortFolio():
    db = local_client["PortFolio-Confidential"]
    collection = db["Members"]
    members = list(collection.find())
    return render_template("TeamPortFolio.html", members=members)

# ROUTE FOR PEOPLE TO SEE THE DOWNLOAD DOCUMENT PAGE
@client_bp.route('/Documents/<memberCode>', methods=['POST', 'GET'])
def Documents(memberCode):
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    if member:
        documents = fs.find({"memberCode":memberCode})
        return render_template("downloadDocuments.html", member=member, documents=documents, memberName=member['memberName'], as_attachment=True)
    else:
        return "Member did not uplaod any document"

# ROUTE FOR THE DOWNLOAD-DOCUMENT PAGE USNG WHICH THE DOCUMENT WILL ACTUALLY DOWNLAOD. ELSE IT WILL JUST OPEN THE DOCUMENT IN THE BROWSER
@client_bp.route('/Documents/download/<filename>')
def download_document(filename):
    try:
        file = fs.find({"filename":filename}).next()
        return send_file(
            BytesIO(file.read()),
            as_attachment=True,
            download_name=file.filename,   # Flask ≥2.0 uses download_name
            mimetype="application/octet-stream"
                         )
    except FileNotFoundError:
        abort(404)

# USERS CAN REACH ME & GET AN AUTOMATED EMAIL    
@client_bp.route('/ReachMe/<memberCode>', methods=['POST', 'GET'])
def ReachMe(memberCode):
    load_dotenv(dotenv_path='../.env')
    
    #For sending automated emails
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    
    visitorName = None
    visitorEmail = None 
    visitorMobile = None 
    message = None

    if request.method == 'POST':
        visitorName = request.form.get('name')
        visitorEmail = request.form.get('email')
        visitorMobile = request.form.get('mobile')
        message = request.form.get('message')
        
        data = {
            "visitorName":visitorName, "visitorEmail":visitorEmail, "mobile":visitorMobile, "message":message 
        }
        print(f"Got info: name:{visitorName}, email:{visitorEmail} \nSaved to MongoDB")
        db = local_client['PortFolio-Confidential']
        collection = db['visitorInfo']
        collection.insert_one(data)
    
        #After storing visitor's data into DB. We need the emailID & Key of the member to send an automated email
        db1 = local_client['PortFolio-Confidential']
        collection = db1['Members-Credentials']
        member = collection.find_one({"memberCode":memberCode})
        if member:
            emailID = member['email']
            API_key = os.getenv(f"{memberCode}_gmail_api_key")
            print(f"Found API key from .env Key: {API_key}")
            
            print("Sending request to the Gmail smtp server in a thread (To run in Background)")
            Thread(
                target=send_email_background,
                args=( smtp_host, smtp_port, emailID, API_key, visitorName, visitorEmail, visitorMobile, message, member),
                daemon=True
            ).start()
            # return redirect(f'/ReachMe/{memberCode}')
            pass
            
        else:
            print("Did not find member in Members-Collection")
            member = collection.find_one({"memberCode":"DevCrishKha8721"})
            emailID = member['email']
            API_key = os.getenv(f"{memberCode}_gmail_api_key")
            
            print("Sending request to the Gmail smtp server in a thread (To run in Background)")
            Thread(
                target=send_email_background,
                args=( smtp_host, smtp_port, emailID, API_key, visitorName, visitorEmail, visitorMobile, message, member),
                daemon=True
            ).start()
            return redirect(f'/ReachMe/{memberCode}')
    
    # return render_template('ReachMe.html', memberCode=memberCode)
    pass


def send_email_background(*args):
    try:
        ''' ALWAYS PASS FUNCTION INSIDE THREADING THIS WAY, DO NOT WRITE THE PARAMETERS WITH THE FUNCTION INSIDE (), Thread expects the function itself, not the result of calling the function. '''
        send_email(*args)    
    except Exception as e:
        print("Email sending failed:", e)
        

def send_email(smtp_host, smtp_port, emailID, API_key, visitorName, visitorEmail, visitorMobile, visitorMessage, member):   #We are passing the member dict for memberName only
    #composing the HTML emailBody 
    
    emailBody = f''' <body><div style="max-width: 600px;margin: 0 auto;font-family: 'Segoe UI', sans-serif;color: #333;" ><div style="display: flex;background: linear-gradient(135deg, #ff9933 0%, #ffffff 50%, #138808 100%);align-items: center;justify-content: center;padding: 2rem;text-align: center;color: #333;font-family: 'Segoe UI', sans-serif;border-radius: 8px;"><h1 style="margin: 0;font-size: 1.8rem;">Thank You for Reaching Me Out 🤗</h1></div><div style="background: #ffffff;border-radius: 8px;padding: 1.5rem;margin-top: 1rem;box-shadow: 0 2px 6px rgba(0,0,0,0.1);line-height: 1.6;"><p>Hi, <strong>{ visitorName }</strong>,</p><p>Thank you for getting in touch! I’ve received your message and noted your details:</p><ul><li><strong>Email:</strong> { visitorEmail }</li><li><strong>Mobile:</strong> { visitorMobile }</li></ul><p>I’ll get back to you as soon as possible.  Meanwhile, wish you have a wonderful day 🌸</p><p>Your Sincerely,<br><strong>{ member['memberName'] }</strong></p></div></div></body>'''
    msg = MIMEText(emailBody, 'html', 'utf-8')
    msg['Subject'] = "ThankYou For Reaching Me Out 🤗"
    msg['From'] = emailID
    msg['To'] = visitorEmail
                
    print("Sending request to the server")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(emailID, API_key)
        server.send_message(msg)
    print("sending notification email to devcrishkha@gmail.com")
    
    emailBody = f''' <body>
    <div style="max-width: 600px;margin: 0 auto;font-family: 'Segoe UI', sans-serif;color: #333;">
        <div
            style="display: flex;background: linear-gradient(135deg, #ff9933 0%, #ffffff 50%, #138808 100%);align-items: center;justify-content: center;padding: 2rem;text-align: center;color: #333;font-family: 'Segoe UI', sans-serif;border-radius: 8px;">
            <h1 style="margin: 0;font-size: 1.8rem;">{ member['memberName'] } \nSomeone reached your PortFolio page🎉🤟🔥</h1>
        </div>
        <div
            style="background: #ffffff;border-radius: 8px;padding: 1.5rem;margin-top: 1rem;box-shadow: 0 2px 6px rgba(0,0,0,0.1);line-height: 1.6;">
            <h3>Visitor Info:</h3>
            <ul>
                <li><strong>Name:</strong> { visitorName }</li>
                <li><strong>Email:</strong> { visitorEmail }</li>
                <li><strong>Mobile:</strong> { visitorMobile }</li>
            </ul>
            <h3><strong>Message: </strong></h3>
            <p>{ visitorMessage }</p>
            <p>Your Sincerely,<br><strong>{ member['memberName'] }</strong></p>
        </div>
    </div>
</body>
'''
    notification = MIMEText(emailBody, 'html', 'utf-8')
    notification['Subject'] = f" { member['memberName'] } | Someone reached your PortFolio page 🎉🤟🔥 | \n Msg from PortFolio AutoEmailing system"
    notification['From'] = emailID
    notification['To'] = "devcrishkha@gmail.com"
                    
    print("Sending request to the server")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(emailID, API_key)
        server.send_message(notification)
        
    print("Done sending email and notification")