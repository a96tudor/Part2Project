/**
    ======= RULE #1 =========

    File downloaded from the web and executed
*/

match (s:Socket)-[sp:PROC_OBJ]->(p1:Process)<-[fp1:PROC_OBJ]-(f:File)-[fp2:PROC_OBJ]->(p2:Process)
where (fp1.state='WRITE' or fp1.state='RaW') and (fp2.state='BIN')
return distinct f.uuid as uuid, f.timestamp as timestamp
