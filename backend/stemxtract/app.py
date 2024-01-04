from stemxtract.state.local import LocalStateManager

from starlette.applications import Starlette


class StemXtract(Starlette):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.manager = LocalStateManager()
