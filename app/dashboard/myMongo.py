import pymongo
from bson import Binary

Atlas_string1 = "mongodb+srv://dev3kha7_8721:YWzwlBcc4swtZEqN@1stcluster.ldsbsgi.mongodb.net/"
Atlas_string2 = "mongodb://dev3kha7_8721:YWzwlBcc4swtZEqN@ac-0x74grp-shard-00-00.ldsbsgi.mongodb.net:27017,ac-0x74grp-shard-00-01.ldsbsgi.mongodb.net:27017,ac-0x74grp-shard-00-02.ldsbsgi.mongodb.net:27017/?ssl=true&replicaSet=atlas-74grp-shard-0&authSource=admin&retryWrites=true&w=majority&appName=1stCluster"

local_client = pymongo.MongoClient("mongodb://localhost:27017")
local_db = local_client['PortFolio']


def uploadProject(category, projectName, memberCode, projectLink, image, discription, HTMLcode, projectCode):
    data = {
        "category":category,
        "projectName":projectName,
        "memberCode":memberCode,
        "projectLink":projectLink,
        "imageName":image.filename, 
        "imageType":image.content_type,
        "imageContent":Binary(image.read()),
        "discription":discription,
        "HTMLcode":HTMLcode,
        "projectCode":projectCode
    }
    print("$$$$$$$$$$$", category, "$$$$$$$$")
    local_db[category].insert_one(data)
    