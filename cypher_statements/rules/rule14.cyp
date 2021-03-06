/**

      ======= RULE #14 =========

    Processes that read from or write to a file and write to a socket
*/

match (f:File)-[fp:PROC_OBJ]->(p:Process)<-[sp:PROC_OBJ]-(s:Socket)
where fp.state <> 'BIN' and fp.state<>'WRITE' and not s.name[0]=~"127.0.0.1.*" and f.timestamp < s.timestamp
return distinct p.uuid as uuid, p.timestamp as timestamp
