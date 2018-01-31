/**
  ======= RULE #3 =========

  File (or version of a file) that was read by a process that opened a socket

*/

match (f:File)-[fp:PROC_OBJ]->(p:Process)<-[sp:PROC_OBJ]-(s:Socket)
where f.timestamp < s.timestamp and fp.state<>'BIN'
return distinct f.uuid