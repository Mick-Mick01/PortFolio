import os 
from pathlib import Path

# Always resolves relative to this file, not to where Python is run
current_dir = Path(__file__).resolve().parent
flask_file_path = current_dir.parent / "routes.py"

app_dir = current_dir.parents[1]
template_path = app_dir / "templates"

def fields_receiving_code(Array_of_fields):
    request_code = f'''
    if request.method == 'POST':
    '''
    for field in Array_of_fields:
        receiving_line = f'''
        {field} = request.form['{field}'] '''
        request_code += receiving_line
    return request_code
#this will provide you the code to receive the fields from HTML page, the code just before the mongoDB code
        
def mongoDB_code_writter(Array_of_fields, collection_name, new_route_name):
    mongoDB_code = f'''
        Collection = db['{collection_name}']
        '''+ f"data = {{\n 'route': '{new_route_name}' " # To initiate the data-dictionary
    for field in Array_of_fields:
        mongoDB_line = f", \n'{field}' : {field}"
        mongoDB_code += mongoDB_line
    mongoDB_code += "\n        }" # To close the data-dictionary
    mongoDB_code += '''
        Collection.insert_one(data)'''

    return mongoDB_code

def createRoute(new_route_name, collection_name, Array_of_fields, HTMLfile):
    #the Array_of_Fields might be an empty list
    if Array_of_fields:
        #this will write the if request.method == 'POST' code
        request_code =  fields_receiving_code(Array_of_fields)
        mongoDB_code = mongoDB_code_writter(Array_of_fields, collection_name, new_route_name)
    else:
        request_code = " "
        mongoDB_code = " "
    
    flask_code = f'''
@hosting_bp.route('/{new_route_name}', methods=['POST', 'GET'])
def {new_route_name}():
    {request_code}
    {mongoDB_code}
    return render_template('{HTMLfile.filename}')
    
    
    '''
    
    with open(flask_file_path, 'r') as f:
        lines = list(f)
        
    lines[len(lines)-3] = flask_code
    
    # Cause while writing the file we can only write a string not a list into a file
    full_flask_code_string = ""
    for line in lines:
        for i in line:
            full_flask_code_string += i 
    
    with open(flask_file_path, 'w') as f:
        f.write(full_flask_code_string)
    
    
    HTMLfile_path = os.path.join(template_path, HTMLfile.filename)

    # Make sure the directory exists first (avoids "No such file or directory" errors)
    os.makedirs(os.path.dirname(HTMLfile_path), exist_ok=True)

    # Now create the file if it doesn't exist
    if not os.path.exists(HTMLfile_path):
        with open(HTMLfile_path, 'w', encoding='utf-8') as f:
            f.write("")  # Creates an empty file
        print(f"Created new file: {HTMLfile_path}")
    else:
        print(f"File already exists: {HTMLfile_path}")
        
    HTMLfile.save(HTMLfile_path)