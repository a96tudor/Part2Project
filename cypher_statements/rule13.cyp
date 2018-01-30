/**
  ======= RULE #13 =========

  Machines that connect to an external machine
*/

match (m1:Machine)-[r:CONN]->(m2:Machine)
where m2.external
return distinct m1, r, m2
