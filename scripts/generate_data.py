import requests
import json
import pprint
import random
from secret import CAP_ONE_API_KEY

API_KEY = CAP_ONE_API_KEY
BASE_API = 'http://api.reimaginebanking.com'
pp = pprint.PrettyPrinter(indent=4)

STATES = {
    'Arizona': 'AZ',
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

# the customers we're working with
CUSTOMER_IDS = ['58274805360f81f104547a55',
                '58274805360f81f104547a57',
                '58274805360f81f104547a59',
                '58274806360f81f104547a5b',
                '58274806360f81f104547a5d',
                '58274410360f81f104547a26',
                '582743fc360f81f104547a25']

# the merchants we're working with
MERCHANT_IDS = ['57cf75cfa73e494d8675f928', # Panera
                '57cf75cfa73e494d8675f8f1', # Boutique Bella
                '57cf75cfa73e494d8675f972', # Fido
                '57cf75cfa73e494d8675f8f7', # Starbucks
                '57cf75cfa73e494d8675f8d8', # Urban Outfitters
                '57cf75cfa73e494d8675f924', # Urban Grub
                '58275242360f81f104547af6', # Belcourt Theatre
                '58275272360f81f104547afa', # Blush
                '58275286360f81f104547afc', # HG Hill Urban Market
                '57cf75cfa73e494d8675f8cf', # Ryman Auditorium
                '57cf75cfa73e494d8675f8d3' # Nashville Farmers' Market
                ]

ACCOUNT_IDS =  ['58278ede360f81f104548915',
                '58278ede360f81f104548916',
                '58278ede360f81f104548917',
                '58278ede360f81f104548919',
                '58278ede360f81f10454891a',
                '58278ede360f81f10454891b',
                '58278ede360f81f10454891d']

# purchase thresholds
CATEGORY_THRESHOLDS = { 'Coffee': [4.00, 10.00],
                        'cafe': [4.00, 10.00],
                        'clothing_store': [20.00, 150.00],
                        'restaurant': [10.00, 30.00],
                        'Entertainment': [10.00, 100.00],
                        'Shopping': [20.00, 150.00],
                        'Groceries': [25.00, 100.00]
                        }

def get_url(path):
    return '%s%s?key=%s' % (BASE_API, path, API_KEY)

def get_request(path):
    return requests.get(get_url(path)).json()

def post_request(path, payload):
    return requests.post(
        get_url(path),
        data=json.dumps(payload),
        headers={'content-type':'application/json'}
    )

def get_customers():
    counter = 0
    url = get_url('/customers')

    cust_names = ['Emily', 'Huynh',
                'Jake', 'Zarobsky',
                'Andrew', 'Thomas',
                'Steve', 'Eastcott',
                'Scott', 'Carl',
                'Jane', 'Doe',
                'John', 'Smith',
                'Joseph', 'Gordon-Levitt',
                'Emma', 'Watson',
                'Adam', 'Tremtone']

    for cust in data['results']:

        if counter == 10:
            break

        # make sure we have all the address fields
        if len(cust['address']) == 5:
            cust_data = {
                'first_name': cust_names[counter],
                'last_name': cust_names[counter + 1],
                'address': {
                    'street_number': cust['address']['street_number'],
                    'street_name': cust['address']['street_name'],
                    'city': cust['address']['city'],
                    'state': STATES[cust['address']['state']],
                    'zip': cust['address']['zip']
                }
            }
        else:
            continue

        # create the customer
        response = requests.post(
        	url,
        	data=json.dumps(cust_data),
        	headers={'content-type':'application/json'},
        )

        # ensure it worked
        if response.status_code == 201:
        	print('account created')
        else:
            print(response.status_code)
            print(response)

        counter += 1

# /customers/{id}/accounts
def create_accounts():
    for cust in CUSTOMER_IDS:
        account = {
            'type': 'Checking',
            'nickname': 'main',
            'rewards': random.randint(1000, 2000),
            'balance': round(random.uniform(20000, 30000), 2)
        }
        path = '/customers/%s/accounts' % (cust)
        response = post_request(path, account)

        # ensure we created the account
        if response.status_code == 201:
            print('account created')
        else:
            print(response.status_code)
            print(response.json())

# http://api.reimaginebanking.com/accounts/{id}/purchases?key={API_KEY}
def create_purchases():

    # for each customer account
    for acc_id in ACCOUNT_IDS:

        # create 100 purchases
        for i in range(100):
            # randomize merchant
            merchant_id = random.choice(MERCHANT_IDS)

            # get merchant categories
            path = '/merchants/%s' % (merchant_id)
            merchant_data = get_request(path)
            categories = merchant_data['category']

            # generate purchase amount
            amount = 0
            for cat in categories:
                if cat in CATEGORY_THRESHOLDS:
                    thresholds = CATEGORY_THRESHOLDS[cat]
                    amount = round(random.uniform(thresholds[0], thresholds[1]), 2)

                    # create post request for purchase
                    purchase = {
                        'merchant_id': merchant_id,
                        'medium': 'balance',
                        'purchase_date': '2016-11-' + str(random.randint(1, 12)),
                        'amount': amount
                    }

                    path = '/accounts/%s/purchases' % (acc_id)
                    response = post_request(path, purchase)

                    if response.status_code == 201:
                        print('purchase created')
                    else:
                        print(response.status_code)
                        print(response.json())


# create_accounts()
# create_purchases()
# don't you dare run this again or you'll get more duplicate customers
# get_customers()
