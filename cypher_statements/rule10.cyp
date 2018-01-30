/**
  ======= RULE #10 =========

  Processes that writes to files in dangerous locations (i.e. /etc/... or /bin/...)
*/

match (f:File)-[c:PROC_OBJ]->(p:Process)
where ((c.state='WRITE') or (c.state='RaW')) and (f.name=~'.*/bin.*' or f.name=~'.*/etc/.*')
return f, c, p