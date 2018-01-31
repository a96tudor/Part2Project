/**
  ======= RULE #3 =========

  Sockets to a different machine

*/

match (s:Socket)-[c:PROC_OBJ]->(p:Process)
where not s.name[0] =~'127.0.0.1.*/'
return s.uuid as s_uuid, s.timestamp as s_timestamp, p.uuid as p_uuid, p.timestamp as p_timestamp, c.state as rel_sts