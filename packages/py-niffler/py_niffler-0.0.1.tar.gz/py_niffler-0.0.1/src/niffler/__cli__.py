import asyncio
import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, get_type_hints

import click
from kaitian.utils.logger import add_file_logger, setup_logger

from .agent import NifflerAgent
from .strategy import Strategy

logger = logging.getLogger(__name__)


def _str_to_bool(value: str) -> bool:
    """
    将字符串 'true'/'false'/'yes'/'no'/'1'/'0' 等转为布尔值。
    大小写不敏感，失败时抛出 ValueError。
    """
    v = value.lower()
    if v in {"true", "1", "yes", "y", "on"}:
        return True
    if v in {"false", "0", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def _load_strategy_class(path: Path) -> type[Strategy[Any]]:
    """动态加载文件并返回第一个 Strategy 子类。"""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise click.ClickException(f"无法加载模块 {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    for _, obj in inspect.getmembers(mod, inspect.isclass):
        if (
            issubclass(obj, Strategy)
            and obj is not Strategy
            and not inspect.isabstract(obj)
        ):
            return obj
    raise click.ClickException(f"找不到具体 Strategy 子类: {path}")


def _convert_kwargs(cls: type[Strategy[Any]], raw: Dict[str, str]) -> Dict[str, Any]:
    """根据 Strategy.__init__ 的类型注解自动转换字符串值。"""
    hints = get_type_hints(cls.__init__)
    converted: Dict[str, Any] = {}
    for k, v in raw.items():
        typ = hints.get(k)
        if typ is None:
            # 没有注解保持字符串
            converted[k] = v
            continue

        # 支持 bool、int、float，其余保持 str
        if typ is bool:
            converted[k] = _str_to_bool(v)
        elif typ is int:
            converted[k] = int(v)
        elif typ is float:
            converted[k] = float(v)
        else:
            converted[k] = v
    return converted


@click.group()
def niffler_cli() -> None:
    """Niffler: WorldQuant Brain Platform Assistant."""
    pass


@niffler_cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("strategy", type=click.Path(exists=True, path_type=Path))
@click.option("--region", required=True, help="Region")
@click.option("--universe", required=True, help="Universe")
@click.option("--delay", type=int, required=True, help="Delay")
@click.option("--slots", type=int, required=True, help="占用槽位")
@click.option("--batch_size", type=int, required=True, help="批大小")
@click.option("--name", type=str, default=None, help="任务名")
@click.option("--db", type=str, default=None, help="因子库")
@click.option("--logfile", type=click.Path(path_type=Path), default=None)
@click.option("--loglevel", type=int, default=10, help="日志级别")
@click.option("--username", type=str, default=None, help="用户名")
@click.option("--password", type=str, default=None, help="密码")
@click.option("--retry_delay", type=int, default=10, help="重试休眠间隔")
@click.option("--max_retry", type=int, default=10, help="最大重试次数")
@click.option("--concurrency", type=int, default=10, help="并发数")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def simulate(
    strategy: Path,
    region: str,
    universe: str,
    delay: int,
    slots: int,
    batch_size: int,
    db: str | None,
    name: str | None,
    logfile: Path | None,
    loglevel: int,
    username: str | None,
    password: str | None,
    retry_delay: float,
    max_retry: int,
    concurrency: int,
    extra_args: tuple[str, ...],
) -> None:
    """
    Niffler 因子回测器

    STRATEGY: 包含 Strategy 子类的 .py 文件路径
    其余形如 --key value 的参数都会透传给 Strategy 构造函数
    """
    cls = _load_strategy_class(strategy)

    # 先把固定参数和额外参数统一收集到 raw
    raw: Dict[str, str] = {
        "region": region,
        "universe": universe,
        "delay": str(delay),
        "slots": str(slots),
        "batch_size": str(batch_size),
    }
    if name is not None:
        raw["name"] = name

    # 解析 extra_args
    it = iter(extra_args)
    for arg in it:
        if not arg.startswith("--"):
            raise click.ClickException(f"额外参数必须以 -- 开头，得到 {arg}")
        key = arg[2:].replace("-", "_")
        try:
            value = next(it)
        except StopIteration:
            raise click.ClickException(f"{arg} 缺少对应值")
        raw[key] = value

    # 统一类型转换
    kwargs = _convert_kwargs(cls, raw)
    if db is not None:
        if Path(db).parent.exists():
            db = f"sqlite:///{Path(db).absolute()}"

    logger = setup_logger(
        "niffler",
        loglevel,
        fmt="[{levelname:.04}] {asctime} {message} [{filename}:{lineno}]",
    )
    if logfile is not None:
        _ = add_file_logger(
            logger,
            logfile,
            loglevel,
            formatter=logging.Formatter(
                fmt="[{levelname:.04}] {asctime} {message} [{filename}:{lineno}]",
                datefmt="%m-%d %H:%M:%S",
                style="{",
            ),
        )

    agent = NifflerAgent(
        dbengine=db,
        username=username,
        password=password,
        retry_delay=retry_delay,
        max_retry=max_retry,
        request_concurrency=concurrency,
    )

    # logger.debug(f"增补参数: {kwargs}")
    strategy_obj = cls(agent=agent, **kwargs)
    asyncio.run(strategy_obj.run())
