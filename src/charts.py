import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import seaborn as sns
import plotly.express as px
from PyQt5.QtWebEngineWidgets import QWebEngineView
import hashlib

# Centralized chart configuration (colors, sizes, etc.)
CHART_CONFIG = {
    "bar_color": "#2196F3",
    "line_color": "#4CAF50",
    "figure_size": (8, 5),
    "dpi": 100,
}

_cache = {}


def get_cache_key(df, chart_type, x, y, **extra):
    """Generate a unique hash key from DataFrame contents + chart config."""
    h = hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()
    extra_str = "_".join(f"{k}={v}" for k, v in sorted(extra.items()))
    return f'{h}_{chart_type}_{x}_{y}_{extra_str}'


def get_cached_chart(key):
    """Return cached chart if it exists, else None."""
    return _cache.get(key)


def set_cached_chart(key, fig):
    """Store a rendered chart in the cache."""
    _cache[key] = fig


def clear_cache():
    """Clear all cached charts."""
    _cache.clear()


def cache_size():
    """Return number of cached charts."""
    return len(_cache)


class ChartCanvas(FigureCanvasQTAgg):
    """A matplotlib canvas embedded in PyQt5 that renders and caches charts."""

    def __init__(self, width=None, height=None, dpi=None):
        """Initialize the figure/axes using CHART_CONFIG defaults unless overridden."""
        fig_width, fig_height = CHART_CONFIG["figure_size"]
        width = width or fig_width
        height = height or fig_height
        dpi = dpi or CHART_CONFIG["dpi"]

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self._last_key = None

    def _setup_axes(self, title="", xlabel="", ylabel=""):
        """Clear axes and apply standard labels."""
        self.ax.clear()
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

    def _render_if_needed(self, df, chart_type, key_x, key_y, plot_func):
        """
        Shared render pipeline: validates df, checks cache key, calls
        plot_func(df) if the chart needs redrawing, then redraws canvas.
        """
        if df.empty:
            raise ValueError(f"Cannot render {chart_type} chart: DataFrame is empty")

        key = get_cache_key(df, chart_type, key_x, key_y)
        if key == self._last_key:
            return

        plot_func(df)
        self.draw()
        self._last_key = key

    def plot_bar(self, df, x, y):
        """Render a bar chart of df[y] grouped by df[x]."""
        def _draw(d):
            self._setup_axes(title=f"{y} by {x}", xlabel=x, ylabel=y)
            self.ax.bar(d[x], d[y], color=CHART_CONFIG["bar_color"])

        self._render_if_needed(df, "bar_canvas", x, y, _draw)

    def plot_line(self, df, x, y):
        """Render a line chart of df[y] over df[x]."""
        def _draw(d):
            self._setup_axes(title=f"{y} over {x}", xlabel=x, ylabel=y)
            self.ax.plot(d[x], d[y], color=CHART_CONFIG["line_color"])

        self._render_if_needed(df, "line_canvas", x, y, _draw)

    def plot_histogram(self, df, col):
        """Render a histogram with KDE overlay for df[col]."""
        def _draw(d):
            self._setup_axes(title=f"Distribution of {col}", xlabel=col, ylabel="Count")
            sns.histplot(d[col], ax=self.ax, kde=True)

        self._render_if_needed(df, "hist_canvas", col, "", _draw)

    def plot_boxplot(self, df, col):
        """Render a boxplot for df[col]."""
        def _draw(d):
            self._setup_axes(title=f"Boxplot of {col}", ylabel=col)
            sns.boxplot(data=d, y=col, ax=self.ax)

        self._render_if_needed(df, "box_canvas", col, "", _draw)


def render_plotly(fig):
    """Convert any Plotly figure to an HTML string for embedding."""
    return fig.to_html(include_plotlyjs="cdn")


def _get_or_render_plotly(df, chart_type, fig_factory, **kwargs):
    """
    Shared caching pipeline for Plotly charts: validates df, checks cache,
    builds the figure via fig_factory if needed, renders to HTML, and caches it.
    """
    if df.empty:
        raise ValueError(f"Cannot generate {chart_type} chart: DataFrame is empty")

    key = get_cache_key(df, chart_type, **kwargs)
    cached = get_cached_chart(key)
    if cached is not None:
        return cached

    fig = fig_factory(df)
    html = render_plotly(fig)
    set_cached_chart(key, html)
    return html


def make_plotly_bar(df, x, y, title=""):
    """Generate a cached Plotly bar chart HTML string."""
    return _get_or_render_plotly(
        df, "bar",
        lambda d: px.bar(d, x=x, y=y, title=title),
        x=x, y=y, title=title
    )


def make_plotly_line(df, x, y, title=""):
    """Generate a cached Plotly line chart HTML string."""
    return _get_or_render_plotly(
        df, "line",
        lambda d: px.line(d, x=x, y=y, title=title),
        x=x, y=y, title=title
    )


def make_plotly_scatter(df, x, y, color=None):
    """Generate a cached Plotly scatter chart HTML string."""
    return _get_or_render_plotly(
        df, "scatter",
        lambda d: px.scatter(d, x=x, y=y, color=color),
        x=x, y=y, color=color
    )
