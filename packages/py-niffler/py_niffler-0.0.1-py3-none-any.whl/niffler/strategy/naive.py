from typing import Self

from ..agent import NifflerAgent
from ..model import Simulation, SuperSimulation
from . import Strategy


class NaiveStrategy(Strategy[Simulation]):
    def __init__(
        self,
        agent: NifflerAgent,
        region: str,
        delay: int,
        universe: str,
        name: str | None = None,
        slots: int = 8,
        batch_size: int = 10,
    ) -> None:
        super().__init__(
            agent=agent,
            slots=slots,
            batch_size=batch_size,
            region=region,
            delay=delay,
            name=name,
            universe=universe,
        )

        self._simulations = []

    def register(self, expr: str | list[str]) -> Self:
        if isinstance(expr, str):
            expr = [expr]
        self._simulations += [
            Simulation(
                region=self.region, universe=self.universe, delay=self.delay, expr=e
            )
            for e in expr
        ]
        return self

    def _produce(self) -> Simulation | None:
        if len(self._simulations) > 0:
            return self._simulations.pop()
        return

    def _feedback(
        self,
        sim_result: list[Simulation] | Simulation | None,
        context: dict | None = None,
    ) -> None:
        self._logger.info(f"FeedBack Report: {sim_result}")
        return


class NaiveSuperStrategy(Strategy[SuperSimulation]):
    def __init__(
        self,
        agent: NifflerAgent,
        region: str,
        delay: int,
        universe: str,
        name: str | None = None,
        slots: int = 3,
        batch_size: int = 1,
    ) -> None:
        super().__init__(
            agent=agent,
            slots=slots,
            batch_size=batch_size,
            region=region,
            delay=delay,
            name=name,
            universe=universe,
        )
