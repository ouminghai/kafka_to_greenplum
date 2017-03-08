# -*- coding: utf-8 -*-
"""
Created on 2016-09-18

@author: Cheng Shangguan
"""
import os
import redis
import psycopg2
from time import sleep
from hashlib import md5
from datetime import datetime
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool


class RedisConnector(object):
    def __init__(self, redis_conf, db):
        pool = redis.ConnectionPool(host=redis_conf['host'], port=6379, db=redis_conf['redis_matcher'][db])
        self._server = redis.StrictRedis(connection_pool=pool)
        self._pipe = self._server.pipeline(transaction=True)
        self._pipe.multi()

    # 批量写入
    def multi_add(self, values):
        total_list = [md5(line).hexdigest() for line in values]
        for value in total_list:
            self._pipe.setnx(value, '')
        results = self._pipe.execute()
        if False not in results:
            self.set_expire(values)
            return True
        while False in results:
            false_index = results.index(False)
            results.pop(false_index)
            values.pop(false_index)
        self.set_expire(values)
        return values

    # 批量设置摧毁时间
    def set_expire(self, values):
        total_list = [md5(line).hexdigest() for line in values]
        for value in total_list:
            self._pipe.expire(value, 3600)
        self._pipe.execute()


class BatchCopy(object):
    def __init__(self, dw_conf, event_path, worker_id, table_names, redis_conf, logger, sep='\x02'):
        self._tables = {}
        self._pool = ThreadedConnectionPool(
            1,
            2,
            host=dw_conf.get("host"),
            port=dw_conf.get("port"),
            database=dw_conf.get("database"),
            user=dw_conf.get("user"),
            password=dw_conf.get("password")
        )
        self._redis = redis_conf
        self._logger = logger
        self._sep = sep
        cur = self._pool.getconn().cursor(cursor_factory=RealDictCursor)
        for table_name in table_names:
            worker_dir = "%s/%s" % (event_path, worker_id)
            if not os.path.exists(worker_dir):
                os.makedirs(worker_dir)
            file_path = "%s/%s.udw" % (worker_dir, table_name)
            self._tables[table_name] = {
                "columns": {},
                "path": file_path,
                "file": open(file_path, 'a+'),
                "data": []
            }
            sql = "SELECT ordinal_position, column_name FROM information_schema.columns " \
                  "WHERE table_name = '%s'" % table_name
            cur.execute(sql)
            columns = cur.fetchall()
            if len(columns) == 0:
                self._logger.error(table_name)
                continue
            for column in columns:
                self._tables[table_name]["columns"][column["column_name"]] = column["ordinal_position"]
        cur.close()

    def json2copy(self, event):
        values = []
        hash_values = {}
        for k, v in event.value.items():
            if type(v) == int:
                hash_values[self._tables[event.key]["columns"][k]] = str(v)
            if type(v) == str:
                hash_values[self._tables[event.key]["columns"][k]] = v
            if type(v) == list or type(v) == dict:
                hash_values[self._tables[event.key]["columns"][k]] = "'%s'" % str(v)
        range_stop = len(hash_values) + 1
        for i in range(1, range_stop):
            values.append(hash_values[i])
        return self._sep.join(values)

    def writelines(self, events):
        for event in events:
            try:
                row = self.json2copy(event)
            except Exception as e:
                self._logger.error(e)
                self._logger.error(self._tables[event.key])
            else:
                self._tables[event.key]["data"].append(row + '\n')
        for v in self._tables.values():
            if not isinstance(v, dict):
                continue
            v["file"].writelines(v["data"])
            del v["data"][:]

    def redis_sieve(self, db, values):
        rc = RedisConnector(self._redis, db)
        values.seek(0)
        values = values.read().split('\n')[:-1]
        return rc.multi_add(values)

    def copy_sink(self):
        for k, v in self._tables.items():
            result = self.redis_sieve(k, v['file'])
            if isinstance(result, list):
                result = '\n'.join(result)
                self._logger.info('duplicate data')
                v['file'].close()
                os.remove(v['path'])
                v['file'] = open(v['path'], 'a+')
                v['file'].write(result)
            # 无重复时
            v["file"].seek(0)
            try:
                conn = self._pool.getconn()
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.copy_from(v["file"], k, sep=self._sep)
                conn.commit()
            # 数据类型错误或缺少字段时为DataError
            except psycopg2.DataError as e:
                self._logger.error(e.message)
                v["file"].seek(0)
                with open('/data/log/unresolved_data/cleaned#' + k + '#' + datetime.now().strftime("%Y%m%d%H%M%S"),
                          'w') as err_log:
                    err_log.write(v["file"].read())
            # 数据库响应速度慢，报错返回失败，返回为空
            except psycopg2.DatabaseError as e:
                self._logger.error(e)
                v["file"].seek(0)
                with open('/data/log/unresolved_data/cleaned#' + k + '#' + datetime.now().strftime("%Y%m%d%H%M%S"),
                          'w') as interrupted:
                    interrupted.write(v["file"].read())
                sleep(300)
            finally:
                cur.close()
                self._pool.putconn(conn)
        self.flush_copy()

    def flush_copy(self):
        for v in self._tables.values():
            if not isinstance(v, dict):
                continue
            v["file"].close()
            os.remove(v["path"])
            v["file"] = open(v["path"], 'a+')

    def close(self):
        for v in self._tables.values():
            if not isinstance(v, dict):
                continue
            v["file"].close()
            os.remove(v["path"])
            if not self._pool.closed:
                self._pool.closeall()
