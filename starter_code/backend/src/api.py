import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    try:
        all_drinks = Drink.query.order_by(Drink.id).all()
        drinks = [drink.short() for drink in all_drinks]

        return jsonify({
            'staus_code': 200,
            'success': True,
            'drinks': drinks,

        })
    except Exception as e:
        print(e)
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    try:
        all_drinks = Drink.query.order_by(Drink.id).all()
        print(all_drinks)
        drinks = [drink.long() for drink in all_drinks]

        return jsonify({
            'staus_code': 200,
            'success': True,
            'drinks': drinks,

        })
    except Exception as e:
        print(e)
        abort(404)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    try:
        body = request.json
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        if isinstance(new_recipe, dict):
            new_recipe = [new_recipe]

        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

        new_drink.insert()

        return jsonify({
            'status_code': 200,
            'success': True,
            'drinks': new_drink.long(),
        })

    except Exception as e:
        print(e)
        abort(404)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id): 
    try:
        body = request.json
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        if new_title:
            drink.title = new_title
        if new_recipe:
            drink.recipe = json.dumps(new_recipe)

        drink.update()

        return jsonify({
            'success': True,
            'status_code': 200,
            'drinks': [drink.long()],
        })

    except Exception as e:
        print(e)
        abort(404)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'status_code': 200,
            'delete': drink_id,
        })
    except Exception as e:
        print(e)
        abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Authentication error"
    }), 401


@app.errorhandler(403)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Permission not found"
    }), 403

@app.errorhandler(AuthError)
def handle_auth_error(auth_err):
    """
    Receive the raised authorization error and propagates it as response
    """
    response = jsonify(auth_err.error)
    response.status_code = auth_err.status_code
    return response