from flask import Flask
from flask_restful import Api, Resource
from pygame import mixer
import pymongo
import tkinter
import threading

# mixer code
mixer.init()
mixer.music.load("sos.wav")
mixer.music.set_volume(0.7)

app = Flask(__name__)
api = Api(app)

#constants dangerous
db_name = "sc_app"
db_col_name = "Users"

def googleMapsLinkGenerator(location):
    link = f"www.google.com/maps/place/{location[0]},{location[1]}/"
    return link

def getUserFromUID(uid):
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    if db_name in mongo_client.list_database_names():
        db_obj = mongo_client[db_name]
        try:
            db_col_obj = db_obj[db_col_name]
        except (IndexError, KeyError):
            print("Collection does not exist in database, major error...contact ISA MPSTME")
            exit(0)

        query = {'uid':uid}
        results = db_col_obj.find(query)
        for i in results:
            # print(i)
            return i['name']
    else:
        print("Database doesn't exist in list of databases, major error...contact ISA MPSTME")
        exit(0) 


def emergency(uid, location):
    fn = getUserFromUID(uid)
    print(f"{fn} is has clicked the sos button, their location is {googleMapsLinkGenerator(location)}")
    mixer.music.play()


class SOS(Resource):
    def post(self, uid, lat, lng):
        location = []
        location.append(lat)
        location.append(lng)
        emergency_thread = threading.Thread(target=emergency, args=(uid, location))        
        emergency_thread.start()
        emergency_thread.join()

api.add_resource(SOS, "/sos/<string:uid>/<float:lat>/<float:lng>")

if __name__ == "__main__":
    app.run(debug=True)