/**
  ======= RULE #3 =========

  Sockets to a different machine

*/

match (s:Socket)-[c:PROC_OBJ]->(p:Process)
where not s.name[0] =~'127.0.0.1.*/'
return s.uuid as uuid, s.timestamp as timestamp
