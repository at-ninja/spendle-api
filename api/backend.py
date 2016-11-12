"""Hello World"""
import os
import urlparse
import uuid
from flask import *
import psycopg2

urlparse.uses_netloc.append("postgres")
URL = urlparse.urlparse(os.environ["DATABASE_URL"])

CONN = psycopg2.connect(
    database=URL.path[1:],
    user=URL.username,
    password=URL.password,
    host=URL.hostname,
    port=URL.port
)

app = Flask(__name__)


@app.route('/user', methods=['POST'])
def generate_user():
    """Generate a new user and return the """
    try:
        # The data will be stored in request.form['key']
        # retrieve from there and send response in
        form = request.json
        phone_num = form['phone']
        first_name = form['account_info']['first']
        last_name = form['account_info']['last']
        zip_code = form['account_info']['zip']

        # Use the Nessie API to figure out their id using first/last/zip

        nessie_api_id = ""
        auth_token = uuid.uuid4()

        # insert the data into the database
        cur = CONN.cursor()
        cur.execute('INSERT INTO Users Values (\'{0}\', \'{1}\', \'{2}\');'.format(
            str(auth_token), nessie_api_id, phone_num))
        CONN.commit()

        response = make_response('{"auth_token":'+'"{0}"'.format(str(auth_token))+'}')
        response.headers['Content-Type'] = 'application/json'

        return response
    except Exception as e:
        return e.message

@app.route('/location', methods=['POST'])
def locationUpdate():
    """The user has given us a new data point. see if they are close to a bad place and text them"""
    
    # get the data out of the request
    form = request.json
    auth_token = form['auth_token']
    lat, lng = form['lat'], form['lng']
    
    list_of_places = get_popular_locations_near_me(auth_token, lat, lng)

    # Now, we want to somehow query data around the User
    # if they are close to any, send a twilio message
    return

@app.route('/aroundme', methods=['POST'])
def sendLocations():
    """The user has given us a new data point. see if they are close to a bad place and return results"""
    
    # get the data out of the request
    form = request.json
    auth_token = form['auth_token']
    lat, lng = form['lat'], form['lng']
    
    list_of_places = get_popular_locations_near_me(auth_token, lat, lng)

    list_of_places = ['{\
			"name":"Some name",\
			"lat": 0.0,\
			"lng": 0.0,\
			"frequency":1,\
			"spent":0.0\
		}' for x in list_of_places]

    response = make_response('{\
	    "locations":"{0}",\
    }'.format(str(list_of_places)))
    response.headers['Content-Type'] = 'application/json'

    return response

def get_popular_locations_near_me(auth_token, lat, lng):
    # Get their nessie id
    cur = CONN.cursor()
    cur.execute('SELECT nesie_id FROM Users WHERE id = \'{0}\''.format(
        str(auth_token)))
    
    nessie_id = ''.join(cur.fetchone())

    list_of_places = []

    return list_of_places

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
