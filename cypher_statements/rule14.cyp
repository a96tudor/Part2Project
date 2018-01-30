/**

      ======= RULE #14 =========

    Processes that read a file and write to a socket
*/

match (f:File)-[fp:PROC_OBJ]->(p:Process)<-[sp:PROC_OBJ]-(s:Socket)
where (fp.state='READ' or fp.state='RaW') and (sp.state='CLIENT')
return distinct p.uuid