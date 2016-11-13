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
import collections
from twilio.rest import TwilioRestClient

API_KEY = os.environ.get('API_KEY')
BASE_API = 'http://api.reimaginebanking.com'
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_AUTH = os.environ.get('TWILIO_AUTH')

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

        list_of_places, transactions = get_popular_locations_near_me(auth_token, lat, lng)
        list_of_places = [{
			"name":x['name'],
			"lat":x['geocode']['lat'],
			"lng":x['geocode']['lng'],
			"frequency": sum([1 for y in transactions if y['merchant_id'] == x['_id']]),
			"spent": sum([y['amount'] for y in transactions if y['merchant_id'] == x['_id']])
		} for x in list_of_places]
        place = max(list_of_places, key=getFreq)

        cur = CONN.cursor()
        cur.execute('SELECT Phone_number FROM Users WHERE id = \'{0}\';'.format(
            str(auth_token).strip()))

        phone_num = ''.join(cur.fetchone()).strip()

        # send text message to twilio about place variable
        client = TwilioRestClient(TWILIO_SID, TWILIO_AUTH)
        message = client.messages.create(to="+12316851234", from_="+17652006198",
                                     body=str(place))
    except Exception as err:
        return str(err)
    # Now, we want to somehow query data around the User
    # if they are close to any, send a twilio message
    return ''

def getFreq(d):
    return d['frequency']


@app.route('/aroundme', methods=['POST'])
def sendLocations():
    """The user has given us a new data point. see if they are close to a bad place and return results"""

    # get the data out of the request
    form = request.json
    auth_token = form['auth_token']
    lat = form['lat']
    lng = form['lng']
    limit = form['limit']

    list_of_places, transactions = get_popular_locations_near_me(auth_token, lat, lng)

    list_of_places = ['{\
			"name":"' + '{0}'.format(x['name']) + '",\
			"lat":' + '{0}'.format(x['geocode']['lat']) + ',\
			"lng":' + '{0}'.format(x['geocode']['lng']) + ',\
			"frequency":' + '{0}'.format(sum([1 for y in transactions if y['merchant_id'] == x['_id']])) + ',\
			"spent":' + '{0}'.format(sum([y['amount'] for y in transactions if y['merchant_id'] == x['_id']])) + '\
		}' for x in list_of_places]

    if len(list_of_places) > limit:
        list_of_places = list_of_places[:limit]

    response = make_response('{\
	    "locations":"'+'{0}'.format(str(list_of_places))+'",\
    }')
    response.headers['Content-Type'] = 'application/json'

    return response

def get_popular_locations_near_me(auth_token, lat, lng):
    # Get their nessie id
    cur = CONN.cursor()
    cur.execute('SELECT nesie_id FROM Users WHERE id = \'{0}\';'.format(
        str(auth_token)))

    nessie_id = ''.join(cur.fetchone()).strip()
    if not (nessie_id is not None and nessie_id != ''):
        return [], []

    accounts = get_request('/customers/{0}/accounts'.format(nessie_id))
    if len(accounts) > 0:
        account = accounts[0]
    else:
        return [], []

    account_id = str(account['_id'].strip())

    list_of_merchants = get_request('/merchants', params={'lat':lat, 'lng':lng, 'rad':1}).get('data', [])

    transactions = get_request('/accounts/{0}/purchases'.format(account_id))
    transactions.sort(key=get_merchant_id)

    totals = {}
    for t in transactions:
        totals[t['merchant_id']] = totals.get(t['merchant_id'], 0) + 1

    list_of_merchants = [x for x in list_of_merchants if (x['_id'] in totals.keys()) and (totals[x['_id']] > 10)]

    return list_of_merchants, transactions

def get_merchant_id(d):
    return d['merchant_id']

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
