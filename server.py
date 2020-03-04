#! python3
from flask import Flask, jsonify, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from validate_email import validate_email
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'api_rest_blog'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/api_rest_blog'
app.config['JWT_SECRET_KEY'] = 'secret'


mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

CORS(app)


@app.route('/users/register', methods=['POST'])
def register():
    users = mongo.db.users
    nombre = request.get_json()['nombre']
    apellido = request.get_json()['apellido']
    email = request.get_json()['email']
    rol = request.get_json()['rol']
    telefono = request.get_json()['telefono']
    direccion = request.get_json()['direccion']
    dni = request.get_json()['dni']

    password = bcrypt.generate_password_hash(
    request.get_json()['password']).decode('utf-8')
    is_valid = validate_email(email,verify=True)
    is_numerico= telefono.isdigit()


    access_token = create_access_token(identity={
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'password': password,
                'rol': rol,
                'telefono': telefono,
                'direccion': direccion,
                'dni': dni
            })
          
    validDni=False
    letraControl = dni[8]
  
    if dni[:8].isdigit() and  letraControl.isalpha():
        validDni=True
    if nombre =='' or apellido=='' or email=='' or rol=='' or password=='' or telefono=='' or direccion=='' or dni=='':
        return jsonify({'result': 'Faltan datos por enviar'})
    if is_valid== False:

        return jsonify({'result': 'El Email no es correcto'})
    if is_numerico == False or len(telefono)!=9:
         return jsonify({'result': 'El telefono no es correcto'})
    if len(dni)!=9 or validDni==False:
         return jsonify({'result': 'El DNI no es correcto'})
        

    else:
        user_id = users.insert({
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'password': password,
                'rol': rol,
                'telefono': telefono,
                'direccion': direccion,
                'dni': dni
            })
        new_user = users.find_one({'_id': user_id})

        result = {'email': new_user['email'] + ' registered'}
      
        return  jsonify({"token": access_token})
      


@app.route('/users/login', methods=['POST'])
def login():

    users = mongo.db.users
    email = request.get_json()['email']
    password = request.get_json()['password']

    result = ""

    response = users.find_one({'email': email})

    if response:
        if bcrypt.check_password_hash(response['password'], password):
            access_token = create_access_token(identity={
                'nombre': response['nombre'],
                'apellido': response['apellido'],
                'email': response['email'],
                'direccion': response['direccion'],
                'dni': response['dni'],
                'telefono': response['telefono'],
                'password': response['password'],
                'rol': response['rol']

            })
            result = jsonify({"token": access_token})
        else:
            result = jsonify({"error": "Invalid username and password"})
    else:
        result = jsonify({"result": "No results found"})
    return result


@app.route('/user/delete/<email>', methods=['DELETE'])
def delete_task(email):
    users = mongo.db.users

    response = users.delete_one({'email': email})

    if response.deleted_count == 1:
        result = {'message': 'record deleted'}
    else:
        result = {'message': 'no record found'}
    return jsonify({'result': result})

@app.route('/user/update/<dni>', methods=['PUT'])
def update_task(dni):
    users = mongo.db.users
    
    rol = request.get_json()['rol']
    nombre = request.get_json()['nombre']
    apellido = request.get_json()['apellido']
    email = request.get_json()['email']
    telefono = request.get_json()['telefono']
    direccion = request.get_json()['direccion']
 

    users.update_one({'dni':dni},{'$set':{'nombre':nombre,'rol':rol,'apellido':apellido,'email':email,'telefono':telefono,'direccion':direccion,'dni':dni}})

    return{'status':'noticia actualizada correctamente'}



if __name__ == '__main__':
    app.run(debug=True)
