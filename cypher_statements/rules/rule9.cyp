/**
  ======= RULE #9 =========

Processes that contain in the command line stuff like: 'sudo', 'chmod', etc.

*/

match (f:File)-[:PROC_OBJ {state: 'BIN'}]->(p:Process)
where p.cmdline=~'.*sudo.*' or p.cmdline=~'.*chmod.*' or
	    p.cmdline=~'.*usermod.*' or p.cmdline=~'.*groupmod.*' or
      p.cmdline=~'.*rm -rf.*' or p.cmdline=~'.*attack.*' or
      p.cmdline=~'.*worm.*' or p.cmdline=~'.*trojan.*' or
      p.cmdline=~'.*virus.*'
return p.uuid AS p_uuid, p.timestamp as p_timestamp,
       f.uuid AS f_uuid, f.timestamp as f_timestamp
