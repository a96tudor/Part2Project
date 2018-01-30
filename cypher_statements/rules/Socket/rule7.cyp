/**
  ======= RULE #7 =========

  Socket connected to a Process via a PROC_OBJ edge
  (i.e. Sockets opened by

*/

match (s:Socket)-[:PROC_OBJ]->(p:Process)
return distinct s.uuid