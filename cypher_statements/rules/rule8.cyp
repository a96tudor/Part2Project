/**
  ======= RULE #8 =========

  Processes with gid != egid

*/

match (f:File)-[:PROC_OBJ {state: 'BIN'}]->(p:Process)
where p.meta_gid <> p.meta_egid
return p.uuid as p_uuid, p.timestamp as p_timestamp,
       f.uuid as f_uuid, f.timestamp as f_timestamp
