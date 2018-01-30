/**
  ======= RULE #12 =========

  External machines
*/

match (m:Machine)
where m.external
return m
