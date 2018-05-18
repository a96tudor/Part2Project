"""
Part2Project -- demo.py

Copyright May 2018 [Tudor Mihai Avram]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from models import get_model
from data.neo4J.database_driver import AnotherDatabaseDriver
from server.cache import CacheHandler
from models.config import PredictConfig
from server.jobs import JobsHandler
from server.config import Config as ServerConfig
from cypher_statements.config import RULES_TO_RUN
import json
import urllib.request
import ssl
import time


def send_data(data, suffix):
    context = ssl._create_unverified_context()

    req = urllib.request.Request("http://127.0.0.1:5000"+suffix)
    req.add_header('Content-Type', 'application/json; charset=utf-8')

    jsondata = json.dumps(data)
    jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))

    response = urllib.request.urlopen(req, jsondataasbytes, context=context)

    print("The result is: ")
    bytes_data = response.read()

    dictionary = json.loads(bytes_data)
    return dictionary


def get_random_nodes(n, driver):

    q = 'match(n) ' \
        'where "File" in labels(n)' \
        'return n.uuid as uuid, n.timestamp as timestamp limit %d' % n

    return driver.execute_query(q)


def main(nodes):

    data = {
        'nodes': nodes
    }

    path = '/classify'

    result = send_data(data, path)

    id = result['jobID']

    print("Sleeping for 5 seconds...")
    time.sleep(1)
    print("Done... Let's see how the job is doing")

    path = '/job-action?action=results&id=%s' % id
    url = 'http://127.0.0.1:5000%s' % path

    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())

    print('Job status is: %s' % data['status'])

    print('Sleeping for a couple more seconds')
    time.sleep(30)

    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())

    print('Ok, cool. Now job status is: %s' % data['status'])
    print('And the results are...')
    print(json.dumps(data['results']))

if __name__ == "__main__":
    neo4Jdriver = AnotherDatabaseDriver(
        host='bolt://127.0.0.1',
        port=7687,
        user='neo4j',
        pswd='opus'
    )

    nodes = get_random_nodes(10, driver=neo4Jdriver)

    main(nodes)
