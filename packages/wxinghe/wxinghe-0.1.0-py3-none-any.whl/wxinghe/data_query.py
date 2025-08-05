import requests
import time
import hashlib
import json
import polars as pl
import io

from pydantic import BaseModel, validate_call


class DataQuery(BaseModel):
    oa: str
    secret: str

    @property
    def url(self):
        return "https://58dp.58corp.com/openapi/team/doc/run"

    @validate_call
    def run_sql(
        self, sql: str, time_out_seconds: int = 7200, sleep_time: int = 5
    ) -> pl.DataFrame:
        """
        执行SQL语句
        :param sql: SQL语句
        :return: 执行结果
        """
        ts = int(time.time() * 1000)
        headers = {
            "client-user": "xn_ai_qa",
            "ts": str(ts),
            "token": hashlib.md5(f"{self.secret}{ts}".encode()).hexdigest(),
        }
        param = {
            "oa": self.oa,
            "content": sql,
            "sql_engine": 2,
        }
        res = requests.post(self.url, headers=headers, json=param)
        execute_id = json.loads(res.text)["data"]["execute_id"]
        # sleep 检查直到运行完毕
        for i in range(0, time_out_seconds):
            ts = int(time.time() * 1000)
            url = "https://58dp.58corp.com/openapi/team/doc/histories/progresses"
            headers = {
                "client-user": "xn_ai_qa",
                "ts": str(ts),
                "token": hashlib.md5(f"{self.secret}{ts}".encode()).hexdigest(),
            }
            param = {"execute_ids": [execute_id]}
            res = requests.post(url, headers=headers, json=param)
            data = json.loads(res.text)["data"]
            if data[0]["status"] in ["WAITING", "EXECUTING"]:
                time.sleep(sleep_time)
                continue
            break

        # 获取预览结果
        ts = int(time.time() * 1000)
        url = f"https://58dp.58corp.com/openapi/team/doc/histories/results?oa={self.oa}&execute_id={execute_id}"
        headers = {
            "client-user": "xn_ai_qa",
            "ts": str(ts),
            "token": hashlib.md5(f"{self.secret}{ts}".encode()).hexdigest(),
        }
        res = requests.get(url, headers=headers)
        res = res.text
        res = res.replace(
            "https://xinghe-storage.58corp.com", "https://xinghe-store.58corp.com"
        )
        # 结果较多>50行时
        # 获取调用结果的下载文件url
        data = json.loads(res)["data"]
        download_link = data["filename"]
        # 下载并读入pandas
        data_result = requests.get(download_link).content
        df = pl.read_csv(io.StringIO(data_result.decode("utf-8")), separator="\t")
        return df
