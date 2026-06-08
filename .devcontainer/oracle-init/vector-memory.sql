-- Enable Oracle's Vector Memory Pool so in-memory HNSW and quantized vector
-- indexes can be built. On the Oracle Free image VECTOR_MEMORY_SIZE defaults to 0,
-- which makes such indexes fail with ORA-51962 ("vector memory area is out of
-- space"). The parameter is dynamic (no restart), and is set at both the CDB root
-- (the actual pool size) and the PDB (the max usage allowed). 256M is ample for
-- the workshop's data and stays well within the Free edition's SGA budget.
-- gvenzl/oracle-free runs files in /container-entrypoint-startdb.d/ as SYSDBA on
-- every container start, so this re-applies automatically.
WHENEVER SQLERROR CONTINUE
ALTER SYSTEM SET VECTOR_MEMORY_SIZE = 256M SCOPE=BOTH;
ALTER SESSION SET CONTAINER = FREEPDB1;
ALTER SYSTEM SET VECTOR_MEMORY_SIZE = 256M SCOPE=BOTH;
EXIT;
