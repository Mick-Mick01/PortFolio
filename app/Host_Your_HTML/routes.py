from flask import *
from .flask_modules import check_conflicts, mainEditor
import pymongo
import sys
from . import hosting_bp
import keyword

#client = pymongo.MongoClient('mongodb+srv://dev3kha7_8721:YWzwlBcc4swtZEqN@1stcluster.ldsbsgi.mongodb.net/?retryWrites=true&w=majority&appName=1stCluster')

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client['GNIT_Friends_Hosted_Website']


@hosting_bp.route('/', methods=['GET', 'POST'])    # index route is handling a POST request
def form():
#The User will first see form.html page and if a POST operation is made then the user will be directed to /greet route
    if request.method == 'POST':
        new_route_name = request.form['new_route_name']
        if not new_route_name.isidentifier() or keyword.iskeyword(new_route_name):
            return "Please enter a valid route without any symbols, number or spaces. Only Letters."
        
        #checking conflicting routes after checking valid route name
        if not check_conflicts.check_conflicting_route(new_route_name):
            return "Conflicting Route name, please choose a globaly unique name"
        HTMLfile = request.files['HTMLfile']
        
         #Checking if there is any collection_name provided
        if request.form.getlist('Fields[]'):
            collection_name = request.form['collection_name']
            
            #checking conflicting Collections
            collection_list = db.list_collection_names()
            for collection in collection_list:
                if collection_name == collection:
                    return "Conflicting Collection names, please choose a globaly unique name"

            #checking conflicting Routes, but First checked collections
            Array_of_fields = request.form.getlist('Fields[]')
            mainEditor.createRoute(new_route_name, collection_name, Array_of_fields, HTMLfile)
        else:
            collection_name = ""
            Array_of_fields = []
            mainEditor.createRoute(new_route_name, collection_name, Array_of_fields, HTMLfile)
                
    return render_template('HTML_Hosting_Site.html')




    

    
    
                                        
        
