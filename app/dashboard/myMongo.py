import pymongo
from bson import Binary
import os

Atlas_string1 = os.getenv("Atlas_string1")
local_client = pymongo.MongoClient(Atlas_string1)
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
    