import pathlib
import pandas as pd
import numpy as np
from traitlets import List, Integer, Unicode, Float, Int, Dict, Bool
from typing import List as TList, Dict as TDict, Optional
from dtaidistance import dtw
from sklearn.preprocessing import normalize

from .base import ViaWidget


class GroupingConstraintsWidget(ViaWidget):
    _esm = pathlib.Path(__file__).parent / "JS" / "GroupingConstraintsWidget.js"
    _css = pathlib.Path(__file__).parent / "CSS" / "GroupingConstraintsWidget.css"
    df_indices = List(Integer(), default_value=[]).tag(sync=True)
    must_link_constraints = List(List(Integer()), default_value=[]).tag(sync=True)
    cannot_link_constraints = List(List(Integer()), default_value=[]).tag(sync=True)
    text_labels = List(Unicode(), default_value=[]).tag(sync=True)

    def __init__(
        self,
        df: pd.DataFrame,
        partition_columns,
        n=10,
        text_label_column=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.df = df
        self.partition_columns = partition_columns
        self.df_indices = [
            int(idx) for idx in np.random.choice(df.index, size=n, replace=False)
        ]
        if text_label_column and text_label_column in df.columns:
            self.text_labels = list(df.loc[self.df_indices, text_label_column])
        self.observe(
            self._set_eligible_partition_columns,
            names=["must_link_constraints", "cannot_link_constraints"],
        )
        self.eligible_partition_columns = partition_columns

    def _set_eligible_partition_columns(self, change=None):
        result_columns = self.partition_columns
        filtered_df = self.df.loc[self.df_indices][result_columns]

        for must_link_constraint in self.must_link_constraints:
            columns_with_same_value = (
                filtered_df.loc[must_link_constraint].nunique() == 1
            )
            result_columns = columns_with_same_value[
                columns_with_same_value
            ].index.tolist()
            if len(result_columns) == 0:
                self.eligible_partition_columns = []
                return
            filtered_df = filtered_df[result_columns]

        for cannot_link_constraint in self.cannot_link_constraints:
            columns_with_different_value = (
                filtered_df.loc[cannot_link_constraint].nunique() == 2
            )
            result_columns = columns_with_different_value[
                columns_with_different_value
            ].index.tolist()
            if len(result_columns) == 0:
                self.eligible_partition_columns = []
                return
            filtered_df = filtered_df[result_columns]

        self.eligible_partition_columns = result_columns


class HistogramRangeFilter(ViaWidget):
    _esm = pathlib.Path(__file__).parent / "JS" / "HistogramRangeFilter.js"
    # _css = pathlib.Path(__file__).parent / "CSS" / "HistogramRangeFilterWidget.css"

    counts = List(Float(), default_value=[]).tag(sync=True)
    bin_edges = List(Float(), default_value=[]).tag(sync=True)
    selected_range = List(Float(), default_value=[]).tag(sync=True)
    width = Int().tag(sync=True)
    height = Int().tag(sync=True)
    bar_color = Unicode("darkslateblue").tag(sync=True)
    slider_color = Unicode("darkslateblue").tag(sync=True)
    y_axis_visible = Bool(False).tag(sync=True)

    def __init__(
        self,
        input_array,
        num_bins: int = 10,
        width: int = 800,
        height: int = 225,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if isinstance(input_array, list):
            self._input_array_instance_type = "list"
            self.input_array = np.asarray(input_array)
        elif isinstance(input_array, np.ndarray):
            self._input_array_instance_type = "ndarray"
            self.input_array = input_array
        else:
            raise TypeError("input_array must be a list or numpy ndarray.")
        self.filtered_array = self.input_array
        counts, bin_edges = np.histogram(input_array, bins=num_bins)
        self.counts = counts.tolist()
        self.bin_edges = bin_edges.tolist()
        self.selected_range = [float(bin_edges[0]), float(bin_edges[-1])]
        self.width = width
        self.height = height

        self.observe(self._set_filtered_array, names="selected_range")

    def _set_filtered_array(self, change):
        """Optional helper to get filtered bins based on selected range."""
        if self._input_array_instance_type == "list":
            self.filtered_array = self.input_array[
                (self.input_array >= self.selected_range[0])
                & (self.input_array <= self.selected_range[1])
            ].tolist()
        elif self._input_array_instance_type == "ndarray":
            self.filtered_array = self.input_array[
                (self.input_array >= self.selected_range[0])
                & (self.input_array <= self.selected_range[1])
            ]


class ScatterplotSelector(ViaWidget):
    _esm = pathlib.Path(__file__).parent / "JS" / "ScatterplotSelector.js"

    datasets = List(trait=Dict(), default_value=[]).tag(sync=True)
    x_cols = List(Unicode(), default_value=[]).tag(sync=True)
    y_cols = List(Unicode(), default_value=[]).tag(sync=True)
    color_cols = List(Unicode(), default_value=[]).tag(sync=True)
    width = Int(800).tag(sync=True)
    height = Int(600).tag(sync=True)
    columns = Int(3).tag(sync=True)  # Number of scatterplots per row
    selected_index = Int(-1).tag(sync=True)  # -1 means none selected

    def __init__(
        self,
        datasets: TList[TDict[str, TList[float]]],
        x_cols: TList[str],
        y_cols: TList[str],
        color_cols: Optional[TList[str]] = None,
        width: int = 800,
        height: int = 600,
        columns: int = 3,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.datasets = datasets
        self.x_cols = x_cols
        self.y_cols = y_cols
        if color_cols is None:
            color_cols = [""] * len(datasets)
        self.color_cols = color_cols
        self.width = width
        self.height = height
        self.columns = columns


class LinePatternSearcher(ViaWidget):
    _esm = pathlib.Path(__file__).parent / "JS" / "LinePatternSearcher.js"

    top_k = Int(5).tag(sync=True)
    _raw_points = List(Float(), default_value=[]).tag(sync=True)
    _search_query_series = List(Float(), default_value=[]).tag(sync=True)
    top_k_indices = List(Int(), default_value=[]).tag(sync=True)
    top_k_dtw_distances = List(Float(), default_value=[]).tag(sync=True)
    _top_dtw_series = List(default_value=[]).tag(sync=True)
    width = Int(800).tag(sync=True)
    height = Int(350).tag(sync=True)

    def __init__(
        self, width=800, height=350, series_length=128, dataset=None, top_k=10, **kwargs
    ):
        super().__init__(width=width, height=height, **kwargs)
        self.series_length = series_length
        self.top_k = top_k
        self._search_query_series = []

        # Accept a dataset for similarity search
        if dataset is None:
            # fallback if user forgets
            dataset = np.random.rand(100, series_length)
        self.dataset = normalize(dataset, norm="l2", axis=1)

        self.observe(self._process_points, names="_raw_points")

    def _process_points(self, change):
        pts = np.array(change["new"]).reshape(-1, 2)
        if len(pts) < 2:
            self._search_query_series = []
            self.top_k_indices = []
            self.top_k_dtw_distances = []
            self._top_dtw_series = []
            return

        x = pts[:, 0]
        y = pts[:, 1]

        y = self.height - y  # Invert SVG y

        if x.max() > x.min():
            norm_x = (x - x.min()) / (x.max() - x.min())
        else:
            norm_x = np.linspace(0, 1, len(x))

        if y.max() > y.min():
            norm_y = (y - y.min()) / (y.max() - y.min())
        else:
            norm_y = np.zeros_like(y)

        target_x = np.linspace(0, 1, self.series_length)
        interp_y = np.interp(target_x, norm_x, norm_y)
        self._search_query_series = interp_y.tolist()

        self._search_similar(interp_y)

    def _search_similar(self, query):
        query = query / np.linalg.norm(query) if np.linalg.norm(query) > 0 else query
        distances = [dtw.distance_fast(query, s) for s in self.dataset]
        indices = np.argsort(distances)[: self.top_k]
        self.top_k_indices = indices.tolist()
        self.top_k_dtw_distances = [distances[i] for i in indices]
        self._top_dtw_series = self.dataset[indices].tolist()


class ScatterplotCategorizer(ViaWidget):
    _esm = pathlib.Path(__file__).parent / "JS" / "ScatterplotCategorizer.js"

    points = List(List(Float()), default_value=[]).tag(sync=True)
    categories = List(
        Unicode(),
        default_value=[
            "Category_1",
            "Category_2",
            "Category_3",
            "Category_4",
            "Category_5",
        ],
    ).tag(sync=True)
    selected_category = Unicode().tag(sync=True)

    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)
        self.points = points

    def set_category(self, category_name):
        self.selected_category = category_name
        self.save_changes()
