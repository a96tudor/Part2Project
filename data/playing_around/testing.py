from data.training.database_driver import DatabaseDriver

dd = DatabaseDriver(
    host='127.0.0.1',
    usrname='neo4j',
    passwd='opus',
    port=7474
)

dd.execute_query(
    "match (n:File)-[:PROC_OBJ]->(p:Process) " 
    "return n, p"
)

