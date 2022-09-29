from datetime import datetime

import json

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import joblib
import pickle
import pandas as pd
import pandas as pd
import requests
import io

import os
os.chdir(os.path.dirname(__file__))


########### UTILS ############

#base de datos sqlite
db = SQLAlchemy()

#modelos de regresión guardados en saved_models y utils
scaler = pickle.load(open("saved_models_1/fullDB/utils/scaler.pkl", 'rb'))
pca = pickle.load(open("saved_models_1/fullDB/utils/pca.pkl", 'rb'))
knn3 = pickle.load(open("saved_models_1/fullDB/utils/kmeans3.pkl", 'rb'))


model_cluster_0 = pickle.load(open("saved_models_1/fullDB/kernelRidge_model_to_cluster_0.pkl", 'rb'))
model_cluster_1 = pickle.load(open("saved_models_1/fullDB/ridge_model_to_cluster_1.pkl", 'rb'))
model_cluster_2 = pickle.load(open("saved_models_1/fullDB/kNeighborsRegressor_model_to_cluster_2.pkl", 'rb'))

scaler_sub = pickle.load(open("saved_models_1/subDB/utils/scaler.pkl", 'rb'))
model_sub= pickle.load(open("saved_models_1/subDB/GradientBoostingRegressor_entrenado.pkl", 'rb'))

############ FUNCIONES  #############
def proccesing_input(y):
    """
       procesamiento datos de entrada, con normalización y pca
    """
    y_scaled = scaler.transform(y)
    y_scaled_pca = pca.transform(y_scaled)
    return y_scaled_pca

def make_energy_prediction(y_input_scaled_pca_array):
    """
       predicción de energía por atomo a partir de datos procesados, con modelos previamente entrenados
       y luego de predecir el cluster al cual mejor se adecua la nanoparticula 
    
    """
    cluster = knn3.predict(y_input_scaled_pca_array)[0]
    if cluster == 0:
       model = pickle.load(open("saved_models_1/fullDB/kernelRidge_model_to_cluster_0.pkl", 'rb'))
       model_info = pd.read_csv("saved_models_1/fullDB/kernelRidge_model_to_cluster_0_info.csv")
    elif cluster == 1:
        model = pickle.load(open("saved_models_1/fullDB/ridge_model_to_cluster_1.pkl", 'rb'))
        model_info = pd.read_csv("saved_models_1/fullDB/ridge_model_to_cluster_1_info.csv")
    elif cluster == 2:
        model = pickle.load(open("saved_models_1/fullDB/kNeighborsRegressor_model_to_cluster_2.pkl", 'rb'))
        model_info = pd.read_csv("saved_models_1/fullDB/kNeighborsRegressor_model_to_cluster_2_info.csv")

    
    prediction = model.predict(y_input_scaled_pca_array)
    model_name = model_info['model'][0]
    error_rsme = float('%.1g' % model_info[" RMSE"])
    error_mape = float(model_info[" MAPE"]*100)

    return [prediction[0], model_name, error_rsme, error_mape]


#Predecir la energía total de nanoparticulas a partir de datos superficiales
def predict_total_energy(sample_json):
    """
       predicción de energía total a partir de datos superficiales, con modelos previamente entrenados
       y luego de realizar normalización de los datos.
    """
    #input vector
    y = [list(sample_json.values())]

    #normalizacion
    y_scaled = scaler_sub.transform(y)

    # Predicción
    prediction = model_sub.predict(y_scaled)

    model_info = pd.read_csv("saved_models_1/subDB/GradientBoostingRegressor_info.csv")
    model_name = "GradientBoostingRegressor"
    rmse = float('%.1g' % model_info[" RMSE"])
    porcentual = float(model_info[" MAPE"]*100)
    
    return [prediction[0], model_name, rmse, porcentual]

######################################################

def CSVReaderToJson():
    """
       función que mapea fichero csv en formato json
    """
    result_status = 'FAILURE'
    result_data = []
    csv_url = "articles.csv"
    try:
        csv_data = pd.read_csv(csv_url)

        row_count = csv_data.shape[0]
        column_count = csv_data.shape[1]
        column_names = csv_data.columns.tolist()

        # Option [2]
        final_row_data = []
        for index, rows in csv_data.iterrows():
            final_row_data.append(rows.to_dict())

        json_result = {'rows': row_count, 'cols': column_count, 'columns': column_names, 'rowData': final_row_data}
        result_data.append(json_result)
        result_status = 'SUCCESS'
    except:
        result_data.append({'message': 'Unable to process the request.'})

    return result_status, result_data
######################################################

#Clase de manejo de usuarios en la base de datos local
class Users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.Text())
    jwt_auth_active = db.Column(db.Boolean())
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"User {self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.username = new_username

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['username'] = self.username
        cls_dict['email'] = self.email

        return cls_dict

    def toJSON(self):

        return self.toDICT()

#Clases de flujo de autenticación 
class JWTTokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jwt_token = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

    def save(self):
        db.session.add(self)
        db.session.commit()
