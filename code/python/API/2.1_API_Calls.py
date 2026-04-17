"""
Exercise 2.1 - API Calls

Go to the API directory on the API Ninja website (make sure you have an account and API key)

    https://api-ninjas.com/api

    Step 1: Choose an API that seems interesting from API Ninja

    STEP 2: Use the code template below and fill in the api_url based on the documentation of your chosen API
            and what you learned in class. Make sure to structure the URL to return the parameters you want.
            Also, make sure you use your API key to return a successful result.

    STEP 3: Parse the return to only display the data you want (if necessary)

    STEP 3: Remove the API key in the code for security, then turn it in.

    Turn in the following:
        1) The code below
        2) Short explanation of which part of the data you parsed for (if multiple parts are returned)

"""
import requests
import json

length = int(input('Enter the length of the password you want: '))

# --- PRACTICE -- MODIFY THE URL BELOW
# --- Structure and make a few of your own API calls below by modifying the api_url
# --- remove the extra URL's if not needed
api_url_1 = 'https://api.api-ninjas.com/v1/passwordgenerator?length={length}'.format(length=length) #I don't have a premium account, so I can't use the premium features of this api.


response = requests.get(api_url_1, headers={'X-Api-Key': ''}) #Replace with YOUR OWN API key


if response.status_code == requests.codes.ok:
    json_data = json.loads(response.text)
    print('Your generated password is: ' + json_data['random_password'])

else:
    print("Error:", response.status_code, response.text) #...or if an error occurs, return error code
