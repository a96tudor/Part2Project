/**

      ======= RULE #15 =========

    Processes that write in directories such as /usr/lib or /etc/passwd. Identify processes changing files
*/

match (f:File)-[fp:PROC_OBJ]->(p:Process)
where (f.name[0] =~'/usr/bin/.*' or f.name[0]=~'/etc/pwd.*' or f.name[0]=~'/lib/.*' or f.name[0]=~'/usr/lib/.*')
      and (fp.state='WRITE' or fp.state='RaW')
return count(distinct p.uuid)