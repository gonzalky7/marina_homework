from google.cloud import datastore
from datetime import datetime
from datetime import time
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
            return ('', 200)
   elif request.method == 'GET' :
     query = client.query(kind=constants.boats)
     results = list(query.fetch())
     for e in results:
        e["id"] = e.key.id
     return json.dumps(results)
   else:
     return 'Method not recogonized'

#Retrieving all slip information and Creating new slips
@app.route('/slips', methods=['POST','GET'])
def slips_get_post():
    if request.method == 'POST':
            #Variable "content" is values passed to API to create a boat
            content = request.get_json()
            #Grab all the number of slips in datastore and compare for uniqueness
            query = client.query(kind=constants.slips)
            query.add_filter('number', '=', content["number"])
            results = list(query.fetch())
            # print results[0].id
            # print results
            # print len(results)
            #Check if submitted name is unique 
            if len(results) >= 1:
                return "Need to have unique number"
            else:
                new_slip = datastore.Entity(key=client.key(constants.slips))
                new_slip.update({
                    "number": content["number"],
                    "arrival_date": content["arrival_date"],
                    "current_boat": False,                
                })
                client.put(new_slip)
                return "slip created"
    elif request.method == 'GET':
      query = client.query(kind=constants.slips)
      results = list(query.fetch())
      for e in results:
        e["id"] = e.key.id
      return json.dumps(results)
    else:
      return 'Method not recogonized'


@app.route('/boats/<id>', methods=['PUT','DELETE', 'GET'])
def boats_get_put_delete(id):
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        #Still need to check that name is unique
        query = client.query(kind=constants.boats)
        query.add_filter('name', '=', content["name"])
        results = list(query.fetch())
        if len(results) >= 1:
            return "Need to have unique number"
        else:
            boat.update({
                "name": content["name"], 
                "type": content["type"],
                "length": content["length"]
            })
            client.put(boat)
            return ('',200)
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        first_key = client.key(constants.boats, int(id))
        print first_key
        query.key_filter(first_key, '=')
        results = list(query.fetch())
        for e in results:
            e["url"] = "https://week-3-marina.appspot.com/boats/" + str(id)
        return json.dumps(results)
    elif request.method == 'DELETE':
        #Deleting a boat should empty the slip the ship was in
        #Query the slips for the boat KEY/ID then replace value with false
        query = client.query(kind=constants.slips)
        query.add_filter('current_boat', '=', int(id))
        results = list(query.fetch())

        if len(results) >= 1:
            #Returned a slip that contains the id of the boat that is trying to be deleted
            #Delete the current boat ID and replace with false
            for e in results:
                slip_key = e.key.id
            slip_to_change = client.key(constants.slips, int(slip_key))
            slip = client.get(key =slip_to_change)
            slip.update({
                "current_boat": False, 
            }) 
            client.put(slip)
        key = client.key(constants.boats, int(id))
        client.delete(key)
        return ('',200)
    else:
        return 'Method not recogonized'

@app.route('/slips/<id>', methods=['PUT','DELETE', 'GET'])
def slips_put_delete(id):
    if request.method == 'PUT':
        content = request.get_json()
        slip_key = client.key(constants.slips, int(id))
        slip = client.get(key=slip_key)
        #Still need to check that number of slip is unique
        query = client.query(kind=constants.slips)
        query.add_filter('number', '=', content["number"])
        results = list(query.fetch())
        if len(results) >= 1:
            return "Need to have unique number"
        else:
            slip.update({
                "number": content["number"], 
                "current_boat": content["current_boat"],
                "arrival_date": content["arrival_date"]
            })
            client.put(slip)
            return ('',200)
    elif request.method == 'DELETE':
        key = client.key(constants.slips, int(id))
        client.delete(key)
        return ('',200)
    elif request.method == 'GET':
        #If slip is occupied with a boat have to show live URL link of boat

        #Query to get all slips entities from datastore
         query = client.query(kind=constants.slips)
         query.key_filter(first_key, '=')
         results = list(query.fetch())

         #Only way I could find to get specific property values from query
         #Need to get boat ID
         first_key = client.key(constants.slips, int(id))
         entity = datastore.Entity(key=first_key)
         entity_keys = client.get(first_key)
        
         result = {}
         for item in entity_keys:
            result[item] = entity_keys[item]
            current_boat_id = result['current_boat']
         if current_boat_id == False:
            # print "No boat assigned to slip"
            for e in results:
               e["url_slip"] = "https://week-3-marina.appspot.com/slips/" + str(id)
            return json.dumps(results)
         else:
            for e in results:
               e["url_slip"] = "https://week-3-marina.appspot.com/slips/" + str(id)
               e["url_of_occupied_boat"] = "https://week-3-marina.appspot.com/boats/" + str(current_boat_id)
               return json.dumps(results)
    

#A boat should be able to arrive and be assigned a slip number specified in the request
#No automatically assigning boats to slips
#If the slip is occupied the server should return an Error 403 Forbiden message
@app.route('/slip/<slip_id>/boat/<boat_id>', methods=['POST'])
def boat_post_slip(slip_id, boat_id):
    if request.method == 'POST':
        print int(slip_id)
        print int(boat_id)
        
        #Need to query slip with id passed

    else:
        return 'Method not recogonized'




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
