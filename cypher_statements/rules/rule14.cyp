/**

      ======= RULE #14 =========

    Processes that read from or write to a file and write to a socket
*/

match (f:File)-[fp:PROC_OBJ]->(p:Process)<-[sp:PROC_OBJ]-(s:Socket)
where fp.state <> 'BIN' and s.name[0]=~"127.0.0.1.*"
return p.uuid as p_uuid, p.timestamp as p_timestamp,
       f.uuid as f_uuid, f.timestamp as f_timestamp,
       fp.state as rel_sts
