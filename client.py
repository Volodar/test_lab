import urllib2
import time

print('Run client...')

url = 'http://192.168.0.105:8045'
url = '{}/result?code=1&message=test_1'.format(url)
print('Response: ' + urllib2.urlopen(url).read())


time.sleep(5)
print('exit.')
exit(1)
