from flask import Flask, request, jsonify
from collections import deque
import sys

app = Flask(__name__)
queue = deque([])

@app.route('/init', methods=['GET', 'POST'])
def initialize():
	if request.method == 'POST':
		global queue

		data 	= request.get_json(); 	
		#print( data)
		queue 	= deque(data['list'])

		resp = {
			"Message": "Queue intialized",
			"queue":   list(queue)
		}

		return jsonify(resp)
	else:
		return "Error!"


@app.route('/query', methods=['GET', 'POST'])
def query():
	global queue
	if request.method == 'GET' or request.method == 'POST':
		if len(queue) == 0: 
			return jsonify({
				'data':    -1,
				'success': True
			})

		ele = queue.popleft()
		return jsonify({
			'data':    ele,
			'success': True
		})
	else:
		return 'Error'

@app.route('/enqueue', methods=['GET', 'POST'])
def enqueue():
	global queue
	if request.method == 'GET' or request.method == 'POST':
		data = request.get_json()
		ele = queue.append(data['data'])
		return jsonify({
			'data':    ele,
			'success': True
		})
	else:
		return 'Error'

@app.route('/enqueue_list', methods=['GET', 'POST'])
def enqueue_list():
	global queue
	if request.method == 'GET' or request.method == 'POST':
		if len(queue) == 0:
			return jsonify({
				'Error':   True,
				'Message': 'Queue empty'
			})
		else:
			data = request.get_json()
			ele  = queue.extend(data['data'])
			return jsonify({
				'data':    ele,
				'success': True
			})
	else:
		return 'Error'

@app.route('/size', methods=['GET', 'POST'])
def size():
	global queue
	if request.method == 'GET' or request.method == 'POST':
		return jsonify({
			'Size':   len(queue),
			'Message': 'Size of queue'
		})
	else:
		return 'Error'

@app.route('/clear', methods=['GET'])
def clearQueue():
	global queue
	if request.method == 'GET':
		queue = deque([])
		return jsonify({
			'Message': 'Queue successfully cleared'
		})
	else:
		return 'Error!'

@app.route('/check', methods=['GET'])
def checkQueue():
	global queue
	if request.method == 'GET':
		return jsonify({
			'Queue': list(queue)
		})
	else:
		return 'Error!'

if __name__ == "__main__":
	print ("Server Running")
	if len(sys.argv) == 2:
		server_port = int(sys.argv[1])
	else:
		server_port = 7979
	app.run(host= '0.0.0.0', port = server_port)
