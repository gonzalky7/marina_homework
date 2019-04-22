from google.cloud import datastore
import datetime
from flask import request
from flask import Flask, render_template
import json
import constants



app = Flask(__name__)
client = datastore.Client()


@app.route('/')
def index():
    return "Please navigate to /marina to use this API"\


#Will retrieve all information from datastore
@app.route('/marina', methods=['GET'])
def marina_get():
    if request.method == 'GET':
        boats = client.query(kind=constants.boats)
        slips = client.query(kind=constants.slips)
        boats_list = list(boats.fetch())
        slips_list = list(slips.fetch())
        marina = boats_list + slips_list
        return json.dumps(marina)
    else:
        return 'Only GET method is allowed with this URL'


#Retrieving all boat information and Creating new boats
@app.route('/boats', methods=['POST','GET'])
def boats_get_post():
   if request.method == 'POST':
            #Variable "content" is values passed to API to create a boat
            content = request.get_json()
            #Grab all the names in datastore and compare for uniqueness
            query = client.query(kind=constants.boats)
            results = list(query.fetch())
            results_into_list = json.dumps(results)
            #Check if submitted name is unique 
            if str(content["name"]) in results_into_list :
                return "Need to have unique name"
            else:
                new_boat = datastore.entity.Entity(key=client.key(constants.boats))
                new_boat.update({"name": content["name"], "type": content["type"],
                  "length": content["length"]})
                client.put(new_boat)
            return json.dumps(results)
   elif request.method == 'GET' :
     query = client.query(kind=constants.boats)
     results = list(query.fetch())
     return json.dumps(results)
   else:
     return 'Method not recogonized'

#Retrieving all slip information and Creating new slips
@app.route('/slips', methods=['POST','GET'])
def marinas_get_post():
    if request.method == 'POST':
            content = request.get_json()
            new_lodging = datastore.entity.Entity(key=client.key(constants.lodgings))
            new_lodging.update({"name": content["name"], "description": content["description"],
              "price": content["price"]})
            client.put(new_lodging)
            return str(new_lodging.key.id)
    elif request.method == 'GET':
        query = client.query(kind=constants.lodgings)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return json.dumps(results)
    else:
        return 'Method not recogonized'


# @app.route('/lodgings/<id>', methods=['PUT','DELETE'])
# def lodgings_put_delete(id):
#     if request.method == 'PUT':
#         content = request.get_json()
#         lodging_key = client.key(constants.lodgings, int(id))
#         lodging = client.get(key=lodging_key)
#         lodging.update({"name": content["name"], "description": content["description"],
#           "price": content["price"]})
#         client.put(lodging)
#         return ('',200)
#     elif request.method == 'DELETE':
#         key = client.key(constants.lodgings, int(id))
#         client.delete(key)
#         return ('',200)
#     else:
#         return 'Method not recogonized'


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [START gae_python37_render_template]
