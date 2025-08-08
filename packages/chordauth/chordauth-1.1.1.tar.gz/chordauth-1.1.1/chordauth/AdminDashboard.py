from flask import Flask, render_template, request, redirect
from urllib.parse import urlparse
import json
import getpass
import os
import requests
from urllib.parse import urlparse
#pip3 install pyopenssl
import logging
import werkzeug

HERE = os.path.dirname(os.path.abspath(__file__))

def local_path(filename):
    return os.path.join(HERE, filename)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

try:
    print("Starting dashboard input form...")
    print("Please note that if you enter invalid information here, the dashboard will not work properly.")

    api = str(input("Please enter your server link. If it is not up, run 'chordauth server' first: "))

    parsed = urlparse(api)

    if not (parsed.scheme == "https" and parsed.netloc != "" and parsed.path in ["", "/"] and parsed.params == "" and parsed.query == "" and parsed.fragment == "" and not api.endswith("/")):
        print("Server link must be in intended format, as in 'https://example.com'.")
        exit()
    api = api + "/api/remove_from_database"

    if os.path.exists(local_path("used_chordauth_already.chordauth_config")):
        passkey = getpass.getpass("Enter your secret passkey: ")
    else:
        print("Please create an account first by running 'chordauth server'.")
        exit()
    print("Now starting dashboard.")
    print("It is now available at https://127.0.0.1:5002/")
    print("Since we are using HTTPS, to ensure your data is encrypted, we use an informal certificate. \nThis means your browser will show a warning.\nYou can bypass the warning.")
    print("To close ChordAuth, close the terminal window or force quit it.")
    print("Thank you for using ChordAuth 🎹🔑😃")
except Exception as e:
    print("Error!")
    print(str(e))
@app.route("/")
def index():
    try:
        with open(local_path("chord_auth_database.json"), "r") as file:
            data = json.load(file)
        newdata = []
        for group in data:
            if "description" in group["json_contents"]:
                new_description = group["json_contents"]["description"]
            else:
                new_description = "Empty"
            newdict = {"identification": group["group_name"],"size": str(int(round(len(str(group["json_contents"]).encode('utf-8'))))) + " byte/s","description": new_description}
            newdata.append(newdict)
        return render_template("dashboard.html", data=newdata, passkey=passkey, api=api), 200
    except:
        return "Error. Server could not be run.", 500
@app.route("/delete_group", methods=["POST"])
def delete_group():
    passkey = request.form.get('passkey')
    api = request.form.get('api')
    group = request.form.get('group')
    data = {'group': group, 'passkey': passkey}
    response = requests.post(api, json=data)
    if response.status_code == 200:
        print("Success in removing group.")
    else:
        print(f"Group deletion error: {response.text}")
    return redirect("https://127.0.0.1:5002")
def start_dashboard():
    app.run(host="127.0.0.1",port=5002, ssl_context='adhoc')
if __name__ == '__main__':
    app.run(host="127.0.0.1",port=5002, ssl_context='adhoc')
