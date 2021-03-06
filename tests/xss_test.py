from .requests_test import RequestsTest
import copy
import sys

class XSSTest(RequestsTest):
	def test(self):
		if self.DEBUG: print("Run the XSS Tests")
		passed = 0
		failed = 0
		messages = []
		url = self.domain['protocol'] + self.domain['host'] + self.config['path']
		print("XSS Test for " + url)
		for k,v in self.config['params'].items():
			result_text = []
			result = 'PASS'
			for p in self.payloads:
				if self.DEBUG: print(url + "?" + k + "=" + v + " (" + p + ")")
				if self.config['method'] == 'GET':
					if self.DEBUG: print("Using GET " + self.config['path'])
					data = copy.deepcopy(self.config['params'])
					data[k] = data[k] + p
					res = self.get(url,params=data)
					if res.status_code != 200:
						result_text.append('Payload ' + p + ' caused an unknown error for parameter ' + k)
						failed = failed + 1
						result = 'ERROR'
					else: 
						if 'testpath' in self.config:
							res = self.get(self.domain['protocol'] + self.domain['host'] + self.config['testpath'])
						if self.DEBUG: print("Status " + str(res.status_code))
						#if self.DEBUG: print("Content " + str(res.text))
						if p in res.text:
							failed = failed + 1
							result_text.append('=> Payload ' + p + ' not filtered for parameter ' + k)
							sys.stderr.write('=> Payload ' + p + ' not filtered for parameter ' + k + '\n')
							result = 'FAIL'
						else:
							passed = passed + 1

				elif self.config['method'] == 'POST':
					data = copy.deepcopy(self.config['params'])
					data[k] = data[k] + p
					if self.DEBUG: print("Using POST " + self.config['path'] + " data: " + str(data))
					res1 = self.get(url) # Get in case we need CSRF tokens and/or other items from the form
					res = self.post(url,data=data)
					if res.status_code != 200:
						result_text.append('Payload ' + p + ' caused an unknown error for parameter ' + k) 
						result = 'ERROR'
						failed = failed + 1
					elif res.status_code >=300 and res.status_code <= 400:
						print("Status Code: " + str(res.status_code))
					else: 
						if 'testpath' in self.config:
							res = self.get(self.domain['protocol'] + self.domain['host'] + self.config['testpath'])
						if self.DEBUG: print("Status " + str(res.status_code))
						#if self.DEBUG: print("Content " + str(res.text))
						if p in res.text:
							failed = failed + 1
							result = 'FAIL'
							result_text.append('=> Payload ' + p + ' not filtered for parameter ' + k)
							sys.stderr.write('=> Payload ' + p + ' not filtered for parameter ' + k + '\n')
						else:
							passed = passed + 1
				else:
					if self.DEBUG: print("Endpoint method is not GET or POST")
			self.report.add_test_result(url,self.config['method'],'xss',k,result,result_text)
		
		print("=> " + str(passed) + "/" + str(passed+failed) + " passed/total")
		#print("Messages: " + str(messages))