import hashlib
import logging
import unittest
from datetime import date, datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

import polars as pl

BRAIN_TIMEZONE = timezone(timedelta(hours=-4))  # 西四区, 美东时间
LOCAL_TIMEZONE = timezone(timedelta(hours=+8))  # 东八区, 北京时间

logger = logging.getLogger(__name__)

# region: time utils


def convert_tz(
    dt: datetime,
    from_tz: timezone = LOCAL_TIMEZONE,
    to_tz: timezone = BRAIN_TIMEZONE,
):
    """Convert TimeZone

    时区转换, 自动将时间戳从 from_tz 转换到 to_tz, 如果 dt 不存在时区信息, 默认为
    东八区.
    """
    if dt.tzinfo is None:
        dt_tz: datetime = dt.replace(tzinfo=from_tz)
    else:
        dt_tz = dt
    return dt_tz.astimezone(to_tz)


def format_dt(dt: datetime) -> str:
    """Format DateTime

    时间戳格式化, 按照 BRAIN 平台的格式进行处理, 如果要提交到平台, 需要先确保
    时间戳的时区已转换到 BRAIN_TIMEZONE.
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%S%Z").replace("UTC", "")


# endregion

# region: hashing


def hashing_fields(fields: list[Any]) -> str:
    # 将布尔值转换为字符串表示（True -> 'true', False -> 'false'）
    fields = [
        str(field).lower() if isinstance(field, bool) else str(field)
        for field in fields
    ]
    # 拼接所有字段值
    concatenated_str = "".join(map(str, fields))
    # 计算MD5哈希值
    md5_hash = hashlib.md5(concatenated_str.encode("utf-8")).hexdigest()
    return md5_hash

    # endregion


# region: calc


def calc_pnl_corr(target: pl.DataFrame, others: list[pl.DataFrame]) -> float:
    """本地检查自相关性

    Parameters
    ----------
    target : dict
        要计算的 PNL
    others : list[dict]
        要对比的其他 PNL
    """

    target_df = target.select(["date", "pnl"])

    if len(others) == 0:
        return 0.0

    others_df = others[0].select(["date", "pnl"])
    for idx, o in enumerate(others[1:]):
        others_df = others_df.join(
            o.select(["date", "pnl"]), how="left", on=["date"], suffix=f"_{idx}"
        )

    pnls_all = target_df.join(others_df, how="left", on=["date"], suffix="_other")
    max_date = pnls_all["date"].max()
    assert isinstance(max_date, date)
    begin_date = pl.date(year=max_date.year - 4, month=max_date.month, day=max_date.day)

    pnls_all = pnls_all.with_columns(
        *[
            pl.col(p) - pl.col(p).fill_null(strategy="forward").shift(1)
            for p in pnls_all.columns
            if p != "date"
        ],
    ).filter(pl.col("date") > begin_date)

    self_corr = (
        pnls_all.select(pl.selectors.exclude(["date"]))
        .corr()
        .with_columns(
            alpha=pl.Series(pnls_all.select(pl.selectors.exclude(["date"])).columns)
        )
        .select(["alpha", "pnl"])
        .sort("pnl", descending=True)
        .filter(pl.col("alpha") != "pnl")
    )["pnl"][0]
    return self_corr


# endregion

# region: miscellaneous

P = ParamSpec("P")
R = TypeVar("R")


def silent_on_error(func: Callable[P, R]) -> Callable[P, R | None]:
    """装饰器：方法报错时返回 None"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            tb = exc.__traceback__
            while tb and tb.tb_next:
                tb = tb.tb_next
            if tb is not None:
                filename = tb.tb_frame.f_code.co_filename
                lineno = tb.tb_lineno
                funcname = tb.tb_frame.f_code.co_name
                logger.error(
                    f"Calling {filename}:{lineno} - {funcname}(*) failed: {exc}"
                )
            else:
                # 兜底
                logger.error(
                    f"Calling {getattr(func, '__qualname__')}(*) failed: {exc}"
                )
            return None

    return wrapper


def parse_record(record: dict[str, Any]) -> pl.DataFrame:
    """Records 解析器

    平台大量的返回数据都是 schema + records 格式, 可统一用
    该函数返回

    Record Example
    --------------
    {
      'schema': {
        'name' / 'title' /
        'properties': [{'name' / 'title', 'type'}] # 列名
      },
      'records': [
        [], [], [], # 行数据
      ]
    }
    """
    schema_mapping = {"date": pl.String, "amount": pl.Float64}

    schema = {
        p["name"]: schema_mapping.get(p["type"]) or pl.String
        for p in record["schema"]["properties"]
    }
    data = pl.DataFrame(data=record["records"], schema=schema, orient="row")
    for f in filter(lambda x: x["type"] == "date", record["schema"]["properties"]):
        data = data.with_columns(pl.col(f["name"]).str.to_date())
    return data


# endregion


class TestTimeUtils(unittest.TestCase):
    def test_convert_tz(self) -> None:
        """测试时区转换功能"""
        dt = datetime(2025, 1, 1, 12, 0, 0)
        self.assertEqual(
            convert_tz(dt), datetime(2025, 1, 1, 0, 0, 0, tzinfo=BRAIN_TIMEZONE)
        )

    def test_format_dt(self) -> None:
        self.assertEqual(
            format_dt(datetime(2025, 1, 1, tzinfo=BRAIN_TIMEZONE)),
            "2025-01-01T00:00:00-04:00",
        )

    def test_dt_pipeline(self) -> None:
        dt_from = "2025-07-28"
        dt_to = format_dt(convert_tz(datetime.fromisoformat(dt_from)))
        self.assertEqual(dt_to, "2025-07-27T12:00:00-04:00")


class TestMiscUtils(unittest.TestCase):
    def test_silent_on_error(self) -> None:
        @silent_on_error
        def ferror():
            raise ValueError("should return None")

        self.assertIsNone(ferror())
