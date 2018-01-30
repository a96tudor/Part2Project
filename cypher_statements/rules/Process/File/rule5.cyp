/**
  ======= RULE #5 =========

  Processes with uid != euid

*/

match (p:Process)
where p.meta_uid <> p.meta_euid
return distinct p.uuid