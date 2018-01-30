/**
  ======= RULE #12 =========

  External machines
*/

match (m:Machine)
where m.external
return distinct m.uuid
