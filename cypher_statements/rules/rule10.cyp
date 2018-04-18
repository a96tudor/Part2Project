/**
  ======= RULE #10 =========

  Processes that writes to files in dangerous locations (i.e. /etc/... or /bin/...)
*/

match (f:File)-[c:PROC_OBJ]->(p:Process)
where (
        c.state='WRITE' or c.state='RaW' or c.state='NONE'
      ) and (
        	f.name[0]=~'/bin/.*' or f.name[0]=~'/etc/.*' or
            f.name[0]=~'/lib/.*' or f.name[0]=~'/usr/bin/.*' or
            f.name[0]=~'/usr/lib.*' or f.name[0]=~'/boot/.*' or
            f.name[0]=~'/root/.*' or f.name[0]=~'/dev/.*' or
            f.name[0]=~'/usr/sbin/.*' or f.name[0]=~'/etc/pwd.*'
       	)
return p.uuid as uuid, p.timestamp as timestamp