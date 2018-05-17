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
from server.jobs import RequestJob

def get_random_nodes(n, driver):

    q = 'match(n) ' \
        'where "File" in labels(n)' \
        'return n.uuid as uuid, n.timestamp as timestamp limit %d' % n

    return driver.execute_query(q)

def main():
    neo4Jdriver = AnotherDatabaseDriver(
        host='bolt://127.0.0.1',
        port=7687,
        user='neo4j',
        pswd='opus'
    )

    cacheHandler = CacheHandler(
        host='127.0.0.1', port=5432, dbName='server-cache', user='tma33', password='opus'
    )

    model = get_model(
        name='cnn',
        config=PredictConfig
    )

    model.load_checkpoint('models/checkpoints/cnn.hdf5')

    nodes = get_random_nodes(n=30, driver=neo4Jdriver)

    job = RequestJob(
        driver=neo4Jdriver,
        model=model,
        cache_handler=cacheHandler,
        jobID='demoJob1',
        ttl=10000,
        batch_size=100,
        nodes=nodes
    )

    job.run()

if __name__ == "__main__":
    main()