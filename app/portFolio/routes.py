from flask import *
from . import myMongo
import pymongo
from . import portFolio_bp
import os
import smtplib
from email.mime.text import MIMEText

#For sending automated emails
smtp_host = 'smtp.zoho.in'
smtp_port = 465  # Use 465 for SSL

Atlas_string1 = "mongodb+srv://dev3kha7_8721:YWzwlBcc4swtZEqN@1stcluster.ldsbsgi.mongodb.net/"
#WHILE UPLOADING DATA USE BOTH LOCAL & ATLAS DBs
# local_client = pymongo.MongoClient("mongodb://localhost:27017")
local_client = pymongo.MongoClient(Atlas_string1)
local_db = local_client['PortFolio']

'''
=======================================================================================================================================================================================================
                                                    HOME FUNCTIONALITY
=======================================================================================================================================================================================================
'''
# THIS ROUTE IS NECESSARY AFTER SENDING TUNNELING LINK PEOPLE CAN SEE MY PORTFOLIO
@portFolio_bp.route('/', methods=['GET', 'POST']) 
def Default():
    # return render_template("portFolio_Home_Page.html")
    return redirect("/Home/DevCrishKha8721")

# HOME PAGE FOR ALL THE MEMBERS
@portFolio_bp.route('/Home/<memberCode>')
def Home(memberCode):
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    categories = member['categories']
    return render_template("portFolio_Home_Page_Dynamic.html", member=member, categories=categories, memberName=member['memberName'])


# RENDER THE PROJECT-VIEW ONCE A USER CLICKS ON A PROJECT-BUTTON THE JS TAKES HTML FROM HERE AND PASTES ON THE HTML PAGE
@portFolio_bp.route('/render_projectView/<project_category>/<memberCode>', methods=['POST', 'GET'])
def render_projectView(project_category, memberCode):
    collection = local_db[project_category]
    all_projects = collection.find()
    projects = list()
    for project in all_projects:
        if project['memberCode'] == memberCode:
            projects.append(project)
    return render_template("partials/projectView.html", projects=projects)

# ROUTE FOR PEOPLES TOO SEE MY WHOLE TEAM AND THEIR PORTFOLIO
@portFolio_bp.route('/TeamPortFolio', methods=['POST', 'GET'] )
def TeamPortFolio():
    db = local_client["PortFolio-Confidential"]
    collection = db["Members"]
    members = list(collection.find())
    return render_template("TeamPortFolio.html", members=members)

# ROUTE FOR PEOPLE TO SEE THE DOWNLOAD DOCUMENT PAGE
@portFolio_bp.route('/Documents/<memberCode>', methods=['POST', 'GET'])
def Documents(memberCode):
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    if member:
        documents = member['documents']
        return render_template("downloadDocuments.html", member=member, documents=documents, memberName=member['memberName'], as_attachment=True)
    else:
        return "Member did not uplaod any document"

# ROUTE FOR THE DOWNLOAD-DOCUMENT PAGE USNG WHICH THE DOCUMENT WILL ACTUALLY DOWNLAOD. ELSE IT WILL JUST OPEN THE DOCUMENT IN THE BROWSER
@portFolio_bp.route('/Documents/download/<filename>')
def download_document(filename):
    # Assuming your files are stored in static/documents/
    directory = "C:\\Users\\User\\Desktop\\Bash,Flask,MongoDB,Website-PROJECTS\DEPLOYEBLE_PORTFOLIO_VERSION_2.0\\app\\static\\documents"
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# USERS CAN REACH ME & GET AN AUTOMATED EMAIL    
@portFolio_bp.route('/ReachMe/<memberCode>', methods=['POST', 'GET'])
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



'''
=======================================================================================================================================================================================================
                                                    DASHBOARD FUNCTIONALITY
=======================================================================================================================================================================================================
'''
# ROUTE TO CHECK THE PASSWORD AND LET A USER ENTER YOUR DASHBAORD
@portFolio_bp.route('/openDashboard/<memberCode>', methods=['GET', 'POST'])
def openDashboard(memberCode):
    if request.method == 'POST':
        passwd = request.form.get("password")
        db1 = local_client['PortFolio-Confidential']
        collection = db1['Members']
        member = collection.find_one({"memberCode":memberCode})
        if member['passwd'] == passwd:
            session[f'openDashboard_{memberCode}'] = True
            return redirect(f'/memberDashboard/{memberCode}')
        else:
            return "Incorrect Password. Please try again."
    return "Method not allowed !! Error Code 408"

# ROUTE TO CHECK THE MEMBERCODE & PASSWORD AND LET A USER ENTER YOUR DASHBAORD
@portFolio_bp.route('/openDashboardFromTeamPortfolio', methods=['POST', 'GET'])
def openDashboardFromTeamPortfolio():
    if request.method == 'POST':
        memberCode = request.form.get('memberCode')
        passwd = request.form.get('password')
        #checking if the password is for this memberCode
        db1 = local_client['PortFolio-Confidential']
        collection = db1['Members']
        member = collection.find_one({"memberCode":memberCode})
        if member['passwd'] == passwd:
            session[f'openDashboard_{memberCode}'] = True
            return redirect(f'/memberDashboard/{memberCode}')
        else:
            return "<h3><strong>Incorrect Member-Code or Password. Please try again.</strong></h3>"
    return "Method not allowed !! Error Code 408"

# ROUTE TO RENDER THE DASHBOARD
@portFolio_bp.route('/memberDashboard/<memberCode>')
def memberDashboard(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    return render_template("memberDashboard.html", member=member)

# ROUTE TO lOG OUT FROM THE DASHBOARD
@portFolio_bp.route('/Logout_Dashboard/<memberCode>', methods=['POST', 'GET'])
def Logout(memberCode):
    session.pop(f'openDashboard_{memberCode}', None)
    #Disable the login session in here
    return redirect('/TeamPortFolio')

# ROUTE TO ADD NEW-PROJECTS TO YOUR PORTFOLIO
@portFolio_bp.route('/addProject/<memberCode>', methods=['POST', 'GET'])
def addProject(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    categories = member['categories']
    if request.method == 'POST':
        category = request.form.get('category')
        projectName = request.form.get('projectName')
        passwd = request.form.get('memberPassCode')
        Code = memberCode
        projectLink = request.form.get('projectLink')
        projectCode = request.form.get('projectCode')
        image = request.files.get('image')
        discription = request.form.get('discription')
        HTMLcode = request.form.get('HTMLcode')

#       Check the password from mongoDB before adding the project 
        db1 = local_client['PortFolio-Confidential']
        collection = db1['Members']
        member = collection.find_one({"memberCode":Code})
        if member['passwd'] == passwd:
        
#           checking for conflicting projectCode. Each project will have its own projectCode
            categories = member['categories']
            for category in categories:
                colection = local_db[category]
                project = colection.find_one({"projectCode":projectCode})
                if project:
                    return "A project with this name already exists. Please change the name or delete the older project"
                
#           checking for XSS atack on a flask Jinja-template environment
            if '{' in HTMLcode or "script" in HTMLcode or "onclick" in HTMLcode:
                return "The HTMLcode doesn't seems right! Please do not add anything more than &lt;p&gt;, &lt;img&gt;, &lt;a&gt; and &lt;video&gt; tags <br> Even styling is not allowed"
            
#           After checking for any conflicting projectNames we store the data into mongoDB
            myMongo.uploadProject(category, projectName, memberCode, projectLink, image, discription, HTMLcode, projectCode)
            
            #After storing the data into mongoDB we store the image into static/images/portFolio_images folder
            portFolio_Project_Images(image)
            return redirect(f'/addProject/{memberCode}')
        else:
            return "Password error. Please try again"
    return render_template('addProject.html', categories=categories, memberCode=memberCode, memberName=member['memberName'])

def portFolio_Project_Images(image):
    save_directory = "C:\\Users\\User\\Desktop\\Bash,Flask,MongoDB,Website-PROJECTS\DEPLOYEBLE_PORTFOLIO_VERSION_2.0\\app\\static\\images\\portFolio_Project_Images"
    save_filename = image.filename
    full_save_path = os.path.join(save_directory, save_filename)
    os.makedirs(save_directory, exist_ok=True)
    image.save(full_save_path)

# ROUTE TO ADD NEW-DOCUMENT TO YOUR PORTFOLIO
@portFolio_bp.route('/addDocuments/<memberCode>', methods=['POST', 'GET'])
def uploadDocument(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    documents = member['documents']
    if request.method == 'POST':
        passwd = request.form.get('password')
        new_doc = request.files.get('document')
        #checking for conflicting documents
        for document in documents:
            if new_doc.filename == document:
                return f"\"{new_doc.filename}\" already exists !! If you want to add a Newer version <strong>please delete </strong> the older one."
        if member['passwd'] == passwd:
            documents.append(new_doc.filename)
            collection.update_one({"memberCode":memberCode}, {"$set": {"documents":documents}})
            
            storeDoc(new_doc)
            return redirect(f'/addDocuments/{memberCode}')
        else:
            return "Incorrect Password !!"
    return render_template('addDocuments.html', memberCode=memberCode, memberName=member['memberName'])

# Store Document to app/static/documents folder 
def storeDoc(new_file):
    save_directory = "C:\\Users\\User\\Desktop\\Bash,Flask,MongoDB,Website-PROJECTS\DEPLOYEBLE_PORTFOLIO_VERSION_2.0\\app\\static\\documents"
    save_filename = new_file.filename
    full_save_path = os.path.join(save_directory, save_filename)
    os.makedirs(save_directory, exist_ok=True)
    new_file.save(full_save_path)

# ROUTE TO DELETE A DOCUMENT
@portFolio_bp.route('/deleteDocument/<memberCode>', methods=['POST', 'GET'])
def deleteDocument(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    documents = member['documents']
    if request.method == 'POST':
        document = request.form['document']
        passwd = request.form['password']
        if member['passwd'] == passwd:
            deleteDoc(document, memberCode)
            return redirect(f'/deleteDocument/{memberCode}')
        else:
            return "Incorrect password !!"
    return render_template("deleteDocument.html", documents=documents, memberCode=memberCode, memberName=member['memberName'])

def deleteDoc(documentName, memberCode):
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    documents = member['documents']
    new_documents_list = list()
    for document in documents:
        if document == documentName:
            continue
        new_documents_list.append(document)
    collection.update_one({"memberCode":memberCode}, {'$set': {"documents":new_documents_list}})
    
# ROUTE TO EDIT CATEGORIES
@portFolio_bp.route('/editCategory/<memberCode>', methods=['POST', 'GET'])
def editCategory(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    categories = member['categories']
    if request.method == 'POST':
        categoryName = request.form.get('categoryName')
        password = request.form.get('password')
        if member['passwd'] == password:
            deleteCat(categoryName, memberCode)
            return redirect(f'/editCategory/{memberCode}')
        else:
            return "Incorrect password !! Please try Again !!."
    return render_template('editCategory.html', categories=categories, memberCode=memberCode)

# FUNCTION TO DELETE CATEGORY
def deleteCat(categoryName, memberCode):
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    categories = member['categories']
    new_category_list = list()
    for category in categories:
        if category == categoryName:
            continue
        new_category_list.append(category)
    collection.update_one({"memberCode":memberCode}, {'$set': {"categories":new_category_list}})
 
# ROUTE TO ADD CATEGORY
@portFolio_bp.route('/addCategory/<memberCode>', methods=['POST', 'GET'])
def addCategory(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    categories = member['categories']
    if request.method == 'POST':
        categoryName = request.form.get('categoryName')
        password = request.form.get('password')
        if " " in categoryName:
            return "<strong>Please do not put any spaces in category name</strong>"
        if member['passwd'] == password:
            categories.append(categoryName)
            collection.update_one({"memberCode":memberCode}, {'$set': {"categories":categories}})
            return redirect(f'/editCategory/{memberCode}')
    return redirect(f'/editCategory/{memberCode}')


'''
=======================================================================================================================================================================================================
                                                    EDIT PROJECTS
=======================================================================================================================================================================================================
'''
@portFolio_bp.route('/showMemberProjects/<memberCode>', methods=['POST', 'GET'])
def showProjects(memberCode):
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    categories = member['categories']
    db2 = local_client['PortFolio']
    all_projects = list()
    for category in categories:
        collection2 = db2[category]
        projects = list(collection2.find())
        for project in projects:
            if project['memberCode'] == memberCode:
                all_projects.append(project)
    if len(all_projects) == 0:
        return "No projects uploaded till Yet !!"
    return render_template("showAllProjects.html", all_projects=all_projects, memberCode=memberCode, memberName=member['memberName'])

@portFolio_bp.route('/editProject/<memberCode>/<projectCode>', methods=['POST', 'GET'])
def editProject(memberCode, projectCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    
    categories = member['categories']
    for category in categories:
        colection = local_db[category]
        project = colection.find_one({"projectCode":projectCode})
        if project:
            return render_template("editProject.html", memberCode=memberCode, project=project, memberName=member['memberName'], categories=categories)
    return redirect(f'/showMemberProjects/{memberCode}')

@portFolio_bp.route('/updateProjectName/<memberCode>', methods=['POST', 'GET'])
def updateProjectName(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection1 = db1['Members']
    member = collection1.find_one({"memberCode":memberCode})
    categories = member['categories']
    db2 = local_client['PortFolio']
    if request.method == 'POST':
        projectCode = request.form['projectCode']
        projectName = request.form['projectName']
        password = request.form['password']
        if member['passwd'] == password:
            for category in categories:
                collection2 = db2[category]
                collection2.update_one({"projectCode":projectCode}, {'$set': {"projectName":projectName}})
            return redirect(f'/showMemberProjects/{memberCode}')
    return redirect('/TeamPortFolio')


@portFolio_bp.route('/updateProjectDescription/<memberCode>', methods=['POST', 'GET'])
def updateProjectDescription(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection1 = db1['Members']
    member = collection1.find_one({"memberCode":memberCode})
    categories = member['categories']
    db2 = local_client['PortFolio']
    if request.method == 'POST':
        projectCode = request.form['projectCode']
        projectDescription = request.form['projectDescription']
        password = request.form['password']
        if member['passwd'] == password:
            for category in categories:
                collection2 = db2[category]
                collection2.update_one({"projectCode":projectCode}, {'$set': {"discription":projectDescription}})
            return redirect(f'/showMemberProjects/{memberCode}')
    return redirect('/TeamPortFolio')

@portFolio_bp.route('/updateProjectPhoto/<memberCode>', methods=['POST', 'GET'])
def updateProjectPhoto(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection1 = db1['Members']
    member = collection1.find_one({"memberCode":memberCode})
    categories = member['categories']
    db2 = local_client['PortFolio']
    if request.method == 'POST':
        projectCode = request.form['projectCode']
        projectPhoto = request.files.get('projectPhoto')
        password = request.form['password']
        if member['passwd'] == password:
            for category in categories:
                collection2 = db2[category]
                requiredProject = collection2.find_one({"projectCode":projectCode})
                if requiredProject:
                    collection2.update_one({"projectCode":projectCode}, {'$set': {"imageName":projectPhoto.filename}})
                    portFolio_Project_Images(projectPhoto)
            return redirect(f'/showMemberProjects/{memberCode}')
    return redirect('/TeamPortFolio')
    
@portFolio_bp.route('/updateProjectCategory/<memberCode>', methods=['POST', 'GET'])
def updateProjectCategory(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection1 = db1['Members']
    member = collection1.find_one({"memberCode":memberCode})
    categories = member['categories']
    db2 = local_client['PortFolio']
    
    if request.method == 'POST':
        projectCode = request.form['projectCode']
        projectCategory = request.form.get('category')
        password = request.form['password']
        if member['passwd'] == password:
            for category in categories:
                collection2 = db2[category]
                requiredProject = collection2.find_one({"projectCode":projectCode})
                if requiredProject != None:
                    db2[projectCategory].insert_one(requiredProject)
                    collection2.delete_one({"projectCode":projectCode})
                    db2[projectCategory].update_one({"projectCode":projectCode}, {'$set': {"category":projectCategory}})
                    break
            return redirect(f'/showMemberProjects/{memberCode}')
    return redirect('/TeamPortFolio')


@portFolio_bp.route('/updateExpandView/<memberCode>', methods=['POST', 'GET'])
def updateExpandView(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection1 = db1['Members']
    member = collection1.find_one({"memberCode":memberCode})
    categories = member['categories']
    db2 = local_client['PortFolio']
    if request.method == 'POST':
        projectCode = request.form['projectCode']
        Expandview = request.form['ExpandCode']
        password = request.form['password']
        if member['passwd'] == password:
            for category in categories:
                collection2 = db2[category]
                collection2.update_one({"projectCode":projectCode}, {'$set': {"HTMLcode":Expandview}})
            return redirect(f'/showMemberProjects/{memberCode}')
    return redirect('/TeamPortFolio')

'''
=======================================================================================================================================================================================================
                                                    EDIT PROFILE
=======================================================================================================================================================================================================
'''
@portFolio_bp.route('/editProfile/<memberCode>', methods=['POST', 'GET'])
def editProfile(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    return render_template("editProfile.html", member=member)

@portFolio_bp.route("/updateName/<memberCode>", methods=['POST', 'GET'])
def updateName(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    if request.method == 'POST':
        memberName = request.form['memberName']
        password = request.form['password']
        if member['passwd'] == password:
            member = collection.update_one({"memberCode":memberCode}, {'$set': {"memberName":memberName}})
            return redirect(f'/editProfile/{memberCode}')
    return redirect(f'/editProfile/{memberCode}')

@portFolio_bp.route("/updatePhoto/<memberCode>", methods=['POST', 'GET'])
def updatePhoto(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    if request.method == 'POST':
        photo = request.files.get('photo')
        password = request.form['password']
        if member['passwd'] == password:
            member = collection.update_one({"memberCode":memberCode}, {'$set': {"memberImageName":photo.filename}})
            
            #After storing the data into mongoDB we store the image into static/images/portFolio_images folder
            portFolio_Member_Images(photo)
            return redirect(f'/editProfile/{memberCode}')
    return redirect(f'/editProfile/{memberCode}')

def portFolio_Member_Images(photo):
    save_directory = "C:\\Users\\User\\Desktop\\Bash,Flask,MongoDB,Website-PROJECTS\DEPLOYEBLE_PORTFOLIO_VERSION_2.0\\app\\static\\images\\portFolio_Member_Images"
    save_filename = photo.filename
    full_save_path = os.path.join(save_directory, save_filename)
    os.makedirs(save_directory, exist_ok=True)
    photo.save(full_save_path)

@portFolio_bp.route("/updatePassword/<memberCode>", methods=['POST', 'GET'])
def updatePassword(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    if request.method == 'POST':
        newPassword = request.form['newPassword']
        password = request.form['password']
        if member['passwd'] == password:
            member = collection.update_one({"memberCode":memberCode}, {'$set': {"passwd":newPassword}})
            return redirect(f'/editProfile/{memberCode}')
    return redirect(f'/editProfile/{memberCode}')


@portFolio_bp.route("/updateCollegeCode/<memberCode>", methods=['POST', 'GET'])
def updateCollegeCode(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    if request.method == 'POST':
        collegeCode = request.form['collegeCode']
        password = request.form['password']
        if member['passwd'] == password:
            member = collection.update_one({"memberCode":memberCode}, {'$set': {"collegeCode":collegeCode}})
            return redirect(f'/editProfile/{memberCode}')
    return redirect(f'/editProfile/{memberCode}')

@portFolio_bp.route("/updateCourseRoll/<memberCode>", methods=['POST', 'GET'])
def updateCourseRoll(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    if request.method == 'POST':
        courseRoll = request.form['courseRoll']
        password = request.form['password']
        if member['passwd'] == password:
            member = collection.update_one({"memberCode":memberCode}, {'$set': {"course_Roll":courseRoll}})
            return redirect(f'/editProfile/{memberCode}')
    return redirect(f'/editProfile/{memberCode}')


'''
=======================================================================================================================================================================================================
                                                    COUNT VISITORS
=======================================================================================================================================================================================================
'''
