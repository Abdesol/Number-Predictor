from fastapi import FastAPI
from cryptography.fernet import Fernet
from pydantic import BaseModel
import numpy as np
import joblib
import requests
import uvicorn

class Request(BaseModel):
    array:list

app = FastAPI()

def download_model():
    model_url = "https://download1320.mediafire.com/3yyrodbo45ag/9gecuxwirpw8o0h/model.pkl"
    model_req = requests.get(model_url, allow_redirects=True)
    open("model.pkl", 'wb').write(model_req.content)

download_model()
model = joblib.load("model.pkl")

def predict(array:np.ndarray):
    try:
        prediction:np.ndarray = model.predict([array])
        predicted_num:int = prediction.tolist()[0]
        return [True, predicted_num]
    except:
        return [False]

@app.post("/predict/")
async def predict_method(req:Request):
    if req.array == None or len(req.array) < 1:
        return {"Error": True, "Message":"Invalid request"}
    
    numpy_array = np.array(req.array)
    prediction = predict(numpy_array)
    if not prediction[0]:
        return {"Error": True, "Message":"Error occured in prediction"}

    return {"Error": False, "Prediction": prediction[1]}

if __name__=="__main__":
    uvicorn.run("server:app",host='0.0.0.0', port=4323)