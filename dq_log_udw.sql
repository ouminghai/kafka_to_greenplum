CREATE TABLE act_log(
	act_id VARCHAR(32),/*接口标识*/
	act_stat INT,/*访问状态*/
	req TEXT,/*请求内容*/
	res TEXT,/*响应内容*/
	proc_time INT,/*处理时间（单位毫秒）*/
	reserve TEXT,/*保留字段*/
	log_time TIMESTAMP,/*接口访问时间*/
	server_id INT,/*区服标识*/
	log_date DATE,/*日期*/
	role_id VARCHAR(32)/*角色标识*/
)
WITH (APPENDONLY=true, COMPRESSLEVEL=5)
DISTRIBUTED BY (role_id)
PARTITION BY RANGE (log_date)
(START (date '2013-01-01') INCLUSIVE
END (date '2023-01-01') EXCLUSIVE
EVERY (INTERVAL '1 month'));
CREATE INDEX act_server_id ON act_log (server_id);
CREATE INDEX act_act_id ON act_log (act_id);
CREATE INDEX act_log_date ON act_log (log_date);

CREATE TABLE login_log(
	user_id VARCHAR(36),/*用户标识*/
	device_id VARCHAR(64),/*设备标识*/
	device_type VARCHAR(64),/*设备类型*/
	device_os VARCHAR(32),/*设备系统*/
	retail_id INT,/*渠道标识*/
	lvl INT,/*角色等级*/
	uptime INT,/*在线时长*/
	ip VARCHAR(64),/*登录地址*/
	log_time TIMESTAMP,/*登录时间*/
	server_id INT,/*区服标识*/
	log_date DATE,/*日期*/
	role_id VARCHAR(32)/*角色标识*/
)
WITH (APPENDONLY=true, COMPRESSLEVEL=5)
DISTRIBUTED BY (role_id)
PARTITION BY RANGE (log_date)
(START (date '2013-01-01') INCLUSIVE
END (date '2023-01-01') EXCLUSIVE
EVERY (INTERVAL '1 month'));
CREATE INDEX login_server_id ON login_log (server_id);
CREATE INDEX login_log_date ON login_log (log_date);

CREATE TABLE reg_log(
    role_id VARCHAR(32),/*角色标识*/
	user_id VARCHAR(32),/*用户标识*/
	device_id VARCHAR(64),/*设备标识*/
	device_type VARCHAR(64),/*设备类型*/
	device_os VARCHAR(32),/*设备系统*/
	retail_id INT,/*渠道标识*/
	log_time TIMESTAMP,/*注册时间*/
	server_id INT,/*区服标识*/
	log_date DATE/*日期*/
)
WITH (APPENDONLY=true, COMPRESSLEVEL=5)
DISTRIBUTED BY (role_id);
CREATE INDEX reg_server_id ON reg_log (server_id);

CREATE TABLE var_log(
	field_name VARCHAR(32),/*重要数值字段名称*/
	old_val BIGINT,/*原始值*/
	new_val BIGINT,/*目标值*/
	scene VARCHAR(32),/*数值变化场景*/
	remark TEXT,/*备注*/
	log_time TIMESTAMP,/*变化时间*/
	server_id INT,/*区服标识*/
	log_date DATE,/*日期*/
	role_id VARCHAR(32)/*角色标识*/
)
WITH (APPENDONLY=true, COMPRESSLEVEL=5)
DISTRIBUTED BY (role_id)
PARTITION BY RANGE (log_date)
(START (date '2013-01-01') INCLUSIVE
END (date '2023-01-01') EXCLUSIVE
EVERY (INTERVAL '1 month'));
CREATE INDEX var_server_id ON var_log (server_id);
CREATE INDEX var_log_date ON var_log (log_date);

CREATE TABLE coin_log(
	field_name VARCHAR(32),/*虚拟币字段名称*/
	old_val BIGINT,/*原始值*/
	new_val BIGINT,/*目标值*/
	lifetime SMALLINT,/*消费周期*/
	scene VARCHAR(32),/*数值变化场景*/
	remark TEXT,/*备注*/
	log_time TIMESTAMP,/*变化时间*/
	server_id INT,/*区服标识*/
	log_date DATE,/*日期*/
	role_id VARCHAR(32)/*角色标识*/
)
WITH (APPENDONLY=true, COMPRESSLEVEL=5)
DISTRIBUTED BY (role_id)
PARTITION BY RANGE (log_date)
(START (date '2013-01-01') INCLUSIVE
END (date '2023-01-01') EXCLUSIVE
EVERY (INTERVAL '1 month'));
CREATE INDEX coin_server_id ON coin_log (server_id);
CREATE INDEX coin_log_date ON coin_log (log_date);
CREATE INDEX coin_field_name ON coin_log (field_name);
