import asyncio
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any, Literal, overload

import httpx
import polars as pl
import sqlalchemy

from .__error__ import APIError, SimulationInProgress
from .db import NifflerDB
from .model import Alpha, AlphaSet, Simulation, SuperAlpha, SuperSimulation, User
from .utils import parse_record, silent_on_error


class NifflerAgent:
    """NifflerAgent

    世坤大脑平台本地代理, 封装大部分接口, 同时与本地因子库通讯.

    Properties
    ----------
    env_user / env_password : str
        账号密码环境变量
    expir_redun : timedelta
        令牌失效冗余
    """

    base_url: str = "https://api.worldquantbrain.com"
    auth_url: str = "/authentication"
    dataset_url: str = "/data-fields"
    operators_url: str = "/operators"
    alphaset_url: str = "/users/self/alphas"
    simulation_url: str = "/simulations"
    alpha_url: dict[str, str] = {
        "alpha": "/alphas/{alpha_id}",
        "pnl": "/alphas/{alpha_id}/recordsets/pnl",
        "check": "/alphas/{alpha_id}/check",
        "prod": "/alphas/{alpha_id}/correlations/prod",
        "perf": "/users/self/alphas/{alpha_id}/before-and-after-performance",
    }

    env_user: str = "WQ_USERNAME"
    env_password: str = "WQ_PASSWORD"
    expire_redun: timedelta = timedelta(hours=0.5)

    def __init__(
        self,
        dbengine: str | sqlalchemy.Engine | None,
        username: str | None = None,
        password: str | None = None,
        retry_delay: float = 10,
        max_retry: int = 10,
        request_concurrency: int = 5,
    ) -> None:
        username = username or os.getenv(self.env_user)
        password = password or os.getenv(self.env_password)
        assert username is not None, "用户名为空"
        self.username = username
        self.password = password
        self.db = NifflerDB(dbengine or "sqlite:///:memory:").build()

        self.retry_delay = retry_delay
        self.max_retry = max_retry

        self._logger = logging.getLogger(__name__)
        self._user: User | None = self.db.get_user(username=username)

        self.request_concurrency = request_concurrency

    # region: request

    def _send_request(
        self,
        client: httpx.Client,
        method: Literal["GET", "POST", "GET-Later", "PATCH"],
        url: str,
        params: dict | None = None,
        payload: dict | list | None = None,
    ) -> httpx.Response | None:
        """发送请求, 自动重试, 超限休眠

        Methods
        -------
        GET : 返回结果为 JSON
        POST : 不一定有返回内容
        GET-Later : 需要不断重试直到拿到内容
        PATCH : 使用同 GET

        Parameters
        ----------
        url : url-stem, 不需要 base_url
        params : url 请求参数, 会附在 url 上, ?&key=val
        payload : json 请求数据, 会在请求体里
        """

        match method:
            case "GET-Later":
                _method = "GET"
            case _:
                _method = method

        ntry = 0
        while self.max_retry - ntry > 0:
            try:
                res = client.request(
                    method=_method,
                    url=url,
                    timeout=None,
                    params=params,
                    json=payload,
                )
                if res.is_error:
                    # 如果异常报错, 可能是因为令牌过期
                    # 此时可能有其他并发的代理已经更新了 cookie
                    # 重新获取 cookie 尝试, 仅尝试一次
                    time.sleep(self.retry_delay)
                    self.user = self.get_user(force=True)
                    client.cookies = self.cookie
                    res = client.request(
                        method=_method,
                        url=url,
                        timeout=None,
                        params=params,
                        json=payload,
                    )
                # 检查状态码
                if res.is_error:
                    match res.status_code:
                        case 401:
                            self._logger.debug("Cookies 失效, 重新登陆")
                            self.user = self.login()
                            client.cookies = self.cookie
                            time.sleep(self.retry_delay)
                            continue
                        case 429:
                            self._logger.warning(
                                f"触发频率限制, 休眠 {self.retry_delay * 10=} 秒后重试"
                            )
                            time.sleep(self.retry_delay * 10)
                            continue
                        case 404:
                            # 404 是比较严重的非意外异常, 不用重试了
                            self._logger.error(f"{_method} {url} ERROR 404")
                            return None
                        case other:
                            ntry += 1
                            self._logger.debug(
                                f"{url} error({other}), retry [{ntry}/{self.max_retry}]"
                            )
                            time.sleep(self.retry_delay)
                            continue
                # 状态码没问题, 检查 GET 结果
                match method:
                    case "GET" | "PATCH":
                        if res.content is None:
                            ntry += 1
                            self._logger.debug(
                                f"{method} {url} Empty, retry [{ntry}/{self.max_retry}]"
                            )
                            time.sleep(self.retry_delay)
                            continue
                        else:
                            _ = res.json()
                    case "GET-Later":
                        retry_after = float(res.headers.get("Retry-After", 0))
                        if retry_after != 0:
                            time.sleep(retry_after + self.retry_delay)
                            continue
                        _ = res.json()
                    case _:
                        pass
                return res
            except Exception as e:
                ntry += 1
                self._logger.debug(f"Error: {e}, retry [{ntry}/{self.max_retry}]")
                time.sleep(self.retry_delay)
        self._logger.debug(f"请求失败 {url}")
        return None

    def get_user(self, force: bool = False) -> User:
        if (
            (self._user is not None)
            and (self._user.cookie is not None)
            and (self._user.update_time is not None)
            and (
                datetime.now() - self._user.update_time
                < timedelta(seconds=self._user.token_expiry) - self.expire_redun
            )
            and not force
        ):
            return self._user
        else:
            user = self.db.get_user(username=self.username)
            if (
                (user is not None)
                and (user.cookie is not None)
                and (user.update_time is not None)
                and (
                    datetime.now() - user.update_time
                    < timedelta(seconds=user.token_expiry) - self.expire_redun
                )
            ):
                return user
            else:
                _ = self.login()
                return self.get_user()

    def login(self) -> None:
        """登录功能

        登录功能单独实现, 如果登录失败, 后续所有功能都无法使用.
        """
        user = self.db.get_user(username=self.username)
        if self.password is None and user is not None:
            self.password = user.password
        assert self.password is not None, "未提供密码"
        with httpx.Client(
            auth=httpx.BasicAuth(self.username, self.password),
            base_url=self.base_url,
        ) as client:
            while True:
                try:
                    login = self._send_request(client, "POST", self.auth_url)
                    if login is not None:
                        self._logger.debug(f"登录成功: {login.json()['user']['id']}")
                        break
                    else:
                        continue
                except Exception as _:
                    self._logger.error(f"登录失败, {self.retry_delay} 秒后重试")
                    time.sleep(self.retry_delay)
        user = User.build(
            login.json(),
            username=self.username,
            password=self.password,
            cookie=login.cookies.get("t"),
        )
        self._user = self.db.add_user(user)

    @property
    def cookie(self) -> httpx.Cookies:
        user = self.get_user()
        return httpx.Cookies({"t": user.cookie or ""})

    def get(self, url: str, params: dict | None = None) -> dict | None:
        # FIXME: 返回值可能是 list
        with httpx.Client(cookies=self.cookie, base_url=self.base_url) as client:
            res = self._send_request(client, "GET", url, params=params)
            if res is not None:
                return res.json()
            else:
                return None

    def get_all(
        self,
        url: str,
        page_size: int,
        params: dict | None = None,
        count_key: str = "count",
        result_key: str = "results",
        concurrency: int | None = None,
    ) -> list[dict] | None:
        if concurrency is None:
            concurrency = self.request_concurrency

        offset = 0
        result = []
        ds0 = self.get(
            url,
            params={**(params or {}), "offset": offset, "limit": page_size},
        )
        if ds0 is None:
            return None

        total = ds0[count_key]
        result += ds0[result_key]

        offsets = list(range(page_size, total, page_size))
        self._logger.debug(f"分页加载进度: [{len(result)}/{total}]")
        if len(offsets) == 0:
            return result

        if concurrency > 0:
            with ThreadPoolExecutor(max_workers=int(concurrency)) as pool:
                tasks = {
                    pool.submit(
                        self.get,
                        url,
                        {**(params or {}), "offset": off, "limit": page_size},
                    ): off
                    for off in offsets
                }
                for rst in as_completed(tasks):
                    data = rst.result()
                    off = tasks[rst]
                    if data is None:
                        self._logger.error(f"分页加载失败(Offset={off})")
                        continue
                    result.extend(data[result_key])
                    self._logger.debug(f"分页加载进度: [{len(result)}/{total}]")
        else:
            offset += page_size
            while offset < total:
                _dataset = self.get(
                    url,
                    params={**(params or {}), "offset": offset, "limit": page_size},
                )
                if _dataset is None:
                    self._logger.error(f"分页加载失败(Offset={offset})")
                    continue
                result += _dataset[result_key]
                self._logger.debug(f"分页加载进度: [{len(result)}/{total}]")
                offset += page_size
        return result

    def post(self, url: str, payload: Any) -> httpx.Response | None:
        with httpx.Client(cookies=self.cookie, base_url=self.base_url) as client:
            return self._send_request(client, "POST", url, payload=payload)

    def patch(self, url: str, payload: Any) -> dict | None:
        with httpx.Client(cookies=self.cookie, base_url=self.base_url) as client:
            res = self._send_request(client, "PATCH", url, payload=payload)
            if res is not None:
                return res.json()
            return None

    # endregion

    # region: alpha

    @silent_on_error
    def get_alpha(self, alpha_id: str, force: bool = False) -> Alpha | SuperAlpha:
        ra = self.db.get_alpha(alpha_id)
        sa = self.db.get_superalpha(alpha_id)

        alpha: Alpha | SuperAlpha | None
        match [ra, sa]:
            case [None, a] if a is not None:
                alpha = a
            case [a, None] if a is not None:
                alpha = a
            case [None, None]:
                alpha = None
            case _:
                raise ValueError(f"{alpha_id} 无法判断是 RA 还是 SA, 请检查因子库")

        if alpha is not None and not force:
            return alpha

        alpha_record = self.get(self.alpha_url["alpha"].format(alpha_id=alpha_id))
        if alpha_record is None:
            raise ValueError(f"获取 Alpha 失败: {alpha_id}")
        match alpha_record["type"]:
            case "REGULAR":
                alpha = Alpha.build(alpha_record)
                alpha = self.db.add_alpha(alpha)
            case "SUPER":
                alpha = SuperAlpha.build(alpha_record)
                alpha = self.db.add_superalpha(alpha)
            case other:
                raise ValueError(f"未知的 Alpha 类型: {other}")
        return alpha

    @silent_on_error
    def get_pnl(self, alpha_id: str, force: bool = False) -> pl.DataFrame:
        """获取 PNL

        如果 Alpha 不在数据库里, 先获取 Alpha
        """
        alpha = self.get_alpha(alpha_id)
        if alpha is None:
            raise ValueError(f"获取 Alpha({alpha_id}) 失败")
        if (alpha.pnl is not None) and (not force):
            return parse_record(alpha.pnl)

        with httpx.Client(cookies=self.cookie, base_url=self.base_url) as client:
            res = self._send_request(
                client, "GET-Later", self.alpha_url["pnl"].format(alpha_id=alpha_id)
            )
            if res is None:
                raise ValueError(f"获取 Alpha({alpha_id}) PNL 失败")
        pnl_raw: dict[str, Any] = res.json()
        alpha.pnl = pnl_raw

        match alpha:
            case Alpha():
                _ = self.db.add_alpha(alpha)
            case SuperAlpha():
                _ = self.db.add_superalpha(alpha)
            case other:
                raise ValueError(f"未知的 Alpha 类型: {other}")
        return parse_record(pnl_raw)

    @silent_on_error
    def get_alphaset(
        self,
        alpha_type: str | None = None,
        region: str | None = None,
        universe: str | None = None,
        delay: int | None = None,
        status: Literal["ACTIVE", "UNSUBMITTED", "DECOMMISSIONED"] | None = None,
        date_from: datetime | str | None = None,
        date_to: datetime | str | None = None,
        sharpe: float | None = None,
        fitness: float | None = None,
        tag: str | None = None,
        name: str | None = None,
        category: str | None = None,
        color: str | None = None,
        date_split: int | timedelta | None = None,
        force: bool = False,
        date_begin: datetime = datetime(2025, 2, 12),
        concurrency: int | None = None,
    ) -> list[Alpha | SuperAlpha]:
        if isinstance(date_from, str):
            date_from = datetime.fromisoformat(date_from)
        if isinstance(date_to, str):
            date_to = datetime.fromisoformat(date_to)
        if date_to is not None and date_to > datetime.now():
            date_to = datetime.now()

        alphaset = AlphaSet(
            alpha_type=alpha_type,
            region=region,
            universe=universe,
            delay=delay,
            status=status,
            date_from=date_from,
            date_to=date_to,
            sharpe=sharpe,
            fitness=fitness,
            tag=tag,
            name=name,
            category=category,
            color=color,
        )

        alphaset_get = self.db.get_alphaset(alphaset.hashing())
        if alphaset_get is not None and alphaset_get.frozen and not force:
            alphas_candidate = [self.get_alpha(a) for a in alphaset_get.alphas]
            alphas = [a for a in alphas_candidate if a is not None]
            self._logger.debug(
                f"Frozen AlphaSet({date_from or ''}~{date_to or ''}) 加载完成, "
                f"共 {len(alphas)} 个 Alpha"
            )
            return alphas

        # 时间切分
        match date_split:
            case float() | int() as i if i > 0:
                date_split = timedelta(days=i)
            case timedelta():
                pass
            case _:
                date_split = None

        alphas: list[Alpha | SuperAlpha] = []
        if date_split is not None:
            current_date = date_from or date_begin
            while current_date <= (date_to or datetime.now()):
                _alphaset_get_split = self.get_alphaset(
                    alpha_type=alpha_type,
                    region=region,
                    universe=universe,
                    delay=delay,
                    status=status,
                    date_from=current_date,
                    date_to=current_date + date_split,
                    sharpe=sharpe,
                    fitness=fitness,
                    tag=tag,
                    name=name,
                    category=category,
                    color=color,
                    date_split=None,
                    force=force,
                    date_begin=date_begin,
                )
                if _alphaset_get_split is not None:
                    alphas += _alphaset_get_split
                current_date += date_split
            return alphas

        # 正常获取
        params: dict[str, Any] = alphaset.to_params()
        alphaset_dicts = self.get_all(
            self.alphaset_url, page_size=100, params=params, concurrency=concurrency
        )
        if alphaset_dicts is None:
            raise ValueError("获取 AlphaSet 失败")

        alphas += [
            (Alpha.build(rst) if rst["type"] == "REGULAR" else SuperAlpha.build(rst))
            for rst in alphaset_dicts
        ]

        alphaset.alphas = [a.id for a in alphas]
        alphaset_get = self.db.get_alphaset(alphaset.hashing())
        if alphaset_get is not None:
            alphaset.id = alphaset_get.id
        alphaset = self.db.add_alphaset(alphaset)

        regular_alphas = self.db.add_alpha([a for a in alphas if isinstance(a, Alpha)])
        super_alphas = self.db.add_superalpha(
            [a for a in alphas if isinstance(a, SuperAlpha)]
        )

        self._logger.debug(f"AlphaSet 加载完成, 一共 {len(alphas)} 个 Alpha.")
        return regular_alphas + super_alphas

    @silent_on_error
    def update_alpha(
        self,
        alpha_id: str,
        name: str | None = None,
        category: str | None = None,
        description: str | None = None,
        color: str | None = None,
        tags: list[str] | str | None = None,
        hidden: bool | None = None,
        favorite: bool | None = None,
        overwrite: bool = False,
    ) -> Alpha:
        alpha = self.get_alpha(alpha_id)
        if alpha is None:
            raise ValueError(f"获取 Alpha({alpha_id}) 失败")
        if isinstance(alpha, SuperAlpha):
            raise ValueError(
                f"Alpha({alpha_id}) 是 SuperAlpha, 请使用 agent.update_superalpha 方法"
            )

        # 如果 name / category / description / ... 全部都是 None
        # 如果某一项 不是 None 但跟 alpha 的值一样
        # 满足上面两个条件, 非覆盖情况下, 不需要更新
        need_update = False
        if not overwrite:
            for prop_field, prop in zip(
                [
                    "name",
                    "category",
                    "description",
                    "color",
                    "tags",
                    "hidden",
                    "favorite",
                ],
                [name, category, description, color, tags, hidden, favorite],
            ):
                if (prop is not None) and (prop != getattr(alpha, prop_field)):
                    self._logger.debug(
                        f"Alpha({alpha.id}).{prop_field} = {getattr(alpha, prop_field)} "
                        f"-> {prop_field} = {prop}, 需要更新"
                    )
                    need_update = True
                    break
        else:
            need_update = True

        if overwrite:
            alpha.name = name
            alpha.category = category
            alpha.description = description
            alpha.color = color
            alpha.hidden = hidden if hidden is not None else alpha.hidden
            alpha.favorite = favorite if favorite is not None else alpha.favorite
            match tags:
                case list() as t:
                    alpha.tags = t
                case str() as t:
                    alpha.tags.append(t)
                case _:
                    pass
        elif need_update:
            alpha.name = name if name is not None else alpha.name
            alpha.category = category if category is not None else alpha.category
            alpha.description = (
                description if description is not None else alpha.description
            )
            alpha.color = color if color is not None else alpha.color
            alpha.hidden = hidden if hidden is not None else alpha.hidden
            alpha.favorite = favorite if favorite is not None else alpha.favorite

            match tags:
                case list() as t:
                    alpha.tags += t
                case str() as t:
                    alpha.tags.append(t)
                case _:
                    pass
        else:
            return alpha

        alpha_record = self.patch(
            url=self.alpha_url["alpha"].format(alpha_id=alpha_id),
            payload=alpha.to_payload(mode="description"),
        )
        if alpha_record is None:
            raise ValueError(f"Patch Alpha({alpha_id}) error")
        return self.db.add_alpha(Alpha.build(alpha_record))

    @silent_on_error
    def update_superalpha(
        self,
        alpha_id: str,
        name: str | None = None,
        category: str | None = None,
        combo_descprition: str | None = None,
        selection_descprition: str | None = None,
        color: str | None = None,
        tags: list[str] | str | None = None,
        hidden: bool | None = None,
        favorite: bool | None = None,
        overwrite: bool = False,
    ) -> Alpha:
        alpha = self.get_alpha(alpha_id)
        if alpha is None:
            raise ValueError(f"获取 Alpha({alpha_id}) 失败")
        if isinstance(alpha, Alpha):
            raise ValueError(
                f"Alpha({alpha_id}) 是 RegularAlpha, 请使用 agent.update_alpha 方法"
            )

        if overwrite:
            alpha.name = name
            alpha.category = category
            alpha.combo_description = combo_descprition
            alpha.selection_description = selection_descprition
            alpha.color = color
            alpha.hidden = hidden if hidden is not None else alpha.hidden
            alpha.favorite = favorite if favorite is not None else alpha.favorite

            match tags:
                case list() as t:
                    alpha.tags = t
                case str() as t:
                    alpha.tags.append(t)
                case _:
                    pass
        else:
            alpha.name = name if name is not None else alpha.name
            alpha.category = category if category is not None else alpha.category
            alpha.combo_description = (
                combo_descprition
                if combo_descprition is not None
                else alpha.combo_description
            )
            alpha.selection_description = (
                selection_descprition
                if selection_descprition is not None
                else alpha.selection_description
            )
            alpha.color = color if color is not None else alpha.color
            alpha.hidden = hidden if hidden is not None else alpha.hidden
            alpha.favorite = favorite if favorite is not None else alpha.favorite

            match tags:
                case list() as t:
                    alpha.tags += t
                case str() as t:
                    alpha.tags.append(t)
                case _:
                    pass

        alpha_record = self.patch(
            url=self.alpha_url["alpha"].format(alpha_id=alpha_id),
            payload=alpha.to_payload(mode="description"),
        )
        if alpha_record is None:
            raise ValueError(f"Patch Alpha({alpha_id}) error")
        return self.db.add_alpha(Alpha.build(alpha_record))

    # endregion

    # region: simulate

    @overload
    def _simulate(self, simulation: Simulation | list[Simulation]) -> str: ...
    @overload
    def _simulate(self, simulation: SuperSimulation) -> str: ...
    def _simulate(
        self, simulation: Simulation | list[Simulation] | SuperSimulation
    ) -> str:
        """Alpha 回测

        支持单 RA 回测, SA 回测, Multi-RA 回测.
        与平台一样, 异步回测模式, 直接返回 simid
        """
        match simulation:
            case Simulation() as s:
                payload = s.to_payload()
            case list() as ss if all(isinstance(s, Simulation) for s in ss):
                payload = [s.to_payload() for s in ss]
                if nbatch := len(payload) > 10:
                    raise ValueError(f"批回测数量 {nbatch} > 10.")
            case SuperSimulation() as s:
                payload = s.to_payload()
            case _:
                raise ValueError("不支持的 Simulation 类型")

        resp = self.post(url=self.simulation_url, payload=payload)
        if resp is None:
            raise ValueError("回测失败")

        simid = resp.headers.get("Location").split("/")[-1]
        return simid

    def _get_simulation_result(self, simid: str) -> list[Alpha] | Alpha | SuperAlpha:
        """获取回测结果

        Parameters
        ----------
        simid : str
            回测 ID

        Returns
        -------
        alphas : list[Alpha]

        Raise
        -----
        SimulationInProgress
            如果回测未完成, 会抛出异常

        Notes
        -----
        * 平台本身自带冗余控制, 短时间内完全一样的回测内容会自动合并, 该函数最终返回结果可能有重复值
        """
        sim_result = self.get(f"{self.simulation_url}/{simid}")
        if sim_result is None:
            raise ValueError(f"获取回测结果失败: {simid}")

        if "progress" in sim_result:
            raise SimulationInProgress(simid=simid, progress=sim_result["progress"])

        if "children" in sim_result:
            # multi-sim regular alpha
            sim_result_all = [
                self.get(f"{self.simulation_url}/{sid}")
                for sid in sim_result["children"]
            ]

            if sim_result["status"] != "COMPLETE":
                error_sims = filter(
                    lambda x: x is not None and x["status"] == "ERROR", sim_result_all
                )
                for es in error_sims:
                    if es is not None:
                        self._logger.error(f"回测 {es['id']} 失败: {es['message']}")
                raise ValueError(f"批量回测失败, simid: {simid}")

            sim_result_all = [
                self.get_alpha(r["alpha"]) for r in sim_result_all if r is not None
            ]
            alphas = [a for a in sim_result_all if isinstance(a, Alpha)]
            return alphas

        alpha = self.get_alpha(sim_result["alpha"])
        if alpha is None:
            raise ValueError("获取回测 Alpha 失败")
        return alpha

    @overload
    def _sim_and_get(self, simulation: Simulation) -> Alpha: ...
    @overload
    def _sim_and_get(self, simulation: SuperSimulation) -> SuperAlpha: ...
    @overload
    def _sim_and_get(self, simulation: list[Simulation]) -> list[Alpha]: ...
    def _sim_and_get(
        self, simulation: Simulation | list[Simulation] | SuperSimulation
    ) -> list[Alpha] | Alpha | SuperAlpha:
        """回测并获取结果"""
        simid = self._simulate(simulation)
        # Try to get simulation result
        progress = 0.0
        while True:
            try:
                alphas = self._get_simulation_result(simid)
                break
            except SimulationInProgress as e:
                if e.progress is not None and e.progress > progress:
                    progress = e.progress
                    self._logger.debug(f"Sim({e.simid}) Progress: {progress:.0%}")
                time.sleep(self.retry_delay)

        self._logger.debug(f"Sim{simid} finished.")
        return alphas

    @overload
    async def _async_sim_and_get(self, simulation: Simulation) -> Alpha: ...
    @overload
    async def _async_sim_and_get(self, simulation: SuperSimulation) -> SuperAlpha: ...
    @overload
    async def _async_sim_and_get(self, simulation: list[Simulation]) -> list[Alpha]: ...
    async def _async_sim_and_get(
        self, simulation: Simulation | list[Simulation] | SuperSimulation
    ) -> list[Alpha] | Alpha | SuperAlpha:
        """回测并获取结果"""
        simid = self._simulate(simulation)
        # Try to get simulation result
        progress = 0.0
        while True:
            try:
                alphas = await asyncio.to_thread(self._get_simulation_result, simid)
                break
            except SimulationInProgress as e:
                if e.progress is not None and e.progress > progress:
                    progress = e.progress
                    self._logger.debug(f"Sim({e.simid}) Progress: {progress:.0%}")
                await asyncio.sleep(self.retry_delay)

        self._logger.debug(f"Sim{simid} finished.")
        return alphas

    @overload
    def simulate(self, simulation: Simulation, force: bool = False) -> Simulation: ...
    @overload
    def simulate(
        self, simulation: list[Simulation], force: bool = False
    ) -> list[Simulation]: ...
    @overload
    def simulate(
        self, simulation: SuperSimulation, force: bool = False
    ) -> SuperSimulation: ...

    @silent_on_error
    def simulate(
        self,
        simulation: list[Simulation] | Simulation | SuperSimulation,
        force: bool = False,
    ) -> list[Simulation] | Simulation | SuperSimulation:
        """回测接口: 同步模式"""
        # 检查是否已存在, 直接返回
        if not force and self.is_simulated(simulation):
            match simulation:
                case Simulation() as s:
                    # 单 Alpha 回测
                    sim_get = self.db.get_simulation(simhash=s.hashing())
                    assert sim_get is not None, "获取 Simulation 失败, 检查本地数据库"
                    return sim_get[0]
                case list() as ss if all(isinstance(s, Simulation) for s in ss):
                    sim_get = [self.db.get_simulation(simhash=s.hashing()) for s in ss]
                    sim_get = [sg[0] for sg in sim_get if sg is not None]
                    return sim_get
                case SuperSimulation() as s:
                    sim_get = self.db.get_super_simulation(simhash=s.hashing())
                    assert sim_get is not None, (
                        "获取 SuperSimulation 失败, 检查本地数据库"
                    )
                    return sim_get[0]
                case _:
                    raise ValueError(f"不支持的 Simulation 类型: {type(simulation)}")

        # 之前没有回测过
        simid = self._simulate(simulation)
        # Try to get simulation result
        progress = 0.0
        while True:
            try:
                alphas = self._get_simulation_result(simid)
                break
            except SimulationInProgress as e:
                if e.progress is not None and e.progress > progress:
                    progress = e.progress
                    self._logger.debug(f"Sim({e.simid}) Progress: {progress:.0%}")
                time.sleep(self.retry_delay)

        self._logger.debug(f"Sim{simid} finished.")

        match alphas:
            case Alpha():
                assert isinstance(simulation, Simulation)
                simulation.simid = simid
                simulation.alpha_id = alphas.id
                sim_update = self.db.add_simulation(simulation)
                alphas = (
                    self.update_alpha(
                        alphas.id,
                        name=simulation.name,
                        category=simulation.category,
                        description=simulation.description,
                        color=simulation.color,
                        tags=simulation.tags,
                        hidden=simulation.hidden,
                        favorite=simulation.favorite,
                        overwrite=False,
                    )
                    or alphas
                )
            case SuperAlpha():
                assert isinstance(simulation, SuperSimulation)
                simulation.simid = simid
                simulation.alpha_id = alphas.id
                sim_update = self.db.add_super_simulation(simulation)
                alphas = (
                    self.update_superalpha(
                        alphas.id,
                        name=simulation.name,
                        category=simulation.category,
                        combo_descprition=simulation.combo_description,
                        selection_descprition=simulation.selection_description,
                        color=simulation.color,
                        tags=simulation.tags,
                        hidden=simulation.hidden,
                        favorite=simulation.favorite,
                        overwrite=False,
                    )
                    or alphas
                )
            case list() as aa if all(isinstance(a, Alpha) for a in aa):
                assert isinstance(simulation, list)
                for idx, (sim, a) in enumerate(zip(simulation, alphas)):
                    simulation[idx].simid = simid
                    simulation[idx].alpha_id = a.id
                    alphas[idx] = (
                        self.update_alpha(
                            a.id,
                            name=sim.name,
                            category=sim.category,
                            description=sim.description,
                            color=sim.color,
                            tags=sim.tags,
                            hidden=sim.hidden,
                            favorite=sim.favorite,
                            overwrite=False,
                        )
                        or alphas[idx]
                    )
                sim_update = self.db.add_simulation(simulation)
            case _:
                raise ValueError(f"未知的 Simulation Result 类型: {type(alphas)}")
        return sim_update

    @overload
    async def async_simulate(
        self, simulation: Simulation, force: bool = False
    ) -> Simulation: ...
    @overload
    async def async_simulate(
        self, simulation: list[Simulation], force: bool = False
    ) -> list[Simulation]: ...
    @overload
    async def async_simulate(
        self, simulation: SuperSimulation, force: bool = False
    ) -> SuperSimulation: ...
    @silent_on_error
    async def async_simulate(
        self,
        simulation: list[Simulation] | Simulation | SuperSimulation,
        force: bool = False,
    ) -> list[Simulation] | Simulation | SuperSimulation:
        """回测接口: 同步模式"""
        # 检查是否已存在, 直接返回
        if not force and self.is_simulated(simulation):
            match simulation:
                case Simulation() as s:
                    # 单 Alpha 回测
                    sim_get = self.db.get_simulation(simhash=s.hashing())
                    assert sim_get is not None, "获取 Simulation 失败, 检查本地数据库"
                    return sim_get[0]
                case list() as ss if all(isinstance(s, Simulation) for s in ss):
                    sim_get = [self.db.get_simulation(simhash=s.hashing()) for s in ss]
                    sim_get = [sg[0] for sg in sim_get if sg is not None]
                    return sim_get
                case SuperSimulation() as s:
                    sim_get = self.db.get_super_simulation(simhash=s.hashing())
                    assert sim_get is not None, (
                        "获取 SuperSimulation 失败, 检查本地数据库"
                    )
                    return sim_get[0]
                case _:
                    raise ValueError(f"不支持的 Simulation 类型: {type(simulation)}")

        # 之前没有回测过
        simid = self._simulate(simulation)
        # Try to get simulation result
        progress = 0.0
        while True:
            try:
                alphas = await asyncio.to_thread(self._get_simulation_result, simid)
                break
            except SimulationInProgress as e:
                if e.progress is not None and e.progress > progress:
                    progress = e.progress
                    self._logger.debug(f"Sim({e.simid}) Progress: {progress:.0%}")
                time.sleep(self.retry_delay)

        self._logger.debug(f"Sim{simid} finished.")

        match alphas:
            case Alpha():
                assert isinstance(simulation, Simulation)
                simulation.simid = simid
                simulation.alpha_id = alphas.id
                sim_update = self.db.add_simulation(simulation)
                alphas = (
                    self.update_alpha(
                        alphas.id,
                        name=simulation.name,
                        category=simulation.category,
                        description=simulation.description,
                        color=simulation.color,
                        tags=simulation.tags,
                        hidden=simulation.hidden,
                        favorite=simulation.favorite,
                        overwrite=False,
                    )
                    or alphas
                )
            case SuperAlpha():
                assert isinstance(simulation, SuperSimulation)
                simulation.simid = simid
                simulation.alpha_id = alphas.id
                sim_update = self.db.add_super_simulation(simulation)
                alphas = (
                    self.update_superalpha(
                        alphas.id,
                        name=simulation.name,
                        category=simulation.category,
                        combo_descprition=simulation.combo_description,
                        selection_descprition=simulation.selection_description,
                        color=simulation.color,
                        tags=simulation.tags,
                        hidden=simulation.hidden,
                        favorite=simulation.favorite,
                        overwrite=False,
                    )
                    or alphas
                )
            case list() as aa if all(isinstance(a, Alpha) for a in aa):
                assert isinstance(simulation, list)
                for idx, (sim, a) in enumerate(zip(simulation, alphas)):
                    simulation[idx].simid = simid
                    simulation[idx].alpha_id = a.id
                    alphas[idx] = (
                        self.update_alpha(
                            a.id,
                            name=sim.name,
                            category=sim.category,
                            description=sim.description,
                            color=sim.color,
                            tags=sim.tags,
                            hidden=sim.hidden,
                            favorite=sim.favorite,
                            overwrite=False,
                        )
                        or alphas[idx]
                    )
                sim_update = self.db.add_simulation(simulation)
            case _:
                raise ValueError(f"未知的 Simulation Result 类型: {type(alphas)}")
        return sim_update

    def is_simulated(
        self, simulation: list[Simulation] | Simulation | SuperSimulation
    ) -> bool:
        match simulation:
            case Simulation() as s:
                sim_get = self.db.get_simulation(simhash=s.hashing())
                if sim_get is None:
                    return False
            case list() as ss if all(isinstance(s, Simulation) for s in ss):
                sim_get = [self.db.get_simulation(simhash=s.hashing()) for s in ss]
                sim_get = [s[0] for s in sim_get if s is not None]
                if len(sim_get) != len(ss):
                    return False
            case SuperSimulation() as s:
                sim_get = self.db.get_super_simulation(simhash=s.hashing())
                if sim_get is None:
                    return False
            case _:
                raise ValueError("不支持的 Simulation 类型")
        return True

    # endregion

    # region: dataset & operators

    @silent_on_error
    def get_dataset(
        self,
        region: str,
        universe: str,
        delay: int,
        dataset: str,
        instrument: str = "EQUITY",
        concurrency: int | None = None,
    ) -> list[dict[str, Any]]:
        params = {
            "instrumentType": instrument,
            "region": region,
            "universe": universe,
            "delay": delay,
            "dataset.id": dataset,
        }
        result = self.get_all(
            url=self.dataset_url, page_size=50, params=params, concurrency=concurrency
        )
        if result is None:
            raise APIError(f"获取数据集失败: {region}-{universe}-{delay} {dataset}")
        return result

    @silent_on_error
    def get_operators(self, retrive_docs: bool = False) -> list[dict]:
        operators = self.get(self.operators_url)
        if operators is None:
            raise APIError("获取操作符失败")
        if isinstance(operators, dict):
            operators = [operators]

        docs: dict[int, str] = {}
        for idx, op in enumerate(operators):
            if op.get("documentation") is not None:
                docs[idx] = op["documentation"]

        if retrive_docs:
            with ThreadPoolExecutor(
                max_workers=int(self.request_concurrency) or 1
            ) as pool:
                tasks = {pool.submit(self.get, url): idx for idx, url in docs.items()}
                for rst in as_completed(tasks):
                    data = rst.result()
                    idx = tasks[rst]
                    if data is None:
                        self._logger.error(
                            f"运算符文档加载失败: {operators[idx]['name']}"
                        )
                        continue
                    operators[idx]["documentation"] = data
                    self._logger.debug(f"加载运算符文档: {operators[idx]['name']}")
        return operators

    # endregion

    # region: check

    @silent_on_error
    def check_prod(self, alpha_id: str, force: bool = False) -> float:
        """Check Alpha Prod Corr

        如果 Alpha 不在数据库里, 先获取 Alpha
        """
        alpha = self.get_alpha(alpha_id)
        if alpha is None:
            raise APIError("获取 Alpha 失败")
        if alpha.prod is not None and not force and alpha.prod > 0.7:
            return alpha.prod

        with httpx.Client(cookies=self.cookie, base_url=self.base_url) as client:
            res = self._send_request(
                client, "GET-Later", self.alpha_url["prod"].format(alpha_id=alpha_id)
            )
            if res is None:
                raise APIError("获取 Prod-Corr 失败")
            rst = res.json()
        alpha.prod_raw = rst
        alpha.prod = rst.get("max")
        match alpha:
            case Alpha():
                _ = self.db.add_alpha(alpha)
            case SuperAlpha():
                _ = self.db.add_superalpha(alpha)
            case _:
                raise ValueError("位置的 Alpha 类型")
        return alpha.prod

    # endregion
