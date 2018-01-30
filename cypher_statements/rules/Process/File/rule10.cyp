/**
  ======= RULE #10 =========

  Processes that writes to files in dangerous locations (i.e. /etc/... or /bin/...)
*/

match (f:File)-[c:PROC_OBJ]->(p:Process)
where (
        c.state='WRITE' or c.state='RaW' or c.state='NONE'
      ) and (
        	f.name=~'/bin/.*' or f.name=~'/etc/.*' or
            f.name=~'/lib/.*' or f.name=~'/usr/bin/.*' or
            f.name=~'/usr/lib.*' or f.name=~'/boot/.*' or
            f.name=~'/root/.*' or f.name=~'/dev/.*' or
            f.name=~'/usr/sbin/.*'
       	)
return distinct p.uuid