REGIONS: dict[str, list[str]] = {
    "USA": ["TOP3000", "TOP1000", "TOP500", "TOP200", "ILLIQUID_MINVOL1M", "TOPSP500"],
    "GLB": ["TOP3000", "MINVOL1M", "TOPDIV3000"],
    "EUR": ["TOP2500", "TOP1200", "TOP800", "TOP400", "ILLIQUID_MINVOL1M"],
    "ASI": ["MINVOL1M", "ILLIQUID_MINVOL1M"],
    "CHN": ["TOP2000U"],
}
ALPHA_CATEGORIES: list[str] = [
    "PRICE_REVERSION",
    "PRICE_MOMENTUM",
    "VOLUME",
    "FUNDAMENTAL",
    "ANALYST",
    "PRICE_VOLUME",
    "RELATION",
    "SENTIMENT",
]
ALPHA_STATUS: list[str] = ["ACTIVE", "UNSUBMITTED", "DECOMMISSIONED"]
ALPHA_LANGUAGE: list[str] = ["FASTEXPR", "EXPR", "PYTHON"]
ALPHA_INSTRUMENT: list[str] = ["CRYPTO", "EQUITY"]

START_DATE = "2013-01-20"
END_DATE = "2023-01-20"

POWER_POOL_ALPHA_DESCRIPTION_PLACEHOLDER = (
    "Idea: This alpha aims to identify stocks that have recently experienced "
    "significant [factor] relative to [reference point]. "
    "By focusing on standardized, outlier-adjusted [factor] over a short-term horizon, "
    "the alpha seeks to capture [market behavior], which may indicate [fundamental/expectation changes].\n"
    "Rationale for data used: -\n"
    "Rationale for operators used: -"
)
