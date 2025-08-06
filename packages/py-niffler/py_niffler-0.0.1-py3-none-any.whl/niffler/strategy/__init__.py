import asyncio
import logging
from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar, get_args, get_origin, overload

from ..agent import NifflerAgent
from ..model import Alpha, Simulation, SuperAlpha, SuperSimulation

T = TypeVar("T", bound=Simulation | SuperSimulation)


class Strategy(Generic[T], metaclass=ABCMeta):
    """因子策略模版

    Configs
    -------
    SLOTS : 同时执行的任务数
    BATCH_SIZE : 批大小
    """

    SLOTS = 8
    BATCH_SIZE = 10

    SUPER_SLOTS = 3
    SUPER_BATCH_SIZE = 1

    def __init__(
        self,
        agent: NifflerAgent,
        slots: int,
        batch_size: int,
        region: str,
        delay: int,
        universe: str,
        name: str | None,
    ) -> None:
        self._logger = logging.getLogger(__name__)
        self.slots = slots
        self.batch_size = batch_size
        self.agent = agent
        self.region = region
        self.delay = delay
        self.universe = universe
        self.name = name

        self.prior_queue = asyncio.Queue()

        self._check(slots, batch_size)

    def _get_generic(self) -> Any:
        generic_bases = getattr(self.__class__, "__orig_bases__", ())
        for base in generic_bases:
            origin = get_origin(base)
            if origin is Strategy:  # 找到 Strategy[...] 这一层
                args = get_args(base)
                if args:  # 防止裸 Strategy
                    t_real = args[0]  # 这就是 T 的实参
                    return t_real
                break

    def _check(self, slots: int, batch_size: int) -> None:
        _t = self._get_generic()
        match _t:
            case t if (
                t is SuperSimulation
                and (slots > self.SUPER_SLOTS or batch_size > self.SUPER_BATCH_SIZE)
            ) or (
                t is Simulation and (slots > self.SLOTS or batch_size > self.BATCH_SIZE)
            ):
                # FIXME: 日志bug
                _error_log = (
                    f"{t.__name__} 最大槽位数或批大小超过限制, "
                    f"slots({slots} ≟ {self.SUPER_SLOTS if t is Simulation else self.SLOTS}), "
                    f"batch_size({batch_size} ≟ {self.SUPER_BATCH_SIZE if t is SuperSimulation else self.BATCH_SIZE})"
                )
                self._logger.error(_error_log)
                raise ValueError(_error_log)
            case t if t not in [Simulation, SuperSimulation]:
                raise ValueError(f"未知的类型: {t}")
            case _:
                pass

    @abstractmethod
    def _produce(self) -> T | None:
        """生成一个 Simulation
        可以通过维护一个生成器
        """
        ...

    @overload
    def _feedback(self, sim_result: list[Simulation] | Simulation) -> None: ...
    @overload
    def _feedback(self, sim_result: SuperSimulation) -> None: ...
    @abstractmethod
    def _feedback(
        self, sim_result: list[Simulation] | Simulation | SuperSimulation | None
    ) -> None:
        """Simulation 结果反馈, 可用于插入优先回测结果"""
        ...

    def get_simulation(self) -> list | T | None:
        simlist = []
        # 优先队列
        while len(simlist) < self.batch_size:
            try:
                sim = self.prior_queue.get_nowait()
                if self.agent.is_simulated(sim):
                    sim = self.agent.db.get_simulation(simhash=sim.hashing())[0]  # type: ignore
                    self._feedback(sim)
                    continue
                simlist.append(sim)
            except asyncio.QueueEmpty:
                break
        while len(simlist) < self.batch_size:
            sim = self._produce()
            if sim is None:
                break
            if self.agent.is_simulated(sim):
                sim = self.agent.db.get_simulation(simhash=sim.hashing())[0]  # type:ignore
                self._feedback(sim)
                continue
            simlist.append(sim)

        if len(simlist) == 0:
            return None
        elif len(simlist) == 1:
            return simlist[0]
        else:
            return simlist

    async def _single_task(self) -> None:
        """
        并发单元（无需信号量，由 run 外部控制并发）：
        1. get_simulation
        2. 执行 simulation
        3. 将结果传给 _feedback
        """
        sim = self.get_simulation()
        if sim is None:  # 无任务
            self._logger.warning("无任务")
            raise ValueError("Error")
            return
        sim_result = await self.agent.async_simulate(sim)  # type: ignore
        if sim_result is not None:
            self._feedback(sim_result)

    async def run(self) -> None:
        """
        主入口：
        持续派发任务，直到 get_simulation 再也拿不到任务；
        始终保持最多 `slots` 个并发协程。
        任何异常直接抛出并中断整个策略。
        """
        sem = asyncio.Semaphore(self.slots)

        async def _wrapped() -> None:
            async with sem:
                await self._single_task()

        pending: set[asyncio.Task] = set()

        # 先一次性启动 slots 个 worker
        for _ in range(self.slots):
            task = asyncio.create_task(_wrapped())
            pending.add(task)

        # 每完成一个就检查是否异常，并再补一个
        task_idx = 1
        try:
            while pending:
                done, pending = await asyncio.wait(
                    pending, return_when=asyncio.FIRST_COMPLETED
                )
                self._logger.info(f"Task Done:  {task_idx}")
                task_idx += 1

                # 有异常直接抛出
                for t in done:
                    exc = t.exception()
                    if exc:
                        self._logger.exception(f"single_task 异常: {exc}")

                # 只要还能拿到任务就继续补
                sim = self.get_simulation()
                if sim is None:
                    break

                # 把任务放回队列后，再补一个 worker
                if isinstance(sim, list):
                    for s in sim:
                        await self.prior_queue.put(s)
                else:
                    await self.prior_queue.put(sim)

                task = asyncio.create_task(_wrapped())
                pending.add(task)
        except asyncio.CancelledError:
            self._logger.warning(f"WarmStop: 剩余 {len(pending)} 任务执行中")
        finally:
            # 等待剩余任务全部结束
            await asyncio.gather(*pending)
