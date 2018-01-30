/**
  ======= RULE #2 =========

  Process opening a socket to a different machine
      (excluding sockets to 127.0.0.1)
*/

match (s:Socket)-[c:PROC_OBJ]->(p:Process)
where c.state='SERVER' and (not s.name[0] =~'127.0.0.1.*/')
return count(distinct s)