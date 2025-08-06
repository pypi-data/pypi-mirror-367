class SimulationInProgress(Exception):
    def __init__(
        self,
        message: str | None = None,
        simid: str | None = None,
        progress: float | None = None,
    ) -> None:
        super().__init__(message)
        self.simid = simid
        self.progress = progress


class APIError(Exception): ...
