--查看进程状态
SELECT * FROM pg_stat_activity;
--结束进程
SELECT pg_terminate_backend(pid);
--查询用户
SELECT * FROM pg_user
--查看用户权限
SELECT * FROM INFORMATION_SCHEMA.role_table_grants
--查看索引
SELECT * FROM pg_indexes;