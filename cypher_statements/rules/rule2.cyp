/**
  ======= RULE #2 =========

  Process opening a socket to a different machine
      (excluding sockets to 127.0.0.1)
*/

match (s:Socket)-[c:PROC_OBJ]->(p:Process)
where not s.name[0] =~'127.0.0.1.*/'
return distinct p.uuid as uuid, p.timestamp as timestamp
