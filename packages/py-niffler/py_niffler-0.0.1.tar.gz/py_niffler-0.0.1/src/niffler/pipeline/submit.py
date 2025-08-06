"""因子提交 Pipeline

检索可提交的因子.
"""

import time
from datetime import datetime
from typing import Callable, Literal

from ..agent import NifflerAgent
from ..model import Alpha, SuperAlpha
from ..utils import calc_pnl_corr
from . import Pipeline


class SubmitPipeline(Pipeline[Callable[[Alpha | SuperAlpha], bool]]):
    """提交检查"""

    PPA_SHARPE = 1.0
    PPA_CORR = 0.5

    SHARPE_D1 = 1.58
    SHARPE_D0 = 2.69
    FITNESS_D1 = 1.0
    FITNESS_D0 = 1.5

    CORR = 0.7

    SHARPE_D1_CN = 2.08
    SHARPE_D0_CN = 3.5

    def __init__(
        self,
        agent: NifflerAgent,
        alpha_type: Literal["SUPER", "REGULAR"],
        region: str,
        delay: Literal[0, 1],
        sharpe: float = 1.0,
        fitness: float = 0.5,
        date_from: datetime | str | None = None,
        topn: int = 10,
    ) -> None:
        super().__init__(agent)
        self.alpha_type = alpha_type.upper()
        self.region = region
        self.delay = delay
        self.sharpe = sharpe
        self.fitness = fitness
        self.date_from = date_from
        self.topn = topn

    def run(self) -> list[Alpha | SuperAlpha]:
        active_alphas = (
            self.agent.get_alphaset(status="ACTIVE", date_split=180, region=self.region)
            or []
        )
        self._logger.info(f"已加载 {len(active_alphas)} Active Alphas")
        active_ppas = list(
            filter(lambda x: bool(getattr(x, "ppa_available")), active_alphas)
        )
        if len(active_ppas) > 0:
            self._logger.info(f"已加载 {len(active_ppas)} Active PowerPoolAlphas")

        candidate_alphas = (
            self.agent.get_alphaset(
                status="UNSUBMITTED",
                date_split=1,
                region=self.region,
                delay=self.delay,
                date_from=self.date_from,
                sharpe=self.sharpe,
                fitness=self.fitness,
            )
            or []
        )
        checkable_alphas = list(filter(lambda x: x.checkable, candidate_alphas))
        self._logger.info(f"备选 Alpha 有 {len(checkable_alphas)} 个")

        for node in self.node:
            checkable_alphas = list(filter(lambda x: node(x), checkable_alphas))
            self._logger.info(
                f"{node.__name__} 过滤后备选 Alpha 剩余 {len(checkable_alphas)} 个"
            )

        pnls_active = [self.agent.get_pnl(a.id) for a in active_alphas]
        pnls_active = [p for p in pnls_active if p is not None]

        pnls_ppa = [self.agent.get_pnl(a.id) for a in active_ppas]
        pnls_ppa = [p for p in pnls_ppa if p is not None]

        submittable_alphas = []
        for idx, alpha in enumerate(
            sorted(checkable_alphas, key=lambda x: x.is_sharpe, reverse=True)
        ):
            if len(submittable_alphas) >= self.topn:
                break
            pnl = self.agent.get_pnl(alpha.id)
            if pnl is None:
                self._logger.error(f"获取 PNL({alpha.id}) 失败")
                continue
            self_corr = calc_pnl_corr(
                target=pnl,
                others=pnls_ppa if alpha.ppa_available else pnls_active,
            )

            if alpha.ppa_available:
                # 满足 PPA
                if self_corr < self.PPA_CORR:
                    submittable_alphas.append(alpha)
                    self._logger.info(
                        f"[{idx + 1}/{len(checkable_alphas)}] PPA({self_corr:.4f}): "
                        f"https://platform.worldquantbrain.com/alpha/{alpha.id}"
                    )
                else:
                    self._logger.info(
                        f"[{idx + 1}/{len(checkable_alphas)}] PPA({alpha.id}) "
                        f"Self-Corr {self_corr:.3f} 不符合条件"
                    )
            elif self_corr < self.CORR:
                # 满足 RA
                prod = self.agent.check_prod(alpha.id)
                if prod is None:
                    self._logger.warning(
                        f"获取 Prod-Corr 失败 Alpha({alpha.id}) 已跳过, "
                        f"休眠 {10 * self.agent.retry_delay} 秒"
                    )
                    time.sleep(10 * self.agent.retry_delay)
                    continue
                if prod < self.CORR:
                    submittable_alphas.append(alpha)
                    self._logger.info(
                        f"[{idx + 1}/{len(checkable_alphas)}] {'RA' if isinstance(alpha, Alpha) else 'SA'}({prod:.4f}): "
                        f"https://platform.worldquantbrain.com/alpha/{alpha.id}"
                    )
                else:
                    self._logger.info(
                        f"[{idx + 1}/{len(checkable_alphas)}] {'RA' if isinstance(alpha, Alpha) else 'SA'}({alpha.id}) "
                        f"Prod-Corr {prod:.3f} 不符合条件"
                    )
            else:
                self._logger.info(
                    f"[{idx + 1}/{len(checkable_alphas)}] {'RA' if isinstance(alpha, Alpha) else 'SA'}({alpha.id}) "
                    f"Self-Corr {self_corr:.3f} 不符合条件"
                )

        return submittable_alphas
