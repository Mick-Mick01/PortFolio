from flask import *
import pymongo
from . import client_bp
import smtplib
from email.mime.text import MIMEText
import gridfs
from io import BytesIO  #For Return send_file()


#For sending automated emails
smtp_host = 'smtp.zoho.in'
smtp_port = 465

Atlas_string1 = "mongodb+srv://dev3kha7_8721:YWzwlBcc4swtZEqN@1stcluster.ldsbsgi.mongodb.net/"
# local_client = pymongo.MongoClient(Atlas_string1)
local_client = pymongo.MongoClient("mongodb://localhost:27017")
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
    if request.method == 'POST':
        visitorName = request.form.get('name')
        visitorEmail = request.form.get('email')
        mobile = request.form.get('mobile')
        message = request.form.get('message')
        data = {
            "visitorName":visitorName, "visitorEmail":visitorEmail, "mobile":mobile, "message":message 
        }
        db = local_client['PortFolio-Confidential']
        collection = db['visitorInfo']
        collection.insert_one(data)
    
        #After storing visitor's data into DB. We need the emailID & Key of the member to send an automated email
        db1 = local_client['PortFolio-Confidential']
        collection = db1['Members-APIKey']
        member = collection.find_one({"memberCode":memberCode})
        if member:
            emailID = member['email']
            API_key = member['email-API']
            
        else:
            member = collection.find_one({"memberCode":"DevCrishKha8721"})
            emailID = member['email']
            API_key = member['email-API']
            #composing the HTML emailBody 
            emailBody = f''' <body><div style="max-width: 600px;margin: 0 auto;font-family: 'Segoe UI', sans-serif;color: #333;" ><div style="display: flex;background: linear-gradient(135deg, #ff9933 0%, #ffffff 50%, #138808 100%);align-items: center;justify-content: center;padding: 2rem;text-align: center;color: #333;font-family: 'Segoe UI', sans-serif;border-radius: 8px;"><h1 style="margin: 0;font-size: 1.8rem;">Thank You for Reaching Me Out 🤗</h1></div><div style="background: #ffffff;border-radius: 8px;padding: 1.5rem;margin-top: 1rem;box-shadow: 0 2px 6px rgba(0,0,0,0.1);line-height: 1.6;"><p>Hi, <strong>{ visitorName }</strong>,</p><p>Thank you for getting in touch! I’ve received your message and noted your details:</p><ul><li><strong>Email:</strong> { visitorEmail }</li><li><strong>Mobile:</strong> { mobile }</li></ul><p>I’ll get back to you as soon as possible.  Meanwhile, wish you have a wonderful day 🌸</p><p>Your Sincerely,<br><strong>{ member['memberName'] }</strong></p></div></div></body>'''
            msg = MIMEText(emailBody, 'html', 'utf-8')
            msg['Subject'] = "ThankYou For Reaching Me Out 🤗"
            msg['From'] = emailID
            msg['To'] = visitorEmail
            
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(emailID, API_key)
                server.send_message(msg)
            return redirect(f'/ReachMe/{memberCode}')
        
    return render_template('ReachMe.html', memberCode=memberCode)