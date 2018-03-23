from data.neo4J.database_driver import DatabaseDriver, AnotherDatabaseDriver
from timeit import timeit


dd = DatabaseDriver(
    host='127.0.0.1',
    usrname='neo4j',
    passwd='opus',
    port=7474
)

a = timeit(dd.execute_query(
    "match (n:File)-[:PROC_OBJ]->(p:Process) " 
    "return n, p"
))

print(a)
