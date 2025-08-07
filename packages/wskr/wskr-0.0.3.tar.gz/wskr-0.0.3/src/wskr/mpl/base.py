import os
import sys
from io import BytesIO
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import _api, interactive, is_interactive  # noqa: PLC2701
from matplotlib._pylab_helpers import Gcf  # noqa: PLC2701
from matplotlib.backend_bases import FigureManagerBase, _Backend  # noqa: PLC2701
from matplotlib.backends.backend_agg import FigureCanvasAgg

from wskr.mpl.utils import autosize_figure, detect_dark_mode
from wskr.tty.base import ImageTransport
from wskr.tty.registry import get_image_transport

if sys.flags.interactive:
    interactive(b=True)

if detect_dark_mode():
    plt.style.use("dark_background")


def render_figure_to_terminal(canvas: FigureCanvasAgg, transport: ImageTransport) -> None:
    """Resize and render a Matplotlib figure to the terminal using a given transport."""
    width_px, height_px = transport.get_window_size_px()
    try:
        scale = float(os.getenv("WSKR_SCALE", "1.0"))
    except ValueError:
        scale = 1.0
    width_px = int(width_px * scale)
    height_px = int(height_px * scale)

    autosize_figure(canvas.figure, width_px, height_px)

    buf = BytesIO()
    canvas.print_png(buf)
    buf.seek(0)
    transport.send_image(buf.read())


class WskrFigureManager(FigureManagerBase):
    def __init__(
        self,
        canvas: FigureCanvasAgg,
        num: int = 1,
        transport: ImageTransport | None = None,
    ) -> None:
        super().__init__(canvas, num)
        self.transport = transport or get_image_transport()

    def show(self, *_args: Any, **_kwargs: Any) -> None:
        render_figure_to_terminal(self.canvas, self.transport)


class WskrFigureCanvas(FigureCanvasAgg):
    manager_class: Any = _api.classproperty(lambda _: WskrFigureManager)

    def draw(self) -> None:
        # Prevent recursive draws triggered by Matplotlib's stale callbacks
        if getattr(self, "_in_draw", False):
            return
        self._in_draw = True
        try:
            super().draw()
            if is_interactive() and self.figure.get_axes():
                self.manager.show()
        finally:
            self._in_draw = False

    draw_idle = draw


class BaseFigureManager(FigureManagerBase):
    """Minimal backend manager parameterized by transport class."""

    def __init__(
        self,
        canvas: FigureCanvasAgg,
        num: int,
        transport_cls: type[ImageTransport],
    ) -> None:
        super().__init__(canvas, num)
        self.transport = transport_cls()

    def show(self, *_args: Any, **_kwargs: Any) -> None:
        render_figure_to_terminal(self.canvas, self.transport)


class TerminalBackend(_Backend):
    """Generic Matplotlib backend for terminal-image protocols."""

    not_impl_msg: str | None = None

    @classmethod
    def draw_if_interactive(cls):
        manager = Gcf.get_active()
        if mpl.is_interactive() and manager and manager.canvas.figure.get_axes():
            cls.show()

    @classmethod
    def show(cls, *args: Any, **kwargs: Any) -> None:
        if cls.not_impl_msg is not None:
            raise NotImplementedError(cls.not_impl_msg)
        manager = Gcf.get_active()
        if manager:
            manager.show(*args, **kwargs)
            Gcf.destroy_all()


FigureCanvas = WskrFigureCanvas
FigureManager = WskrFigureManager


@_Backend.export
class _BackendTermAgg(TerminalBackend):
    FigureCanvas = WskrFigureCanvas
    FigureManager = WskrFigureManager
