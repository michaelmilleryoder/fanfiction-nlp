import requests, pdb
import re, json

class QueueClient():
	def __init__(self, url="http://10.24.28.106:7979/"):
		self.queueURL = url;

	def dequeServer(self):
		try:
			req = requests.get(self.queueURL + 'query')

			if (req.status_code == 200):
				data = json.loads(req.text)
				if 'Error' in data: return -1
				else: return data['data']
			else:
				print("Error! Status code :" + str(req.status_code))
				return -1

		except Exception as e:
			print("Error in Queue Server!! \n\n",e)
			return -1

	def enqueue_list(self, data_list):
		try:
			data = {'data': data_list }
			headers = {'Content-Type' : 'application/json'}
			req = requests.post(self.queueURL + 'enqueue_list', data=json.dumps(data), headers=headers)

			msg = json.loads(req.text)
			return msg

		except Exception as e:
			print('Error in Queue Server!! \n\n', e)

	def enqueue(self, data):
		try:
			data = {'data': data }
			headers = {'Content-Type' : 'application/json'}
			req = requests.post(self.queueURL + 'enqueue', data=json.dumps(data), headers=headers)

			msg = json.loads(req.text)
			return msg

		except Exception as e:
			print('Error in Queue Server!! \n\n', e)

	def initServer(self, data_list):
		try:
			data = {'list': data_list }
			headers = {'Content-Type' : 'application/json'}
			req = requests.post(self.queueURL + 'init', data=json.dumps(data), headers=headers)
			msg = json.loads(req.text)
			return msg

		except Exception as e:
			print('Error in Queue Server!! \n\n', e)


	def checkQueue(self):
		try:
			req = requests.get(self.queueURL + 'check')
			return json.loads(req.text)
		except Exception as e:
			print("Error in Queue Server!! \n\n", e)

	def getSize(self):
		try:
			req = requests.get(self.queueURL + 'size')
			return json.loads(req.text)['Size']
		except Exception as e:
			print("Error in Queue Server!! \n\n", e)


	def isEmpty(self):
		try:
			req  = requests.get(self.queueURL + 'check')
			resp = json.loads(req.text)
			return len(resp['Queue']) == 0
		except Exception as e:
			print("Error in Queue Server!! \n\n", e)

	def clear(self):
		try:
			req  = requests.get(self.queueURL + 'clear')
			resp = json.loads(req.text)
			print(resp)
			return True
		except Exception as e:
			print("Error in Queue Server!! \n\n", e)
			return False
