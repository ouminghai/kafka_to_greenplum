ALTER TABLE login_log ADD COLUMN device_type VARCHAR(32) DEFAULT NULL, ADD COLUMN device_os VARCHAR(32) DEFAULT NULL;
ALTER TABLE reg_log ADD COLUMN device_type VARCHAR(32) DEFAULT NULL, ADD COLUMN device_os VARCHAR(32) DEFAULT NULL;
ALTER TABLE coin_log RENAME COLUMN coin_type TO lifetime;

ALTER TABLE login_log ALTER COLUMN device_id TYPE VARCHAR(64);
ALTER TABLE reg_log ALTER COLUMN device_id TYPE VARCHAR(64);

ALTER TABLE login_log ALTER COLUMN device_type TYPE VARCHAR(64);
ALTER TABLE reg_log ALTER COLUMN device_type TYPE VARCHAR(64);

ALTER TABLE login_log ALTER COLUMN ip TYPE VARCHAR(64);

ALTER INDEX act_index RENAME TO act_server_id;

CREATE INDEX act_log_date ON act_log (log_date);

DROP INDEX act_act_id;
CREATE OR REPLACE FUNCTION drop_tab_indexes(idx_name text, total int) RETURNS void AS $$
BEGIN
    FOR i IN 1..total LOOP
        EXECUTE 'DROP INDEX ' || idx_name || '_1_prt_' || i;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
SELECT drop_tab_indexes('act_act_id', 120);
ALTER TABLE act_log ALTER COLUMN act_id TYPE VARCHAR(32);
CREATE INDEX act_act_id ON act_log (act_id);
CREATE INDEX coin_field_name ON coin_log(field_name);