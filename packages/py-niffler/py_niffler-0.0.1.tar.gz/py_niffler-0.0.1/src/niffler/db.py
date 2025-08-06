import itertools
import logging
import unittest
from datetime import datetime
from typing import Self, TypeVar, overload

import sqlalchemy
from sqlmodel import Session, asc, inspect, select

from .model import (
    Alpha,
    AlphaSet,
    Simulation,
    SQLModel,
    SuperAlpha,
    SuperSimulation,
    User,
)

T = TypeVar("T", bound=SQLModel, covariant=True)
PK = TypeVar("PK", str, int)
logger = logging.getLogger(__name__)


class NifflerDB:
    """本地因子集管理器"""

    def __init__(self, engine: str | sqlalchemy.Engine) -> None:
        self._logger = logging.getLogger(__name__)
        if isinstance(engine, str):
            self.engine = sqlalchemy.create_engine(engine)
        else:
            self.engine = engine

    def build(self) -> Self:
        SQLModel.metadata.create_all(self.engine)
        return self

    @staticmethod
    def update_model(old: T, new: T, overwrite: bool = False) -> T:
        """更新模型

        如果 overwrite, 直接覆盖, 否则只更新非空字段.
        如果 update_time 属性存在, 自动更新.
        """

        if overwrite:
            old = old.sqlmodel_update(new)
        else:
            props = [
                p
                for p in old.__class__.model_fields.keys()
                if (p not in ["id"]) and (getattr(new, p) is not None)
            ]
            for p in props:
                setattr(old, p, getattr(new, p))

        if getattr(old, "update_time") is not None:
            setattr(old, "update_time", datetime.now())
        return old

    @overload
    def _get_object_by_id(self, oid: PK, model: type[T]) -> T | None: ...
    @overload
    def _get_object_by_id(self, oid: list[PK], model: type[T]) -> list[T] | None: ...
    def _get_object_by_id(
        self, oid: PK | list[PK], model: type[T]
    ) -> T | list[T] | None:
        """根据主键获取对象

        如果传入的是 list 则返回 list, 如果查询结果为空, 则返回 None
        """
        pk = inspect(model).primary_key[0].name
        with Session(self.engine) as session:
            if isinstance(oid, list):
                statement: sqlalchemy.Select = select(model).where(
                    getattr(model, pk).in_(oid)
                )
                return list(session.exec(statement).all()) or None
            else:
                return session.get(model, oid)

    @overload
    def _add_or_update_object(
        self, obj: T, model: type[T], overwrite: bool = False
    ) -> T: ...
    @overload
    def _add_or_update_object(
        self, obj: list[T], model: type[T], overwrite: bool = False
    ) -> list[T]: ...
    def _add_or_update_object(
        self, obj: T | list[T], model: type[T], overwrite: bool = False
    ) -> T | list[T]:
        """添加或更新对象"""
        pk = inspect(model).primary_key[0].name

        if isinstance(obj, list):
            return_single = False
            objs = obj
        else:
            return_single = True
            objs = [obj]

        def _safe_key(x, counter=itertools.count()):
            v = getattr(x, pk, None)
            # 用 (is_none_flag, value_or_uuid) 保证：
            #   1) None 始终排在最后
            #   2) 每个 None 对象仍然独一无二
            return (0, v) if v is not None else (1, -1 - next(counter))

        objs = [
            k
            for _, (k, *_) in itertools.groupby(
                sorted(objs, key=_safe_key),
                key=lambda x: str(_safe_key(x)[1]),  # 只按真正的 pk 值去重
            )
        ]
        with Session(self.engine) as session:
            # 获取存量
            # pks: objs 中所有不为空的主键(如果主键为空表示纯新增)
            # pks_map: pk~obj 映射
            # objs_stock: 根据 pks 获取的存量
            pks = [p for p in [getattr(o, pk) for o in objs] if p is not None]
            pks_map = {p: o for o in objs if (p := getattr(o, pk)) in pks}
            objs_stock = self._get_object_by_id(oid=pks, model=model)
            if objs_stock is not None:
                for idx, o in enumerate(objs_stock):
                    objs_stock[idx] = self.update_model(
                        o, pks_map[getattr(o, pk)], overwrite=overwrite
                    )
                session.add_all(objs_stock)
            # 获取新增
            pks_stock = [getattr(o, pk) for o in objs_stock or []]
            objs_new = [o for o in objs if getattr(o, pk) not in pks_stock]
            if len(objs_new) != 0:
                session.add_all(objs_new)
            # Commit
            session.commit()
            for o in objs_new:
                session.refresh(o)
            for o in objs_stock or []:
                session.refresh(o)
            # Log
            if objs_stock is not None:
                self._logger.debug(f"更新 {len(objs_stock)} 个 {model.__name__}")
            if len(objs_new) != 0:
                self._logger.debug(f"新增 {len(objs_new)} 个 {model.__name__}")

        final_obj = (objs_stock or []) + objs_new
        if len(final_obj) != len(objs):
            self._logger.warning(
                f"结果集数量有误, 应该为 {len(objs)}, 实际为 {len(final_obj)}"
            )
        if return_single:
            return final_obj[-1]
        else:
            return final_obj

    def get_user(
        self, userid: str | None = None, username: str | None = None
    ) -> User | None:
        assert not (userid is None and username is None), "userid 和 username 全为空"
        with Session(self.engine) as session:
            if userid is not None:
                user = self._get_object_by_id(userid, User)
                return user
            else:
                statement: sqlalchemy.Select = select(User).where(
                    User.username == username
                )
                return session.exec(statement).first()

    def add_user(self, user: User) -> User:
        _user = self._add_or_update_object(user, User, overwrite=True)
        return _user

    @overload
    def get_alpha(self, alpha_id: str) -> Alpha | None: ...
    @overload
    def get_alpha(self, alpha_id: list[str]) -> list[Alpha] | None: ...
    def get_alpha(self, alpha_id: str | list[str]) -> Alpha | list[Alpha] | None:
        _alpha = self._get_object_by_id(alpha_id, Alpha)
        return _alpha

    @overload
    def get_superalpha(self, superalpha_id: str) -> SuperAlpha | None: ...
    @overload
    def get_superalpha(self, superalpha_id: list[str]) -> list[SuperAlpha] | None: ...
    def get_superalpha(
        self, superalpha_id: str | list[str]
    ) -> SuperAlpha | list[SuperAlpha] | None:
        _superalpha = self._get_object_by_id(superalpha_id, SuperAlpha)
        return _superalpha

    @overload
    def add_alpha(self, alpha: Alpha) -> Alpha: ...
    @overload
    def add_alpha(self, alpha: list[Alpha]) -> list[Alpha]: ...
    def add_alpha(self, alpha: Alpha | list[Alpha]) -> Alpha | list[Alpha]:
        _alpha = self._add_or_update_object(alpha, Alpha)
        return _alpha

    @overload
    def add_superalpha(self, superalpha: SuperAlpha) -> SuperAlpha: ...
    @overload
    def add_superalpha(self, superalpha: list[SuperAlpha]) -> list[SuperAlpha]: ...
    def add_superalpha(
        self, superalpha: SuperAlpha | list[SuperAlpha]
    ) -> SuperAlpha | list[SuperAlpha]:
        _superalpha = self._add_or_update_object(superalpha, SuperAlpha)
        return _superalpha

    @overload
    def add_or_get_alpha(self, alpha: Alpha) -> Alpha: ...
    @overload
    def add_or_get_alpha(self, alpha: list[Alpha]) -> list[Alpha]: ...
    def add_or_get_alpha(self, alpha: Alpha | list[Alpha]) -> Alpha | list[Alpha]:
        if isinstance(alpha, list):
            return_single = False
            alphas = alpha
        else:
            return_single = True
            alphas = [alpha]

        alpha_get = self.get_alpha([a.id for a in alphas])
        aid_get = [a.id for a in alpha_get or []]

        alpha_add = [a for a in alphas if a.id not in aid_get]
        alpha_add = self.add_alpha(alpha_add)
        result = (alpha_get or []) + alpha_add

        if return_single:
            return result[-1]
        else:
            return result

    @overload
    def add_or_get_superalpha(self, superalpha: SuperAlpha) -> SuperAlpha: ...
    @overload
    def add_or_get_superalpha(
        self, superalpha: list[SuperAlpha]
    ) -> list[SuperAlpha]: ...
    def add_or_get_superalpha(
        self, superalpha: SuperAlpha | list[SuperAlpha]
    ) -> SuperAlpha | list[SuperAlpha]:
        if isinstance(superalpha, list):
            return_single = False
            superalphas = superalpha
        else:
            return_single = True
            superalphas = [superalpha]

        superalpha_get = self.get_superalpha([a.id for a in superalphas])
        said_get = [sa.id for sa in superalpha_get or []]

        superalpha_add = [sa for sa in superalphas if sa.id not in said_get]
        superalpha_add = self.add_superalpha(superalpha_add)
        result = (superalpha_get or []) + superalpha_add

        if return_single:
            return result[-1]
        else:
            return result

    def get_simulation(
        self, simid: str | None = None, simhash: str | None = None
    ) -> list[Simulation] | None:
        """通过 SimID 或者 SimHash(encode) 来检索 Simulation

        不通过主键检索, 所以结果可能为 Sim-Batch
        """
        assert not (simid is None and simhash is None), "simid 和 simhash 全为空"
        with Session(self.engine) as session:
            if simid is not None:
                statement: sqlalchemy.Select = (
                    select(Simulation)
                    .where(Simulation.simid == simid)
                    .order_by(asc(Simulation.update_time))
                )
            else:
                statement: sqlalchemy.Select = (
                    select(Simulation)
                    .where(Simulation.encode == simhash)
                    .order_by(asc(Simulation.update_time))
                )
            sim = list(session.exec(statement).all())
            return sim or None

    def get_super_simulation(
        self, simid: str | None = None, simhash: str | None = None
    ) -> list[SuperSimulation] | None:
        """通过 SuperSimID 或者 SuperSimHash(encode) 来检索 Simulation

        不通过主键检索, 所以结果可能为 Sim-Batch
        """
        assert not (simid is None and simhash is None), "simid 和 simhash 全为空"
        with Session(self.engine) as session:
            if simid is not None:
                statement: sqlalchemy.Select = select(SuperSimulation).where(
                    SuperSimulation.simid == simid
                )
            else:
                statement: sqlalchemy.Select = select(SuperSimulation).where(
                    SuperSimulation.encode == simhash
                )
            super_sim = list(session.exec(statement).all())
            return super_sim or None

    @overload
    def add_simulation(self, simulation: Simulation) -> Simulation: ...
    @overload
    def add_simulation(self, simulation: list[Simulation]) -> list[Simulation]: ...
    def add_simulation(
        self, simulation: Simulation | list[Simulation]
    ) -> Simulation | list[Simulation]:
        sim = self._add_or_update_object(simulation, Simulation)
        return sim

    @overload
    def add_super_simulation(self, simulation: SuperSimulation) -> SuperSimulation: ...
    @overload
    def add_super_simulation(
        self, simulation: list[SuperSimulation]
    ) -> list[SuperSimulation]: ...
    def add_super_simulation(
        self, simulation: SuperSimulation | list[SuperSimulation]
    ) -> SuperSimulation | list[SuperSimulation]:
        sim = self._add_or_update_object(simulation, SuperSimulation)
        return sim

    def add_alphaset(self, alphaset: AlphaSet) -> AlphaSet:
        alphaset = self._add_or_update_object(alphaset, AlphaSet)
        return alphaset

    def get_alphaset(self, alphaset_hash: str) -> AlphaSet | None:
        """根据哈希获取因子集

        只返回最新更新的一条因子集.
        """
        with Session(self.engine) as session:
            statement: sqlalchemy.Select = (
                select(AlphaSet)
                .where(AlphaSet.encode == alphaset_hash)
                .order_by(asc(AlphaSet.update_time))
            )
            alphaset = session.exec(statement).first()
            return alphaset


class TestNifflerDB(unittest.TestCase):
    def setUp(self) -> None:
        self.db = NifflerDB("sqlite:///:memory:").build()
        self.alpha_record = {
            "id": "ZNpVbmY",
            "type": "REGULAR",
            "author": "ZH87224",
            "settings": {
                "instrumentType": "EQUITY",
                "region": "EUR",
                "universe": "TOP2500",
                "delay": 1,
                "decay": 4,
                "neutralization": "SUBINDUSTRY",
                "truncation": 0.08,
                "pasteurization": "ON",
                "unitHandling": "VERIFY",
                "nanHandling": "ON",
                "maxTrade": "OFF",
                "language": "FASTEXPR",
                "visualization": False,
                "startDate": "2013-01-20",
                "endDate": "2023-01-20",
            },
            "regular": {
                "code": "ts_zscore(winsorize(ts_backfill(oth455_partner_n2v_p50_q50_w5_pca_fact1_value, 120), std=4), 5)",
                "description": "Idea: ts_zscore(winsorize(ts_backfill(oth455_partner_n2v_p50_q50_w5_pca_fact1_value, 120), std=4), 5)\nRationale for data used: -\nRationale for operators used: -",
                "operatorCount": 3,
            },
            "dateCreated": "2025-07-18T23:32:42-04:00",
            "dateSubmitted": None,
            "dateModified": "2025-07-21T02:17:13-04:00",
            "name": "other455_EUR1_TOP2500_1step",
            "favorite": False,
            "hidden": False,
            "color": None,
            "category": None,
            "tags": ["other455_EUR1_TOP2500_1step"],
            "classifications": [
                {"id": "DATA_USAGE:SINGLE_DATA_SET", "name": "Single Data Set Alpha"}
            ],
            "grade": None,
            "stage": "IS",
            "status": "UNSUBMITTED",
            "is": {
                "pnl": 1741112,
                "bookSize": 20000000,
                "longCount": 68,
                "shortCount": 97,
                "turnover": 0.1367,
                "returns": 0.017,
                "drawdown": 0.0289,
                "margin": 0.000249,
                "sharpe": 1.03,
                "fitness": 0.36,
                "startDate": "2013-01-20",
                "investabilityConstrained": {
                    "pnl": 2735422,
                    "bookSize": 20000000,
                    "longCount": 273,
                    "shortCount": 296,
                    "turnover": 0.2028,
                    "returns": 0.0266,
                    "drawdown": 0.1276,
                    "margin": 0.000262,
                    "fitness": 0.12,
                    "sharpe": 0.34,
                },
                "riskNeutralized": {
                    "pnl": 828669,
                    "bookSize": 20000000,
                    "longCount": 68,
                    "shortCount": 97,
                    "turnover": 0.1367,
                    "returns": 0.0081,
                    "drawdown": 0.0257,
                    "margin": 0.000118,
                    "fitness": 0.15,
                    "sharpe": 0.63,
                },
                "checks": [
                    {
                        "name": "LOW_SHARPE",
                        "result": "WARNING",
                        "limit": 1.58,
                        "value": 1.03,
                    },
                    {
                        "name": "LOW_FITNESS",
                        "result": "WARNING",
                        "limit": 1.0,
                        "value": 0.36,
                    },
                    {
                        "name": "LOW_TURNOVER",
                        "result": "PASS",
                        "limit": 0.01,
                        "value": 0.1367,
                    },
                    {
                        "name": "HIGH_TURNOVER",
                        "result": "PASS",
                        "limit": 0.7,
                        "value": 0.1367,
                    },
                    {"name": "CONCENTRATED_WEIGHT", "result": "WARNING"},
                    {
                        "name": "LOW_SUB_UNIVERSE_SHARPE",
                        "result": "PASS",
                        "limit": 0.54,
                        "value": 1.4,
                    },
                    {"name": "SELF_CORRELATION", "result": "PENDING"},
                    {"name": "DATA_DIVERSITY", "result": "PENDING"},
                    {"name": "PROD_CORRELATION", "result": "PENDING"},
                    {"name": "REGULAR_SUBMISSION", "result": "PENDING"},
                    {
                        "name": "LOW_2Y_SHARPE",
                        "result": "PASS",
                        "value": 2.11,
                        "limit": 1.58,
                    },
                    {
                        "result": "PASS",
                        "name": "MATCHES_PYRAMID",
                        "effective": 1,
                        "multiplier": 1.7,
                        "pyramids": [{"name": "EUR/D1/OTHER", "multiplier": 1.7}],
                    },
                    {
                        "result": "WARNING",
                        "name": "MATCHES_THEMES",
                        "themes": [
                            {
                                "id": "M4ZY3YD",
                                "multiplier": 2.0,
                                "name": "GLB high turnover Theme",
                            }
                        ],
                    },
                    {"name": "POWER_POOL_CORRELATION", "result": "PENDING"},
                ],
            },
            "os": None,
            "train": None,
            "test": None,
            "prod": None,
            "competitions": None,
            "themes": None,
            "pyramids": None,
            "pyramidThemes": None,
            "team": None,
        }
        self.superalpha_record = {
            "id": "xWVr3rW",
            "type": "SUPER",
            "author": "ZH87224",
            "settings": {
                "instrumentType": "EQUITY",
                "region": "USA",
                "universe": "TOP3000",
                "delay": 1,
                "decay": 3,
                "neutralization": "SUBINDUSTRY",
                "truncation": 0.08,
                "pasteurization": "ON",
                "unitHandling": "VERIFY",
                "nanHandling": "ON",
                "selectionHandling": "POSITIVE",
                "selectionLimit": 100,
                "maxTrade": "OFF",
                "language": "FASTEXPR",
                "visualization": False,
                "startDate": "2013-01-20",
                "endDate": "2023-01-20",
                "componentActivation": "IS",
                "testPeriod": "P1Y",
            },
            "combo": {
                "code": "combo_a(alpha)",
                "description": None,
                "operatorCount": None,
            },
            "selection": {
                "code": '(prod_correlation<0.1 && universe=="TOP3000" && turnover>0.1)',
                "description": None,
                "operatorCount": None,
            },
            "dateCreated": "2025-07-11T10:16:28-04:00",
            "dateSubmitted": None,
            "dateModified": "2025-07-11T10:16:29-04:00",
            "name": None,
            "favorite": False,
            "hidden": False,
            "color": None,
            "category": None,
            "tags": [],
            "classifications": [],
            "grade": None,
            "stage": "IS",
            "status": "UNSUBMITTED",
            "is": {
                "pnl": 8204967,
                "bookSize": 20000000,
                "longCount": 1602,
                "shortCount": 1462,
                "turnover": 0.1466,
                "returns": 0.2085,
                "drawdown": 0.0123,
                "margin": 0.002843,
                "sharpe": 5.92,
                "fitness": 7.06,
                "startDate": "2013-01-20",
                "investabilityConstrained": {
                    "pnl": 6669229,
                    "bookSize": 20000000,
                    "longCount": 1584,
                    "shortCount": 1549,
                    "turnover": 0.1287,
                    "returns": 0.1694,
                    "drawdown": 0.017,
                    "margin": 0.002633,
                    "fitness": 5.82,
                    "sharpe": 5.07,
                },
                "riskNeutralized": {
                    "pnl": 5369206,
                    "bookSize": 20000000,
                    "longCount": 1602,
                    "shortCount": 1462,
                    "turnover": 0.1466,
                    "returns": 0.1364,
                    "drawdown": 0.0122,
                    "margin": 0.001861,
                    "fitness": 5.77,
                    "sharpe": 5.98,
                },
                "checks": [
                    {
                        "name": "LOW_SHARPE",
                        "result": "PASS",
                        "limit": 1.58,
                        "value": 5.92,
                    },
                    {
                        "name": "LOW_FITNESS",
                        "result": "PASS",
                        "limit": 1.0,
                        "value": 7.06,
                    },
                    {
                        "name": "LOW_TURNOVER",
                        "result": "PASS",
                        "limit": 0.02,
                        "value": 0.1466,
                    },
                    {
                        "name": "HIGH_TURNOVER",
                        "result": "PASS",
                        "limit": 0.4,
                        "value": 0.1466,
                    },
                    {"name": "CONCENTRATED_WEIGHT", "result": "PASS"},
                    {
                        "name": "LOW_SUB_UNIVERSE_SHARPE",
                        "result": "PASS",
                        "limit": 2.56,
                        "value": 4.22,
                    },
                    {"name": "SELF_CORRELATION", "result": "PENDING"},
                    {"name": "PROD_CORRELATION", "result": "PENDING"},
                    {"name": "SUPER_SUBMISSION", "result": "PENDING"},
                    {
                        "name": "IS_LADDER_SHARPE",
                        "result": "PASS",
                        "year": 2,
                        "startDate": "2023-01-20",
                        "endDate": "2021-01-21",
                        "limit": 2.02,
                        "value": 6.6,
                    },
                ],
            },
            "os": None,
            "train": {
                "pnl": 5905773,
                "bookSize": 20000000,
                "longCount": 1604,
                "shortCount": 1450,
                "turnover": 0.1468,
                "returns": 0.2014,
                "drawdown": 0.0123,
                "margin": 0.002744,
                "fitness": 6.82,
                "sharpe": 5.82,
                "startDate": "2013-01-20",
                "investabilityConstrained": {
                    "pnl": 4565983,
                    "bookSize": 20000000,
                    "longCount": 1578,
                    "shortCount": 1546,
                    "turnover": 0.1283,
                    "returns": 0.1557,
                    "drawdown": 0.017,
                    "margin": 0.002427,
                    "fitness": 5.32,
                    "sharpe": 4.83,
                },
                "riskNeutralized": {
                    "pnl": 4281643,
                    "bookSize": 20000000,
                    "longCount": 1604,
                    "shortCount": 1450,
                    "turnover": 0.1468,
                    "returns": 0.146,
                    "drawdown": 0.0071,
                    "margin": 0.001989,
                    "fitness": 6.25,
                    "sharpe": 6.27,
                },
            },
            "test": {
                "pnl": 2291000,
                "bookSize": 20000000,
                "longCount": 1594,
                "shortCount": 1496,
                "turnover": 0.146,
                "returns": 0.2273,
                "drawdown": 0.0088,
                "margin": 0.003113,
                "fitness": 7.69,
                "sharpe": 6.16,
                "startDate": "2022-01-20",
                "investabilityConstrained": {
                    "pnl": 2093311,
                    "bookSize": 20000000,
                    "longCount": 1599,
                    "shortCount": 1559,
                    "turnover": 0.1298,
                    "returns": 0.2077,
                    "drawdown": 0.0105,
                    "margin": 0.0032,
                    "fitness": 7.2,
                    "sharpe": 5.69,
                },
                "riskNeutralized": {
                    "pnl": 1087098,
                    "bookSize": 20000000,
                    "longCount": 1594,
                    "shortCount": 1496,
                    "turnover": 0.146,
                    "returns": 0.1078,
                    "drawdown": 0.0122,
                    "margin": 0.001477,
                    "fitness": 4.37,
                    "sharpe": 5.09,
                },
            },
            "prod": None,
            "competitions": None,
            "themes": None,
            "pyramids": None,
            "pyramidThemes": None,
            "team": None,
        }

    def test_user(self) -> None:
        user = User(
            id="XX2345",
            username="ashswing",
            password="ashswing",
            token_expiry=14400.0,
        )
        self.assertIsNone(self.db.get_user(username="ashswing"))

        user_get = self.db.add_user(user)
        self.assertEqual(user_get.id, "XX2345")

    def test_alpha(self) -> None:
        alpha = Alpha.build(self.alpha_record)
        _ = self.db.add_or_get_alpha(alpha)
        alpha_get = self.db.get_alpha(alpha.id)
        self.assertIsNotNone(alpha_get)
        self.assertEqual(getattr(alpha_get, "id"), alpha.id)

    def test_superalpha(self) -> None:
        alpha = SuperAlpha.build(self.superalpha_record)
        _ = self.db.add_or_get_superalpha(alpha)
        alpha_get = self.db.get_superalpha(alpha.id)
        self.assertIsNotNone(alpha_get)
        self.assertEqual(getattr(alpha_get, "id"), alpha.id)
