/**
  ======= RULE #5 =========

  Processes with uid != euid

*/

match (f:File)-[:PROC_OBJ {state: 'BIN'}]->(p:Process)
where p.meta_uid <> p.meta_euid
return p.uuid as p_uuid, p.timestamp as p_timestamp,
       f.uuid as f_uuid, f.timestamp as f_timestamp