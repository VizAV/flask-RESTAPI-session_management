from flask import jsonify

# register details check: checking if all the details entered while registering are correct and in proper format or not
def checkDetails(emailId, password, first_name, last_name,mongo):

    # Check if any of the fields are empty : Front end
    # Check if emailformat is correct : front end
    # Check if user alread exists : Backend

    #

    if mongo.db.users.find({'emailId':emailId}).count():
        response = {'message': 'User exists, please login or provide another Email ID', 'status_code': 409}
        return jsonify(response)

    return 0

