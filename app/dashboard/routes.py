from flask import *
from . import myMongo
import pymongo
from . import dashboard_bp

Atlas_string1 = "mongodb+srv://dev3kha7_8721:YWzwlBcc4swtZEqN@1stcluster.ldsbsgi.mongodb.net/"
local_client = pymongo.MongoClient(Atlas_string1)
local_db = local_client['PortFolio']

'''
=======================================================================================================================================================================================================
                                                    DASHBOARD FUNCTIONALITY
=======================================================================================================================================================================================================
'''
# ROUTE TO CHECK THE PASSWORD AND LET A USER ENTER YOUR DASHBAORD
@dashboard_bp.route('/openDashboard/<memberCode>', methods=['GET', 'POST'])
def openDashboard(memberCode):
    if request.method == 'POST':
        passwd = request.form.get("password")
        db1 = local_client['PortFolio-Confidential']
        collection = db1['Members']
        member = collection.find_one({"memberCode":memberCode})
        if member['passwd'] == passwd:
            session[f'openDashboard_{memberCode}'] = True
            return redirect(f'/dashboard/memberDashboard/{memberCode}')
        else:
            return "Incorrect Password. Please try again."
    return "Method not allowed !! Error Code 408"

# ROUTE TO CHECK THE MEMBERCODE & PASSWORD AND LET A USER ENTER YOUR DASHBAORD
@dashboard_bp.route('/openDashboardFromTeamPortfolio', methods=['POST', 'GET'])
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
            return redirect(f'/dashboard/memberDashboard/{memberCode}')
        else:
            return "<h3><strong>Incorrect Member-Code or Password. Please try again.</strong></h3>"
    return "Method not allowed !! Error Code 408"

# ROUTE TO RENDER THE DASHBOARD
@dashboard_bp.route('/memberDashboard/<memberCode>')
def memberDashboard(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    return render_template("memberDashboard.html", member=member)

# ROUTE TO lOG OUT FROM THE DASHBOARD
@dashboard_bp.route('/Logout_Dashboard/<memberCode>', methods=['POST', 'GET'])
def Logout(memberCode):
    session.pop(f'openDashboard_{memberCode}', None)
    #Disable the login session in here
    return redirect('/TeamPortFolio')

# ROUTE TO ADD NEW-PROJECTS TO YOUR PORTFOLIO
@dashboard_bp.route('/addProject/<memberCode>', methods=['POST', 'GET'])
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
            return redirect(f'/dashboard/addProject/{memberCode}')
        else:
            return "Password error. Please try again"
    return render_template('addProject.html', categories=categories, memberCode=memberCode, memberName=member['memberName'])

def portFolio_Project_Images(image):
    from pathlib import Path
    import os
    save_directory = Path(__file__).parent.parent / "static" / "images" / "portFolio_Project_Images"
#   save_directory = "C:\\Users\\User\\Desktop\\Bash,Flask,MongoDB,Website-PROJECTS\DEPLOYEBLE_PORTFOLIO_VERSION_2.0\\app\\static\\images\\portFolio_Project_Images"
    save_filename = image.filename
    full_save_path = os.path.join(save_directory, save_filename)
    os.makedirs(save_directory, exist_ok=True)
    image.save(str(full_save_path))

# ROUTE TO ADD NEW-DOCUMENT TO YOUR PORTFOLIO
@dashboard_bp.route('/addDocuments/<memberCode>', methods=['POST', 'GET'])
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
            
            storeDoc2(new_doc)
            return redirect(f'/addDocuments/{memberCode}')
        else:
            return "Incorrect Password !!"
    return render_template('addDocuments.html', memberCode=memberCode, memberName=member['memberName'])

# Store Document to app/static/documents folder 
def storeDoc(new_file):
    import os
    save_directory = "C:\\Users\\User\\Desktop\\Bash,Flask,MongoDB,Website-PROJECTS\DEPLOYEBLE_PORTFOLIO_VERSION_2.0\\app\\static\\documents"
    save_filename = new_file.filename
    full_save_path = os.path.join(save_directory, save_filename)
    os.makedirs(save_directory, exist_ok=True)
    new_file.save(full_save_path)
    
def storeDoc2(new_file):
    from pathlib import Path
    folder = Path(__file__).parent.parent
    location = folder / "static" / "documents"
    location.mkdir(parents=True, exist_ok=True)
    full_save_path = location / new_file.filename
    new_file.save(str(full_save_path))

# ROUTE TO DELETE A DOCUMENT
@dashboard_bp.route('/deleteDocument/<memberCode>', methods=['POST', 'GET'])
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
@dashboard_bp.route('/editCategory/<memberCode>', methods=['POST', 'GET'])
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
@dashboard_bp.route('/addCategory/<memberCode>', methods=['POST', 'GET'])
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

@dashboard_bp.route('/Uplaoad_Member/<memberCode>', methods=['POST', 'GET'])
def uplaod_member(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    if request.method == 'POST':
        memberName = request.form['memberName']
        collegeCode = request.form['collegeCode']
        course_Roll = request.form['course_Roll']
        memberPost = request.form['memberPost']
        new_memberCode = request.form['memberCode']
        new_passwd = request.form['passwd']
        Image = request.files.get('memberImage')
        categories = list()
        documents = list()
        my_password = request.form['my_password']
        Api_key = request.form.get("Api-Key")
        email = request.form.get('email')
        
        db = local_client['PortFolio-Confidential']
        collection = db['Members']
        collection2 = db['Members-APIKey']
        member = collection.find_one({"memberCode":memberCode})
        if member["passwd"] == my_password:
            data = {"memberName":memberName, "collegeCode":collegeCode, "course_Roll":course_Roll, "memberPost":memberPost, "memberCode":new_memberCode, "passwd":new_passwd, "memberImageName":Image.filename, "memberImageType":Image.content_type, "categories":categories, "documents":documents }
            collection.insert_one(data)
            portFolio_Member_Images(Image)
            
            if Api_key != "":
                data = {"email":email, "email-API":Api_key, "memberCode":new_memberCode, "memberName":memberName, "passwd":new_passwd}
            return redirect(f'/dashboard/memberDashboard/{memberCode}')
        else:
            return "<strong> Entered the worng password please try again !! </strong>"
    return render_template("Upload_Member.html", memberCode=memberCode)

'''
=======================================================================================================================================================================================================
                                                    EDIT PROJECTS
=======================================================================================================================================================================================================
'''
@dashboard_bp.route('/showAllProjects/<memberCode>', methods=['POST', 'GET'])
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

@dashboard_bp.route('/editProject/<memberCode>/<projectCode>', methods=['POST', 'GET'])
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
    return redirect(f'/showAllProjects/{memberCode}')

@dashboard_bp.route('/updateProjectName/<memberCode>', methods=['POST', 'GET'])
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
            return redirect(f'/showAllProjects/{memberCode}')
    return redirect('/TeamPortFolio')


@dashboard_bp.route('/updateProjectDescription/<memberCode>', methods=['POST', 'GET'])
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
            return redirect(f'/showAllProjects/{memberCode}')
    return redirect('/TeamPortFolio')

@dashboard_bp.route('/updateProjectPhoto/<memberCode>', methods=['POST', 'GET'])
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
            return redirect(f'/showAllProjects/{memberCode}')
    return redirect('/TeamPortFolio')
    
@dashboard_bp.route('/updateProjectCategory/<memberCode>', methods=['POST', 'GET'])
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
            return redirect(f'/showAllProjects/{memberCode}')
    return redirect('/TeamPortFolio')


@dashboard_bp.route('/updateExpandView/<memberCode>', methods=['POST', 'GET'])
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
            return redirect(f'/showAllProjects/{memberCode}')
    return redirect('/TeamPortFolio')

'''
=======================================================================================================================================================================================================
                                                    EDIT PROFILE
=======================================================================================================================================================================================================
'''
@dashboard_bp.route('/editProfile/<memberCode>', methods=['POST', 'GET'])
def editProfile(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    return render_template("editProfile.html", member=member)

@dashboard_bp.route("/updateName/<memberCode>", methods=['POST', 'GET'])
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

@dashboard_bp.route("/updatePhoto/<memberCode>", methods=['POST', 'GET'])
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
    from pathlib import Path
    import os
#   save_directory = "C:\\Users\\User\\Desktop\\Bash,Flask,MongoDB,Website-PROJECTS\DEPLOYEBLE_PORTFOLIO_VERSION_2.0\\app\\static\\images\\portFolio_Member_Images"
    save_directory = Path(__file__).parent.parent / "static" / "images" / "portFolio_Member_Images"
    save_filename = photo.filename
    full_save_path = os.path.join(save_directory, save_filename)
    os.makedirs(save_directory, exist_ok=True)
    photo.save(str(full_save_path))

@dashboard_bp.route("/updatePassword/<memberCode>", methods=['POST', 'GET'])
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


@dashboard_bp.route("/updateCollegeCode/<memberCode>", methods=['POST', 'GET'])
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

@dashboard_bp.route("/updateCourseRoll/<memberCode>", methods=['POST', 'GET'])
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
