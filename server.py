from flask import Flask, request, Response
import json

app = Flask(__name__)

data = {}

@app.route('/test')
def test():
    return Response('{"status":"ok"}', status=200, mimetype='application/json')

@app.route('/offer', methods=['POST'])
def offer():
    if request.form.get("type") == "offer":
        data["offer"] = {"id" : request.form['id'], "type" : request.form['type'], "sdp" : request.form['sdp']}
        return Response(status=200)
    else:
        return Response(status=400)

@app.route('/answer', methods=['POST'])
def answer():
    if request.form.get("type") == "answer":
        data["answer"] = {"id" : request.form['id'], "type" : request.form['type'], "sdp" : request.form['sdp']}
        return Response(status=200)
    else:
        return Response(status=400)

@app.route('/candidate', methods=['POST'])
def candidate():
    if request.json.get("type") == "candidate":
        candidate_data = {
            "id": request.json['id'],
            "type": request.json['type'],
            "candidate": request.json['candidate'],
            "sdpMid": request.json['sdpMid'],
            "sdpMLineIndex": request.json['sdpMLineIndex']
        }
        if "candidates" not in data:
            data["candidates"] = []
        data["candidates"].append(candidate_data)
        return Response(status=200)
    else:
        return Response(status=400)

@app.route('/get_offer', methods=['GET'])
def get_offer():
    if "offer" in data:
        j = json.dumps(data["offer"])
        del data["offer"]
        return Response(j, status=200, mimetype='application/json')
    else:
        return Response(status=503)

@app.route('/get_answer', methods=['GET'])
def get_answer():
    if "answer" in data:
        j = json.dumps(data["answer"])
        del data["answer"]
        return Response(j, status=200, mimetype='application/json')
    else:
        return Response(status=503)

@app.route('/get_candidates', methods=['GET'])
def get_candidates():
    if "candidates" in data and data["candidates"]:
        j = json.dumps(data["candidates"])
        data["candidates"] = []
        return Response(j, status=200, mimetype='application/json')
    else:
        return Response(status=503)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9090, debug=True)
