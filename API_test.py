import os
import sys
import json
import time
import unittest
import urllib2

import requests


# checks if the internet connection is on;
# if not, waits for for maximum 1 minute.
def wait_for_internet():
    prev_time = time.time()
    while True:
        try:
            response = urllib2.urlopen('https://www.google.com', timeout = 1)
            return
        except urllib2.URLError:
            pass
        time.sleep(5)
        if time.time() - prev_time > 60:
            sys.exit()


# returns content of the given url
def get_content(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)
    return response

# posts given content to the specified url
def post_content(url, content):
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.post(url, json.dumps(content), headers=headers)
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)
    return response

# updates content at specified url by the new one
def put_content(url, content):
    headers = {'Content-type': 'application/json'}
    try:
        response = requests.put(url, json.dumps(content), headers=headers)
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)
    return response

# removes content of a given url
def delete_content(url):
    try:
        requests.delete(url)
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)
        

# Testing class for the functions in API.py;
# name of the functions in the class reveals
# what are being tested inside them.
class TestAPIMethods(unittest.TestCase):
    # url of the EC2 instance that hosts the API.
    basic_url = "http://ec2-54-208-173-198.compute-1.amazonaws.com:5000/api/objects"

    def test_initially(self):
        response = json.loads(get_content(self.basic_url).text)
        self.assertTrue(type(response) is list)

    def test_post_valid_object(self):
        info = {
            "name": "Akaki",
            "surname": "Margvelashvili"
            }
        response = json.loads(post_content(self.basic_url, info).text)
        self.assertTrue('uid' in response)
        self.assertTrue(response['uid'] != '')
        info['uid'] = response['uid']
        self.assertEqual(info, response)

    def test_post_invalid_object(self):
        info = ['random']
        response = json.loads(post_content(self.basic_url, info).text)
        for key in ['verb', 'url', 'message']:
            self.assertTrue(key in response)
        self.assertTrue('uid' not in response)

    def test_get_single_object(self):
        info = {"language": "java"}
        post_response = json.loads(post_content(self.basic_url, info).text)
        self.assertTrue('uid' in post_response)
        url = self.basic_url + '/' + post_response['uid']
        get_response = json.loads(get_content(url).text)
        self.assertEquals(post_response, get_response)
        self.assertTrue('language' in get_response)
        self.assertEquals(get_response['language'], 'java')
        self.assertEqual(len(get_response), 2)

    def test_get_all_objects(self):
        object1 = {"key1": "value1"}
        response1 = json.loads(post_content(self.basic_url, object1).text)
        object1['uid'] = response1['uid']
        object2 = {"key2": "value2"}
        response2 = json.loads(post_content(self.basic_url, object2).text)
        object2['uid'] = response2['uid']
        response = json.loads(get_content(self.basic_url).text)
        self.assertTrue(type(response) is list)
        self.assertTrue(object1 in response)
        self.assertTrue(object2 in response)

    def test_put_object_invalid(self):
        response = put_content(self.basic_url + '/non_existing_uid', {})
        response = json.loads(response.text)
        for key in ['verb', 'url', 'message']:
            self.assertTrue(key in response)
        self.assertTrue('uid' not in response)

    def test_put_object_valid(self):
        init_object = {'init_key': 'init_value'}
        post_response = post_content(self.basic_url, init_object)
        post_response = json.loads(post_response.text)
        self.assertTrue('uid' in post_response)
        uid = post_response['uid']
        new_object = {}
        put_response = put_content(self.basic_url + '/' + uid, new_object)
        put_response = json.loads(put_response.text)
        self.assertEquals(put_response, {'uid': uid})
        
    def test_delete(self):
        info = {'some_key': 'some_value'}
        post_response = json.loads(post_content(self.basic_url, info).text)
        self.assertTrue('uid' in post_response)
        uid = post_response['uid']
        delete_content(self.basic_url + '/' + uid)
        all_objects = json.loads(get_content(self.basic_url).text)
        same_uid = [obj for obj in all_objects if obj['uid'] == uid]
        self.assertTrue(len(same_uid) == 0)


# is called when the script is run directly
if __name__ == '__main__':
    unittest.main()
