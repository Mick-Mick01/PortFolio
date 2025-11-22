from flask import *
from . import myMongo
import pymongo
from . import dashboard_bp
from bson import Binary
import gridfs #To store DOCs and give users for download through Return send_files()

Atlas_string1 = "mongodb+srv://dev3kha7_8721:YWzwlBcc4swtZEqN@1stcluster.ldsbsgi.mongodb.net/"
local_client = pymongo.MongoClient("mongodb://localhost:27017")
local_db = local_client['PortFolio']
fsDB = local_client["PortFolio-Confidential"]
fs = gridfs.GridFS(fsDB)

@dashboard_bp.route("/getImage/<dataBase>/<collection>/<filename>", methods=['GET'])
def get_Image(dataBase, collection, filename):
    db = local_client[dataBase]
    coll = db[collection]
    Image = coll.find_one({"imageName":filename})
    return Response(Image['imageContent'])

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
    categories = member["categories"]
    if request.method == 'POST':
        category = request.form.get('category')
        if category == "" or category == None:
            return "Add a valid project-category"
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
            for cat in categories:
                colection = local_db[cat]
                project1 = colection.find_one({"projectCode":projectCode})
                project2 = colection.find_one({"projectName":projectName})
                if project1 or project2:
                    return "A project with this Project-Code already exists. Please change the name & Project-Code or delete the older project"
                
#           checking for XSS atack on a flask Jinja-template environment
            if '{' in HTMLcode or "script" in HTMLcode or "onclick" in HTMLcode:
                return "The HTMLcode doesn't seems right! Please do not add anything more than &lt;p&gt;, &lt;img&gt;, &lt;a&gt; and &lt;video&gt; tags <br> Even styling is not allowed"
            
#           After checking for any conflicting projectNames we store the data into mongoDB
            myMongo.uploadProject(category, projectName, memberCode, projectLink, image, discription, HTMLcode, projectCode)
            
            return redirect(f'/dashboard/addProject/{memberCode}')
        else:
            return "Password error. Please try again"
    return render_template('addProject.html', categories=categories, memberCode=memberCode, memberName=member['memberName'])

@dashboard_bp.route('/deleteProject/<memberCode>', methods=['POST', 'GET'])
def deleteProject(memberCode):
    if not session.get(f'openDashboard_{memberCode}'):
        return "<strong>Please login first <a href='/TeamPortFolio'>Login</a> </strong>"
    #Getting the categories cause I need to show all categories to the user
    member = local_client['PortFolio-Confidential']['Members'].find_one({"memberCode":memberCode})
    categories = member['categories']
    all_projects = list()
    for category in categories:
        projects = list(local_client['PortFolio'][category].find({"memberCode":memberCode}))
        for project in projects:
            all_projects.append(project)
    if request.method == 'POST':
        projectCode = request.form.get("projectCode")
        category = request.form.get("category")
        passwd = request.form.get("password")
        if member['passwd'] == passwd:
            collection = local_db[category]
            collection.delete_one({"projectCode":projectCode})
            return redirect(url_for('dashboard.deleteProject', memberCode=memberCode))
    return render_template("deleteProject.html", all_projects=all_projects, memberCode=memberCode)

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
            if total_space_occupied(memberCode) > 40.00: # Return False if total_space >= 50
                return "You exeded your limit to upload files. Every Member gets <strong>50MB</strong> of storage. Contact the Developer(@ 8240892958) to upgrade your plan."
            else:
                check_total_space_occupied(new_doc, memberCode)
                if not fs.find_one({"filename":new_doc.filename}):
                    file_size = round((len(new_doc.read())/1024)/1024, 2)
                    return f"File not saved. You are exceding your limit to upload files by this upload. <br> Every Member gets <strong>50MB</strong> of storage. Contact the Developer(@ 8240892958) to upgrade your plan."
            documents.append(new_doc.filename)
            collection.update_one({"memberCode":memberCode}, {"$set": {"documents":documents}})
            
            store_to_gridfs(new_doc, memberCode)
            return redirect(f'/dashboard/addDocuments/{memberCode}')
        else:
            return "Incorrect Password !!"
    space = total_space_occupied(memberCode)
    space_occupied = round(space, 3)
    return render_template('addDocuments.html', memberCode=memberCode, memberName=member['memberName'], total_space_occupied=space_occupied)

#The file is first saved into mongoDB and then the total space is calculated. We cannot use len(file.read()) initially as it empties the stream. And I don't want to implement a tough to understand code right now.
def check_total_space_occupied(new_file, memberCode):
    file_id = fs.put(new_file, filename=new_file.filename, content_type=new_file.content_type, memberCode=memberCode)
    files = fs.find({"memberCode":memberCode})
    total_space_occupied = 0
    for file in files:
        total_space_occupied += ((file.length)/1024)/1024
    if total_space_occupied >= 40.00:
        current_file_id = fs.find_one({"filename":new_file.filename})
        fs.delete(current_file_id._id)

def total_space_occupied(memberCode):
    files = fs.find({"memberCode":memberCode})
    total_space_occupied = 0
    for file in files:
        total_space_occupied += file.length
    space = (total_space_occupied/1024)/1024
    return space

def store_to_gridfs(new_file, memberCode):
    #getting a file_id and storing that into the documents name. But that is not needed hence the user cannot upload the same named file more than once. So we can remote the term 'file_id' variable
    file_id = fs.put(new_file, filename=new_file.filename, content_type=new_file.content_type, memberCode=memberCode)

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
            return redirect(f'/dashboard/deleteDocument/{memberCode}')
        else:
            return "Incorrect password !!"
    return render_template("deleteDocument.html", documents=documents, memberCode=memberCode, memberName=member['memberName'])

def deleteDoc(documentName, memberCode):
    db1 = local_client['PortFolio-Confidential']
    collection = db1['Members']
    member = collection.find_one({"memberCode":memberCode})
    documents = member['documents']
    new_documents_list = list()
    # We need to create a new list without the documentName
    for document in documents:
        if document == documentName:
            continue
        new_documents_list.append(document)
    collection.update_one({"memberCode":memberCode}, {'$set': {"documents":new_documents_list}})
    
    #Deleting from gridFS
    files = fs.find({"filename":documentName})
    for file in files:
        fs.delete(file._id)  #Delete all files with the same filename. Hence we have only one file with the same name it only deletes one file. But still I want to take all the files and run a loop. To be safe in the future as I scale and want to have more options.
    
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
            return redirect(f'/dashboard/editCategory/{memberCode}')
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
        if member['passwd'] == password:
            categories.append(categoryName)
            collection.update_one({"memberCode":memberCode}, {'$set': {"categories":categories}})
            return redirect(f'/dashboard/editCategory/{memberCode}')
    return redirect(f'/dashboard/editCategory/{memberCode}')

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
            data = {"memberName":memberName, "collegeCode":collegeCode, "course_Roll":course_Roll, "memberPost":memberPost, "memberCode":new_memberCode, "passwd":new_passwd, "imageName":Image.filename, "imageContent":Binary(Image.read()), "imageType":Image.content_type, "categories":categories, "documents":documents }
            collection.insert_one(data)
            
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
            return render_template("editProject.html", project=project, member=member, categories=categories)
    return redirect(f'/dashboard/showAllProjects/{memberCode}')

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
            return redirect(f'/dashboard/showAllProjects/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
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
            return redirect(f'/dashboard/showAllProjects/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
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
                    collection2.update_one({"projectCode":projectCode}, {'$set': {"imageContent":Binary(projectPhoto.read())}})
                    collection2.update_one({"projectCode":projectCode}, {'$set': {"imageType":projectPhoto.content_type}})
            return redirect(f'/dashboard/showAllProjects/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
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
            return redirect(f'/dashboard/showAllProjects/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
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
            return redirect(f'/dashboard/showAllProjects/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
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
            collection.update_one({"memberCode":memberCode}, {'$set': {"memberName":memberName}})
            return redirect(f'/dashboard/editProfile/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
    return redirect(f'/dashboard/editProfile/{memberCode}')

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
            #Storing image of projects and members in mongoDB as Binary
            collection.update_one({"memberCode":memberCode}, {'$set': {"imageName":photo.filename}})
            collection.update_one({"memberCode":memberCode}, {'$set': {"imageContent":Binary(photo.read())}})
            collection.update_one({"memberCode":memberCode}, {'$set': {"imageType":photo.content_type}})
            return redirect(f'/dashboard/editProfile/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
            
    return redirect(f'/dashboard/editProfile/{memberCode}')

def portFolio_Member_Images(photo):
    from pathlib import Path
    import os
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
            return redirect(f'/dashboard/editProfile/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
    return redirect(f'/dashboard/editProfile/{memberCode}')


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
            return redirect(f'/dashboard/editProfile/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
    return redirect(f'/dashboard/editProfile/{memberCode}')

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
            return redirect(f'/dashboard/editProfile/{memberCode}')
        else:
            return f"Incorrect Password, {member['memberName']} please try again !!"
    return redirect(f'/dashboard/editProfile/{memberCode}')
