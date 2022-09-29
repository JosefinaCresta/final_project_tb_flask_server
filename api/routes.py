from datetime import datetime, timezone, timedelta

from functools import wraps

from flask import request
from flask_restx import Api, Resource, fields
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS, cross_origin

import jwt

from .models import db, Users, JWTTokenBlocklist
from .models import predict_total_energy, make_energy_prediction, proccesing_input, predict_total_energy
from .models import CSVReaderToJson
from .models import scaler, pca, knn3, model_cluster_0, model_cluster_1, model_cluster_2
from .config import BaseConfig
# import joblib
import pickle
import pandas as pd
import numpy as np

rest_api = Api(version="1.0", title="Users API")


"""
    Flask-Restx models for api request and response data
"""

signup_model = rest_api.model('SignUpModel', {"username": fields.String(required=True, min_length=2, max_length=32),
                                              "email": fields.String(required=True, min_length=4, max_length=64),
                                              "password": fields.String(required=True, min_length=4, max_length=16)
                                              })

login_model = rest_api.model('LoginModel', {"email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=4, max_length=16)
                                            })

user_edit_model = rest_api.model('UserEditModel', {"userID": fields.String(required=True, min_length=1, max_length=32),
                                                   "username": fields.String(required=True, min_length=2, max_length=32),
                                                   "email": fields.String(required=True, min_length=4, max_length=64)
                                                   })




"""
   Pedido de JWT token para flujo de autenticación
"""

def token_required(f):

    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if "authorization" in request.headers:
            token = request.headers["authorization"]

        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 400

        try:
            data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
            current_user = Users.get_by_email(data["email"])

            if not current_user:
                return {"success": False,
                        "msg": "Sorry. Wrong auth token. This user does not exist."}, 400

            token_expired = db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar()

            if token_expired is not None:
                return {"success": False, "msg": "Token revoked."}, 400

            if not current_user.check_jwt_auth_active():
                return {"success": False, "msg": "Token expired."}, 400

        except:
            return {"success": False, "msg": "Token is invalid"}, 400

        return f(current_user, *args, **kwargs)

    return decorator


"""
    Rutas Flask-Rest 
"""



@rest_api.route('/api/users/register')
class Register(Resource):
    """
       Creación nuevo usuario
    """

    @rest_api.expect(signup_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _username = req_data.get("username")
        _email = req_data.get("email")
        _password = req_data.get("password")

        user_exists = Users.get_by_email(_email)
        if user_exists:
            return {"success": False,
                    "msg": "Email already taken"}, 400

        new_user = Users(username=_username, email=_email)

        new_user.set_password(_password)
        new_user.save()

        return {"success": True,
                "userID": new_user.id,
                "msg": "The user was successfully registered"}, 200


@rest_api.route('/api/users/login')
class Login(Resource):
    """
        Login usuario con JWT token de respuesta
    """

    @rest_api.expect(login_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _email = req_data.get("email")
        _password = req_data.get("password")

        user_exists = Users.get_by_email(_email)

        if not user_exists:
            return {"success": False,
                    "msg": "This email does not exist."}, 400

        if not user_exists.check_password(_password):
            return {"success": False,
                    "msg": "Wrong credentials."}, 400

        token = jwt.encode({'email': _email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)

        user_exists.set_jwt_auth_active(True)
        user_exists.save()

        return {"success": True,
                "token": token,
                "user": user_exists.toJSON()}, 200


@rest_api.route('/api/users/edit')
class EditUser(Resource):
    """
       Editar el usuario
    """

    @rest_api.expect(user_edit_model)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _new_username = req_data.get("username")
        _new_email = req_data.get("email")

        if _new_username:
            self.update_username(_new_username)

        if _new_email:
            self.update_email(_new_email)

        self.save()

        return {"success": True}, 200


@rest_api.route('/api/users/logout')
class LogoutUser(Resource):
    """
       Log out 
    """

    @token_required
    def post(self, current_user):

        _jwt_token = request.headers["authorization"]

        jwt_block = JWTTokenBlocklist(jwt_token=_jwt_token, created_at=datetime.now(timezone.utc))
        jwt_block.save()

        self.set_jwt_auth_active(False)
        self.save()

        return {"success": True}, 200



#############
#FULL DB
#############
@rest_api.route('/api/modelsFullDB')
class Model(Resource):
    """
       Predicción energía por atomo con full datos
    """
    def post(self):
        content = request.json['parsedData']
        
        df_input = pd.DataFrame.from_dict(content, orient='columns')
     
        y_input_array = np.array(df_input).reshape(1, -1)
    
        y_input_processed = proccesing_input(y_input_array)
      
        prediction_result = make_energy_prediction(y_input_processed)
       
        return {"prediction": round(prediction_result[0],2), "model": prediction_result[1], "rmse": prediction_result[2], "mape": prediction_result[3]}, 200



#############
#SUB DB
#############
@rest_api.route('/api/modelsSubDB')
class ModelSub(Resource):
    """
       Predicción energía total a partir de datos superficiales
    """
    def post(self):
        content = {'nSurface': float(request.json['nSurface']), 'avgSurf': float(request.json['avgSurf']),
                'q6q6AvgSurf': float(request.json['q6q6AvgSurf']), 'S100': float(request.json['S100']), 
                 'S111': float(request.json['S111']), 'S110': float(request.json['S110']), 'S311': float(request.json['S311'])}

        result = predict_total_energy(content)

        print(result[0])
        print(result[1])
        print(result[2])
        print(result[3])

        
        return {"prediction": round(result[0],2),  "model": result[1] , "rmse": result[2], "mape": result[3]}, 200


#############
#Articles
#############
@rest_api.route('/api/articles')
class Articles(Resource):
    """
       Articulos de webscrapping
    """
    def get(self):
       
        result_status, result_data = CSVReaderToJson()
        
        return {'resultStatus': result_status, 'resultData': result_data}
