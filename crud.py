import pymongo
import base64
import json
from pymongo import MongoClient
from random import randint
from flask import Flask
from flask_restful import Api, Resource

userdbflaskapp = Flask(__name__)
userdbflaskapi = Api(userdbflaskapp)

# uid, mode, userDetailsJson

def parseData(payload):
    base64_bytes = payload.encode("utf-8")  
    json_data_string_bytes = base64.b64decode(base64_bytes)
    json_data_string = json_data_string_bytes.decode("utf-8")
    json_data_dict = json.loads(json_data_string)

    return json_data_dict  
    # json_data_dict['uid'],json_data_dict['name'],json_data_dict['address'], json_data_dict['aadhar'],json_data_dict['dob'],json_data_dict['age'],json_data_dict['gender'],json_data_dict['bloodgroup'],json_data_dict['mobile'],json_data_dict['diseases'],json_data_dict['hospital'],json_data_dict['emergencyname'],json_data_dict['emergencynumber'],json_data_dict['caretakername'],json_data_dict['caretakernumber'],json_data_dict['relativename'],json_data_dict['relativenumber'],json_data_dict['relativeaddress']



class UserCRUD(Resource):
    def post(self, mode, payload):
        if mode == "create":
            
            userDetailsJson = parseData(payload)
            insertUserReturnObj = insertUser(userDetailsJson)
            if insertUserReturnObj == -1:
                return {
                    'operation': insertUserReturnObj,
                    'comments': 'user already exists'
                    }

            return {
                'operation': insertUserReturnObj,
                'comments': 'successs, new user created'
            }

        elif mode == 'update':
            userDetailsJson = parseData(payload)
            updateOperation = updateUserInfo(userDetailsJson)
            
            if updateOperation == 1:
                return {
                'operation': updateOperation,
                'comments': 'user fields updated'
            }
            elif updateOperation == -1:
                return {
                    'operation': updateOperation,
                    'comments': 'user with uid was not found'
                }

        elif mode == 'delete':
            userDetailsJson = parseData(payload)
            deleteUserReturnObj = deleteUser(userDetailsJson['uid'])
            if deleteUserReturnObj == -1:
                return {
                    'operation': deleteUserReturnObj,
                    'comments': 'user does not exist'
                }
            return {'operation' : deleteUserReturnObj,
                    'comments': 'sucess, user deleted'
                }



# userdbflaskapi.add_resource(UserCRUD, '/CRUD/<string:mode>/<string:uid>/<string:name>/<string:rmn>/<string:blood_group>/<string:e_contactname>/<string:e_contactnum>/<string:aadharnum>')
userdbflaskapi.add_resource(UserCRUD, '/CRUD/<string:mode>/<string:payload>')


#constants 
db_name = "sc_app"
db_col_name = "Users"

#pymongo init to get handle of collections object
def pymongo_init():
    mongo_client = pymongo.MongoClient("mongodb+srv://Aaryadev:aurora1127@cluster0.jvar5.mongodb.net/sc_app?retryWrites=true&w=majority")
    if db_name in mongo_client.list_database_names():
        db_obj = mongo_client[db_name]
        try:
            db_col_obj = db_obj[db_col_name]
            return db_col_obj
        except (IndexError, KeyError):
            print("Collection does not exist in database, major error...contact ISA MPSTME")
            exit(0)        
    else:
        print("Database doesn't exist in list of databases, major error...contact ISA MPSTME")
        exit(0)

# checks if a user has been already added in the db and the user is attempting to create a new record
# checks if a record with the user's aadhar number already exists 
def checkRepeatedUser(db_col_obj, aadharnum_to_check):
    for i in db_col_obj.find():
        if i['aadhar'] == aadharnum_to_check:
            return -1
    return 1


# checks if by some odd chance the randomly generated UID already exists
def checkRepeatedUID(uid, db_col_obj):
    for i in db_col_obj.find():
        if i['uid'] == uid:
            return -1
    return 1

def generatUID(db_col_obj):
    uid = randint(1000000, 9999999)
    if checkRepeatedUID(uid, db_col_obj) == -1:
        generatUID()
    return uid


def insertUser(userDetailsJson):
    db_col_obj = pymongo_init()

    
    if checkRepeatedUser(db_col_obj, userDetailsJson['aadhar']) == -1:
        print("User has previously made account")
        return -1

    else:
        
        user_uid = generatUID(db_col_obj)
# json_data_dict['uid'],json_data_dict['name'],json_data_dict['address'], json_data_dict['aadhar'],json_data_dict['dob'],json_data_dict['age'],json_data_dict['gender'],json_data_dict['bloodgroup'],json_data_dict['mobile'],json_data_dict['diseases'],json_data_dict['hospital'],json_data_dict['emergencyname'],json_data_dict['emergencynumber'],json_data_dict['caretakername'],json_data_dict['caretakernumber'],json_data_dict['relativename'],json_data_dict['relativenumber'],json_data_dict['relativeaddress']
        insert_obj = {"uid":str(user_uid), "name":userDetailsJson['name'], "address": userDetailsJson['address'], 
        "aadhar":userDetailsJson['aadhar'], "dob": userDetailsJson['dob'], "age": userDetailsJson['age'], 
        "gender": userDetailsJson['gender'], "bloodgroup": userDetailsJson['bloodgroup'], "mobile": userDetailsJson['mobile'],
        "diseases": userDetailsJson['diseases'], "hospital": userDetailsJson['hospital'], "emergencyname": userDetailsJson['emergencyname'],
        "emergencynumber": userDetailsJson['emergencynumber'], "caretakername": userDetailsJson['caretakername'], 
        "caretakernumber": userDetailsJson['caretakernumber'], "relativename": userDetailsJson['relativename'],
        "relativename": userDetailsJson['relativename'], "relativeaddress": userDetailsJson['relativeaddress']}
        
        db_col_obj.insert_one(insert_obj)
        print(f"\n\nNew User Added -> {userDetailsJson['uid']}")
        return 1
        # print(f"UID: {insert_obj['uid']}")
        # print(f"Name: {insert_obj['name']}")
        # print(f"Registered Mobile Number: {insert_obj['rmn']}")
        # print(f"Blood Group: {insert_obj['blood_group']}")
        # print(f"Name: {insert_obj['e_contactname']}")
        # print(f"Name: {insert_obj['e_contactnum']}")
        # print(f"Aadhar number: {insert_obj['aadharnum']}")


# update user functionalities

def updateUserInfo(userDetailsJson):

    found_flag = -1

    db_col_obj = pymongo_init()

    for i in db_col_obj.find():
        if i['uid'] == userDetailsJson['uid']:
            found_flag = 1
            
            myquery = { "uid": userDetailsJson['uid']}
            newvalues = { "$set": {"uid":userDetailsJson['uid'], "name":userDetailsJson['name'], "address":userDetailsJson['address'], 
            "dob":userDetailsJson['dob'], 
            "age":userDetailsJson['age'], "gender":userDetailsJson['gender'], "bloodgroup":userDetailsJson['bloodgroup'], "mobile": userDetailsJson['mobile'],
            "diseases": userDetailsJson['diseases'], "hospital": userDetailsJson['hospital'], "emergencyname": userDetailsJson['emergencyname'],
            "emergencynumber": userDetailsJson['emergencynumber'], "caretakername": userDetailsJson['caretakername'], 
            "caretakernumber": userDetailsJson['caretakernumber'], "relativename": userDetailsJson['relativename'], "relativenumber": userDetailsJson['relativenumber'],
            "relativeaddress": userDetailsJson['relativeaddress']}}
            db_col_obj.update_one(myquery, newvalues)

    if found_flag == -1:
        print(f"\n\nUser with UID {userDetailsJson['uid']} was not found")
        return found_flag

    elif found_flag == 1:
        print(f"User details updated -> {userDetailsJson['uid']}")
        return found_flag



def deleteUser(uid):
    found_flag = -1

    db_col_obj = pymongo_init()

    for i in db_col_obj.find():
        if i['uid'] == uid:
            found_flag = 1
            
            myquery = { "uid": uid}
            # newvalues = { "$set": {"uid":int(uid), "name":name, "rmn":rmn, "blood_group":blood_group, "e_contactname":e_contactname, 
            # "e_contactnum":e_contactnum, "aadharnum":aadharnum} }
            db_col_obj.delete_one(myquery)

    if found_flag == -1:
        print(f"\n\nUser with UID {uid} was not found")
        return -1

    elif found_flag == 1:
        print(f"User deleted -> {uid}")

# insertUser("Aaryadev Chandra", 9711155179, "B+ve", "Swati Chandra", 9819902423, 123456778912)
# updateUSerInfo(7735054, "chandra aaryadev", 9711155179, "B+ve", "Swati Chandra", 9819902423, 123456778912)

userdbflaskapp.run(debug=True)


