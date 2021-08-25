from flask import Flask
from flask_restful import Api, Resource
from pygame import mixer
import pymongo


# mixer code
mixer.init()
mixer.music.load("sos.wav")
mixer.music.set_volume(0.7)

app = Flask(__name__)
api = Api(app)


def getUserFromUID(uid):
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db_client = mongo_client['scapp_db']


def emergency(uid, location):
    print(f"{uid} is has clicked the sos button, their location is {location}")
    mixer.music.play()


class SOS(Resource):
    def post(self, uid, lat, lng):
        location = []
        location.append(lat)
        location.append(lng)
        emergency(uid, location)


api.add_resource(SOS, "/sos/<string:uid>/<float:lat>/<float:lng>")

if __name__ == "__main__":
    app.run(debug=True)
