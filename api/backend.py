import os
from flask import *

app = Flask(__name__)

@app.route('/user', methods=['POST'])
def generate_user():
    """Generate a new user and return the """
    
    # The data will be stored in request.form['key']
    # retrieve from there and send response in
    form = request.form
    phone_num = form['phone']
    first_name = form['account_info']['first']
    last_name = form['account_info']['last']
    zip_code = form['account_info']['zip']

    response = make_response('{\
	    "auth_token":"guid",\
	    "message":null\
	    "status": 200\
    }')
    response.headers['Content-Type'] = 'application/json'
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
