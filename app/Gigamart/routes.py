from flask import *
from . import myMongo
import pymongo
from . import Gigamart_bp


# client = pymongo.MongoClient('mongodb://localhost:27017')
Atlas_string1 = "mongodb+srv://dev3kha7_8721:YWzwlBcc4swtZEqN@1stcluster.ldsbsgi.mongodb.net/"
client = pymongo.MongoClient(Atlas_string1)

@Gigamart_bp.route('/upload_shop', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        shopName = request.form['shopName']
        ownerName = request.form['ownerName']
        stallNumber = request.form['stallNumber']
        mobile = request.form['mobile']
        openHours = request.form['openHours']
        shopImage = request.files['shopImage']
        ownerImage = request.files['ownerImage']
        shopType = request.form['shopType']
        marketName = request.form['marketName']

        myMongo.uploadShop(shopName, ownerName, stallNumber, mobile, openHours, shopImage, ownerImage, shopType, marketName)
        return redirect('/Gigamart/upload_shop')

    markets = pymongo.MongoClient('mongodb://localhost:27017').list_database_names() 
    return render_template('upload_shop.html', markets=markets)



@Gigamart_bp.route('/list', methods=['GET', 'POST']) 
def form2():
    if request.method == 'POST':
        marketName = request.form['marketName']
        return redirect(f'/Gigamart/market/{marketName}')
    return render_template('market_list_current.html')

@Gigamart_bp.route('/market/<marketName>', methods=['GET', 'POST']) 
def market(marketName):
    market_name = marketName
    db = client[marketName]
    categories = db.list_collection_names()
    shops_by_category = list()

    for category in categories:
        shops = list(db[category].find())
        shops_by_category.append(shops)
    
    coll = db["info"]
    docs = list(coll.find())
    info_doc = docs[0] #The 0th document in the info collection contains information of the market, that collection only has one Document

    return render_template('market.html', categories=categories, shops_by_category=shops_by_category, marketName=marketName, info=info_doc)

@Gigamart_bp.route('/shop/<marketName>/<shopName>', methods=['GET', 'POST']) 
def shop(marketName, shopName):
    db = client[marketName]
    collections = db.list_collection_names()
    
    for collection in collections:
        shop = db[collection].find_one({ "shopName":shopName })
        if shop:
            return render_template('shop.html', shop=shop, marketName=marketName)

    return render_template('shop.html')


@Gigamart_bp.route('/streamShopImage/<marketName>/<filename>', methods=['POST', 'GET'])
def streamShopImage(marketName, filename):
    db = client[marketName]
    categories = db.list_collection_names()
    for category in categories:
        image = db[category].find_one({ "shopImageName":filename })
        if image:
            return Response(image['shopImage'], content_type=image['shopImageContentType'])
    return None 

@Gigamart_bp.route('/streamOwnerImage/<marketName>/<filename>', methods=['POST', 'GET'])
def streamOwnerImage(marketName, filename):
    db = client[marketName]
    categories = db.list_collection_names()
    for category in categories:
        image = db[category].find_one({ "ownerImageName":filename })
        if image:
            return Response(image['ownerImage'], content_type=image['ownerImageContentType'])
    return None 

@Gigamart_bp.route('/items_page')
def items_page():
    return render_template("items_page.html")