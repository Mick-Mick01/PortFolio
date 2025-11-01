import pymongo
from bson import Binary
from .small_libraries import *

client = pymongo.MongoClient('mongodb://localhost:27017')

def uploadShop(shopName, ownerName, stallNumber, mobile, openHours, shopImage, ownerImage, shopType, marketName):
    data = {
        "shopName":shopName,
        "ownerName":ownerName,
        "stallNumber":stallNumber,
        "mobile":mobile,
        "openHours":openHours,
        "shopType":shopType,
        "marketName":marketName,
        
        #//Files are sent from the HTML page as an object
        "shopImageName":shopImage.filename,
        "shopImageContentType":shopImage.content_type,

        "ownerImageName":ownerImage.filename,
        "ownerImageContentType":ownerImage.content_type,

    }

    # 1. Creating a hexaDecimal depending on the shop's Data (without image binary)
    shopId = uniqueID.unique_ShopItemId(data)  

    # 2. Creating an index of shopId 
    db = client[marketName]
    collection = db[shopType]
    collection.create_index([("shopId", pymongo.ASCENDING)], unique=True)

    
    # 3. Decresing the size of the image if more than 3MB
    shop_reduced_Image = imageCompress.reduce_image_size(shopImage, max_size_mb=3)
    owner_reduced_Image = imageCompress.reduce_image_size(ownerImage, max_size_mb=3)

    # 4. Actual shop data that will be uploaded to the DB
    shopData = {
        "shopName":shopName,
        "ownerName":ownerName,
        "stallNumber":stallNumber,
        "mobile":str(mobile),
        "openHours":openHours,
        "shopType":shopType,
        "marketName":marketName,
        "shopId":shopId,
        
        #//Files are sent from the HTML page as an object
        "shopImage":Binary(shop_reduced_Image.read()),
        "shopImageName":shopImage.filename,
        "shopImageContentType":shopImage.content_type,

        "ownerImage":Binary(owner_reduced_Image.read()),
        "ownerImageName":ownerImage.filename,
        "ownerImageContentType":ownerImage.content_type,
    }

    # 5. Inserting shop-data into the DB
    # Including the shop&owner Images as a Binary (Wont take much space)(Owner and Shop image will be clicked by our staff's phone and not a camera)
    collection.insert_one(shopData)
    print(marketName, shopType, mobile)





def upload_item(itemName, discription, shopId, imageList, videoList, marketName):
    data = {
        "itemName": itemName,
        "discription": discription,
        "shopId":shopId,
        "imageList":imageList,
        "videoList":videoList
    }

    shopId = uniqueID.uniqueShop_ItemId(data)    #//Creating a hexaDecimal depending on the shop's Data
    db = client[marketName]
    shopType="Hero"
    collection = db[shopType]
    collection.create_index(["shopId", pymongo.AScENDING], unique=True)