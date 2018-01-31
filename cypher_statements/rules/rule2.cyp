/**
  ======= RULE #2 =========

  Process opening a socket to a different machine
      (excluding sockets to 127.0.0.1)
*/

match (s:Socket)-[c:PROC_OBJ]->(p:Process)
where c.state='SERVER' and (not s.name[0] =~'127.0.0.1.*/')
return distinct p.uuid as p_uuid, p.timestamp as p_timestamp, s.uuid as s_uuid, s.timestamp as s_timestamp, c.state as rel_sts
