/**
  ======= RULE #3 =========

  Sockets to a different machine

*/

match (s:Socket)
where not s.name[0] =~'127.0.0.1.*/'
return distinct s.uuid