import pymongo
from flask import *
import os

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['PortFolio-Confidential'] 

# This collection is to store data of Members
Collection1 = db['Members']

app = Flask(__name__)

HTML = ''' 
<head>
    <title>Add Member</title>
</head>
<body>
    <form action="/" method="post" id="my-form" enctype="multipart/form-data">
        <input type="text" name="memberName" placeholder="Name" required> <br>
        <input type="text" name="collegeCode" placeholder="college code" required> <br>
        <input type="text" name="course_Roll" placeholder="course-roll" required> <br>
        <input type="text" name="memberPost"  placeholder="member post" required> <br>
        <input type="file" name="memberImage" required> <br>
        <input type="text" name="memberCode" placeholder="member code" required> <br>
        <input type="text" name="memberPassCode" placeholder="password" required> <br>
        <button type="submit">submit</button>
        <br>
        <button type="button" onclick="addField()">+AddCategory</button>
    </form>

    <script>
        function addField(){
            const category = document.createElement('input');
            const form = document.getElementById('my-form');
            category.setAttribute('type', 'text');
            category.setAttribute('placeholder', 'Category Name');
            category.setAttribute('name', 'categories[]');

            form.append(document.createElement('br'));
            form.append(category);
        }
        function addDoc(){
            const category = document.createElement('input');
            const form = document.getElementById('my-form');
            category.setAttribute('type', 'text');
            category.setAttribute('placeholder', 'Document Name');
            category.setAttribute('name', 'documents[]');

            form.append(document.createElement('br'));
            form.append(category);
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['POST', 'GET'])
def Home():
    if request.method == 'POST':
        memberName = request.form.get("memberName")
        collegeCode = request.form.get("collegeCode")
        course_Roll = request.form.get("course_Roll")
        memberPost = request.form.get("memberPost")
        memberImage = request.files.get("memberImage")
        memberCode = request.form.get("memberCode")
        passwd = request.form.get("memberPassCode")
        categories = request.form.getlist('categories[]')
        documents = request.form.getlist('documents[]')
        
        data = {
            "memberName":memberName,
            "collegeCode":collegeCode,
            "course_Roll":course_Roll,
            "memberPost":memberPost,
            "memberCode":memberCode,
            "memberImageName":memberImage.filename,
            "memberImageContent": "Storing image into static/images/portFolio...",
            "memberImageType":memberImage.content_type,
            "passwd":passwd,
            "categories":categories,
            "documents":documents
        }
        Collection1.insert_one(data)
        
        #After storing the data into mongoDB we store the image into static/images/portFolio_images folder
        save_directory = "C:\\Users\\User\\Desktop\\Bash,Flask,MongoDB,Website-PROJECTS\DEPLOYEBLE_PORTFOLIO_VERSION_2.0\\app\\static\\images\\portFolio_Member_Images"
        save_filename = memberImage.filename
        full_save_path = os.path.join(save_directory, save_filename)
        os.makedirs(save_directory, exist_ok=True)
        memberImage.save(full_save_path)
    return HTML

app.run(debug=True)