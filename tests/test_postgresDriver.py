"""
Part2Project -- test_postgresDriver.py

Copyright Apr 2018 [Tudor Mihai Avram]

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
from unittest import TestCase
from server.cache.driver import PostgresDriver
from exceptions.server.cache import *

class TestPostgresDriver(TestCase):

    def test_init(self):
        def init_conn(host, port, dbName, user, password):
            driver = PostgresDriver(
                host=host,
                port=port,
                dbName=dbName,
                user=user,
                password=password
            )

            return driver

        self.assertRaises(
            PostgresDriverConnectionException,
            lambda: init_conn('127.0.0.1', 1234, 'server-cache', 'tma33', 'opus')
        )

        self.assertRaises(
            PostgresDriverConnectionException,
            lambda: init_conn('127.0.0.1', 5432, 'server-cache', 'aaa', 'opus')
        )

        driver = init_conn('127.0.0.1', 5432, 'server-cache', 'tma33', 'opus')

        self.assertIsInstance(
            driver, PostgresDriver
        )

    def test_close(self):
        driver = PostgresDriver(
            host='127.0.0.1',
            port=5432,
            dbName='server-cache',
            user='tma33',
            password='opus'
        )
        self.assertIsNotNone(
            driver.conn
        )
        driver.close()

        self.assertIsNone(
            driver.conn
        )

    def test__execute_query(self):
        self.assertAlmostEqual(1, 1)

    def test__get_new_connection(self):
        self.assertAlmostEquals(1, 1)

    def test_setup_database(self):
        self.assertAlmostEquals(1, 1)

    def test_execute_SELECT(self):
        self.assertAlmostEquals(1, 1)

    def test_execute_INSERT(self):
        self.assertAlmostEquals(1, 1)

    def test_execute_UPDATE(self):
        self.assertAlmostEquals(1, 1)

    def test_renew_connection(self):
        self.assertAlmostEquals(1, 1)

    def test_reset_connection(self):
        self.assertAlmostEquals(1, 1)
