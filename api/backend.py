"""Hello World"""
import os
import urlparse
import uuid
from flask import *
import psycopg2
import requests
import json
import urllib
import urllib2

API_KEY = os.environ.get('API_KEY')
BASE_API = 'http://api.reimaginebanking.com'

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

    # The data will be stored in request.form['key']
    # retrieve from there and send response in
    form = request.json
    phone_num = form['phone']
    first_name = form['account_info']['first']
    last_name = form['account_info']['last']
    zip_code = form['account_info']['zip']

    # Use the Nessie API to figure out their id using first/last/zip

    customers = get_request('/customers')
    customers = [x for x in customers if (x['first_name'] == first_name and x['last_name'] == last_name) \
        and x['address']['zip'] == zip_code]

    nessie_api_id = customers[0]['_id']
    auth_token = uuid.uuid4()

    # insert the data into the database
    cur = CONN.cursor()
    cur.execute('INSERT INTO Users Values (\'{0}\', \'{1}\', \'{2}\');'.format(
        str(auth_token), nessie_api_id, phone_num))
    CONN.commit()

    response = make_response('{"auth_token":'+'"{0}"'.format(str(auth_token))+'}')
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/location', methods=['POST'])
def locationUpdate():
    """The user has given us a new data point. see if they are close to a bad place and text them"""
    try:
        # get the data out of the request
        form = request.json
        auth_token = form['auth_token']
        lat = form['lat']
        lng = form['lng']
    
        list_of_places = get_popular_locations_near_me(auth_token, lat, lng)
    except Exception as err:
        return str(err)
    # Now, we want to somehow query data around the User
    # if they are close to any, send a twilio message
    return ''
    

@app.route('/aroundme', methods=['POST'])
def sendLocations():
    """The user has given us a new data point. see if they are close to a bad place and return results"""
    
    # get the data out of the request
    form = request.json
    auth_token = form['auth_token']
    lat = form['lat']
    lng = form['lng']
    
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
    cur.execute('SELECT nesie_id FROM Users WHERE id = \'{0}\';'.format(
        str(auth_token)))

    nessie_id = ''.join(cur.fetchone())
    
    #list_of_merchants = get_request('/merchants', params={'lat':lat, 'lng':lng})

    return []#list_of_merchants

def get_url(path):
    return '{0}{1}?key={2}'.format(BASE_API, path, API_KEY)

def get_request(path, params=None):
    if params:
        params.update({'key': API_KEY})
    else:
        params = {'key': API_KEY}

    url = "%s%s?%s" % (BASE_API, path, urllib.urlencode(params))
    result = urllib2.urlopen(url)
    response_data = result.read()
    return json.loads(response_data)

def post_request(path, payload):
    return requests.post(
        get_url(path),
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
