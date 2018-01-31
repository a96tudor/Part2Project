/**
  ======= RULE #8 =========

  Processes with gid != egid

*/

match (p:Process)
where p.meta_gid <> p.meta_egid
return distinct p.uuid
