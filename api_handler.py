# api_handler.py
from flask import Flask, request, jsonify
from train_bot import train_chatbot
import random
from flask_cors import CORS
import numpy as np
from pymongo import MongoClient 

app = Flask(__name__)
CORS(app)
vectorizer, best_svm_model, labels = train_chatbot()


#mongodb 
uri = "mongodb+srv://Visitor:researchgogogo@reseearch.a2rwr6l.mongodb.net/"

client = MongoClient(uri)
db = client['research']
collection = db['data']
UserSaves = db['UserSaves']
UsersInfo = db['UsersInfo']



    

def get_predicted_label(user_input):
    
    user_input_tfidf = vectorizer.transform([user_input])

    predicted_label = best_svm_model.predict(user_input_tfidf)[0]
    predicted_confidence = best_svm_model.predict_proba(user_input_tfidf)[0]

    confidence = np.sort(np.array(predicted_confidence))[::-1]

    if confidence[0] >= 0.700:
            return predicted_label
    else:
        return "None"



def authenticatedUser(user_information):
    myquery = { "Email": user_information[0] }
    mydoc = UsersInfo.find(myquery,{ "_id": 0, "Email": 1,"Password": 1})
    for x in mydoc:
        if(user_information[0] == x.get("Email")):
            if(user_information[1] == x.get("Password")):
                return "True"
            else:
                return "False"
        else:
            return "False"
        
    
    

@app.route('/intent', methods=['POST'])
def intent():
    user_input = request.json.get('message', '')
    intent = get_predicted_label(user_input)
    print(intent)
    return jsonify({'response': intent})

@app.route('/signup', methods=['POST'])
def signup():
    user_input = request.json.get('message', '')
    user_information = user_input.split()
    mydict = { "UserName": user_information[0], "Fullname": user_information[1],"Email": user_information[2], "Password": user_information[3] }
    myquery = { "Email": user_information[2] }
    mydoc = UsersInfo.find(myquery,{ "_id": 0, "Email": 1})
    for x in mydoc:
        if(user_information[2] == x.get("Email")):  
            return jsonify({'response': "A User with that email already exists"})

    Save = UsersInfo.insert_one(mydict)
    return jsonify({'response': "User signed up"})
    

@app.route('/login', methods=['POST'])
def login():
    user_input = request.json.get('message', '')
    user_information = user_input.split()
    if authenticatedUser(user_information) == "True":
        return jsonify({'Authentication ': "User Authenticated"})
    else:
        return jsonify({'Authentication ': "Failed to login"})



@app.route('/savemessage', methods=['POST'])
def savemessage():
    user_input = request.json.get('message', '')
    user_information = user_input.split()
    mydict,myquery = { "Email": user_information[0], "Message": user_information[1]}
    mydoc = UserSaves.find(myquery)
    for x in mydoc:
        if(user_information[2] == x.get("Message")):  
            return jsonify({'response': "Message Already Saved"})
    
    return jsonify({'response': "Message saved"})

@app.route('/loadmessages', methods=['POST'])
def loadmessages():
    user_input = request.json.get('message', '')
    user_information = user_input.split()
    myquery = { "Email": user_information[0]}
    mydoc = UserSaves.find(myquery)
    responses=[]
    for x in mydoc:
        responses.append(x.get("Message"))
        print(responses)
    return jsonify({'response': responses})

@app.route('/deletemessages', methods=['POST'])
def deletemessages():
    user_input = request.json.get('message', '')
    user_information = user_input.split()
    myquery = { "Email": user_information[0], "Message": user_information[1]}
    mydoc = UserSaves.delete_one(myquery)
    return jsonify({'response': "Message deleted"})

@app.route('/deleteallmessages', methods=['POST'])
def deleteallmessages():
    user_input = request.json.get('message', '')
    user_information = user_input.split()
    myquery = { "Email": user_information[0]}
    mydoc = UserSaves.delete_many(myquery)
    return jsonify({'response': "All Messages deleted"})



@app.route('/test', methods=['POST'])
def test():
    # Assuming the request contains JSON data with a 'message' key
    data = request.get_json()

    if 'message' in data:
        user_message = data['message']

        # Process the user's message here
        # ...

        # Return a response, for example echoing the message
        return jsonify({'response': f'You said: {user_message}'})

    return jsonify({'ERROR': 'Invalid request'}), 400

def getresponse(intent):
    myquery = { "tag": intent }
    patterns = collection.find(myquery)
    response = ""
    for x in patterns:
        response = x.get("responses")
    return random.choice(response)


@app.route("/chatbot", methods=['POST'])
async def chatbot():
    user_input = request.json.get('message', '')
    intent = get_predicted_label(user_input)
    if intent=="None":
        return jsonify({"chatbot message": "I couldn't understand what you said, can u rephrase that"})
    else:
        try:
            response= getresponse(intent)
            return jsonify({"chatbot message": response})
        except Exception as e:
            print(e)
            return jsonify({"ERROR": "Internal server error"})
        
