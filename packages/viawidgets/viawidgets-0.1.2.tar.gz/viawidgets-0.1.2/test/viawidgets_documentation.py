import marimo

__generated_with = "0.14.12"
app = marimo.App(
    width="columns",
    app_title="viawidgets docs",
    layout_file="layouts/viawidgets_documentation.grid.json",
)


@app.cell(column=0, hide_code=True)
def _(mo):
    mo.md(r"""# `viawidgets`""")
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import random
    from sklearn.datasets import make_blobs, make_moons, make_circles

    from viawidgets.widgets import GroupingConstraintsWidget, HistogramRangeFilter, LinePatternSearcher, ScatterplotSelector
    return (
        GroupingConstraintsWidget,
        HistogramRangeFilter,
        LinePatternSearcher,
        ScatterplotSelector,
        make_blobs,
        make_circles,
        make_moons,
        mo,
        np,
        pd,
        random,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## What are ViaWidgets?

    They are interactive widgets (based on [anywidget](https://anywidget.dev/)) centered around two core concepts:

    - **via**: You go "**via**" them, *i.e.*, input data (+interactions) → ViaWidget → output data.
    - **VIA**: They use **V**isualization for **I**nteraction **A**ugmentation.

    ---

    A simple example is the following `HistogramRangeFilter`:

    - **via**: It is used to filter an input array based on a selected range. The filtered array can be used in subsequent notebook cells.
    - **VIA**: The range slider is augmented by the histogram, allowing interpretation of the underlying distribution for an informed interaction.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo, np):
    # Generate random data with two peaks
    arr1 = np.random.normal(0, 2, size=10000)  # Larger and spread-out peak
    arr2 = np.random.normal(4.5, 0.75, size=3000)  # Thinner and towards the right peak

    # Combine the two datasets
    arr = np.concatenate([arr1, arr2])


    nbins_slider = mo.ui.slider(start=1, stop=50, step=1, value=15, show_value=True)
    mo.vstack(
        [
            mo.md("## Inputs"),
            mo.accordion({"`input_array`": arr, "`num_bins`": nbins_slider}),
        ]
    )
    return arr, nbins_slider


@app.cell(hide_code=True)
def _(HistogramRangeFilter, arr, mo, nbins_slider):
    sample_widget = mo.ui.anywidget(
        HistogramRangeFilter(arr, num_bins=nbins_slider.value)
    )
    mo.vstack([mo.md("## ViaWidget: `HistogramRangeFilter`"), sample_widget])
    return (sample_widget,)


@app.cell(hide_code=True)
def _(mo, sample_widget):
    mo.vstack(
        [
            mo.md("## Outputs:"),
            mo.accordion(
                {
                    "`filtered_array`": sample_widget.filtered_array,
                    "`selected_range`": sample_widget.selected_range,
                }
            ),
        ]
    )
    return


@app.cell(column=1, hide_code=True)
def _(mo, pd):
    def get_widget_description_doc(doc_description_str):
        widget_description_doc = mo.callout(mo.md(doc_description_str))
        return widget_description_doc

    def get_widget_ip_op_list_doc(widget_ip_op_dict, which_list):
        widget_ip_op_df = pd.DataFrame.from_dict(
            widget_ip_op_dict,
            orient="index",
            columns=["Description", "Example values"],
        )

        widget_ip_op_list_md_str = [
            "`" + widget_ip_op + "`" for widget_ip_op in widget_ip_op_df.index
        ]
        widget_ip_op_list_doc = mo.vstack(
            [
                mo.md("## " + which_list + ":"),
                mo.ui.tabs(
                    dict(
                        [
                            (
                                widget_ip_op_df_column,
                                mo.accordion(
                                    dict(
                                        zip(
                                            widget_ip_op_list_md_str,
                                            widget_ip_op_df[
                                                widget_ip_op_df_column
                                            ].to_list(),
                                        )
                                    )
                                ),
                            )
                            for widget_ip_op_df_column in widget_ip_op_df.columns
                        ]
                    )
                ),
            ]
        )
        return widget_ip_op_list_doc

    def get_widget_portion_doc(widget_name, widget):
        return mo.vstack([mo.md("## ViaWidget: `" + widget_name + "`"), widget])

    def get_full_widget_doc(
        widget_name,
        doc_description_str=None,
        widget_inputs_dict=None,
        widget=None,
        widget_outputs_dict=None,
    ):
        return mo.vstack(
            [
                get_widget_description_doc(doc_description_str),
                mo.md("<br>"),
                get_widget_ip_op_list_doc(
                    widget_inputs_dict,
                    which_list="Input"+("s" if len(widget_inputs_dict)>1 else "") 
                ),
                mo.md("<br><br>"),
                get_widget_portion_doc(widget_name, widget),
                mo.md("<br><br>"),
                get_widget_ip_op_list_doc(
                    widget_outputs_dict, 
                    which_list="Output"+("s" if len(widget_outputs_dict)>1 else "") 
                ),
            ]
        )

    return (get_full_widget_doc,)


@app.cell(hide_code=True)
def _(
    GroupingConstraintsWidget_doc_description_str,
    GroupingConstraintsWidget_inputs_dict,
    GroupingConstraintsWidget_outputs_dict,
    GroupingConstraintsWidget_widget,
    HistogramRangeFilter_doc_description_str,
    HistogramRangeFilter_inputs_dict,
    HistogramRangeFilter_outputs_dict,
    HistogramRangeFilter_widget,
    LinePatternSearcher_doc_description_str,
    LinePatternSearcher_inputs_dict,
    LinePatternSearcher_outputs_dict,
    LinePatternSearcher_widget,
    ScatterplotSelector_doc_description_str,
    ScatterplotSelector_inputs_dict,
    ScatterplotSelector_outputs_dict,
    ScatterplotSelector_widget,
    get_full_widget_doc,
):
    doc_widgets_list_tabs = {}

    doc_widgets_list_tabs["`GroupingConstraintsWidget`"] = get_full_widget_doc(
        widget_name="GroupingConstraintsWidget",
        doc_description_str=GroupingConstraintsWidget_doc_description_str,
        widget_inputs_dict=GroupingConstraintsWidget_inputs_dict,
        widget=GroupingConstraintsWidget_widget,
        widget_outputs_dict=GroupingConstraintsWidget_outputs_dict,
    )

    doc_widgets_list_tabs["`HistogramRangeFilter`"] = get_full_widget_doc(
        widget_name="HistogramRangeFilter",
        doc_description_str=HistogramRangeFilter_doc_description_str,
        widget_inputs_dict=HistogramRangeFilter_inputs_dict,
        widget=HistogramRangeFilter_widget,
        widget_outputs_dict=HistogramRangeFilter_outputs_dict,
    )

    doc_widgets_list_tabs["`LinePatternSearcher`"] = get_full_widget_doc(
        widget_name="LinePatternSearcher",
        doc_description_str=LinePatternSearcher_doc_description_str,
        widget_inputs_dict=LinePatternSearcher_inputs_dict,
        widget=LinePatternSearcher_widget,
        widget_outputs_dict=LinePatternSearcher_outputs_dict,
    )

    doc_widgets_list_tabs["`ScatterplotSelector`"] = get_full_widget_doc(
        widget_name="ScatterplotSelector",
        doc_description_str=ScatterplotSelector_doc_description_str,
        widget_inputs_dict=ScatterplotSelector_inputs_dict,
        widget=ScatterplotSelector_widget,
        widget_outputs_dict=ScatterplotSelector_outputs_dict,
    )

    return (doc_widgets_list_tabs,)


@app.cell(hide_code=True)
def _(doc_widgets_list_tabs, mo):
    hr = mo.md("<hr>")

    doc_disclaimer = mo.callout(
        mo.md(
            r"""## ⚠️ Disclaimer ⚠️
    ### This package is in an early development stage and is currently built as a research prototype. Expect

    - Bugs 🐛🐛🐛🐛
    - Frequent changes to widget names, parameters, etc.
    - A lack of proper documentation.
    """
        )
    )

    doc_future_plans = mo.callout(
        mo.md(
            """

    ## Future plans

    - Many, many more ViaWidgets. Also, new kinds of ViaWidgets (e.g., collaborative(web-based) ViaWidgets).
    - Adding/modifying different visualizations to fit different data characteristics/analysis tasks/user personas.
    - Providing some consistency across different ViaWidgets (e.g., common styling options, shared data models)
    - Figuring out a way to combine compatible ViaWidgets dynamically for a bi-directional brushing and linking.
    - Widget suggestions and widget combination templates for certain application scenarios.
    """
        )
    )

    doc_widgets_list = mo.vstack(
        [
            mo.md(
                r"""<br>
            ## Widgets list<br><br>
            ```python
            from viawidgets.widgets import <widget_name>
            ``` 
            <br>
            """
            ),
            mo.ui.tabs(doc_widgets_list_tabs),
        ]
    )

    mo.vstack(
        [
            mo.md(
                """
        --- 
        ## Want to use ViaWidgets?<br>
        """
            ),
            mo.vstack(
                [
                    doc_disclaimer,
                    hr,
                    doc_widgets_list,
                    mo.md("<br><br>"),
                    hr,
                    doc_future_plans,
                ]
            ),
        ]
    )

    return


@app.cell(column=2)
def _():
    GroupingConstraintsWidget_doc_description_str = r"""The same set of data items (e.g., {🟦🟥🔵🔴}) can be grouped in many ways — for example, {{🟦🟥}, {🔵🔴}} or {{🟦🔵}, {🔴🟥}}. But not all groupings make sense — some, like {{🟦🔴}, {🔵🟥}}, might feel wrong.

    The `GroupingConstraintsWidget` helps guide better groupings by letting you set simple rules:

    - **Must-Link**: these items should be in the same group
    - **Cannot-Link**: these items should not be in the same group

    The widget shows a small set of sample items as nodes in a diagram. You can tap to select and connect nodes with either type of link to set your grouping constraints.
    """
    return (GroupingConstraintsWidget_doc_description_str,)


@app.cell(hide_code=True)
def _(pd, random):
    def generate_random_clustering_data():
        # Define possible values for each component of the shape_name
        areas = [str(i) for i in range(1, 5)]
        shapes = ["triangle", "rectangle", "circle"]
        colors = ["red", "blue", "green"]

        # Generate 100 rows of data
        data = []
        for _ in range(100):
            area = random.choice(areas)
            shape = random.choice(shapes)
            color = random.choice(colors)
            shape_name = f"{area}_{shape}_{color}"
            cr4 = f"{shape}_{color}"
            random_group = random.randint(0, 2)  # Randomly assign to group 0, 1, or 2
            data.append([shape_name, int(area), shape, color, cr4, random_group])

        # Create the DataFrame
        df = pd.DataFrame(data, columns=[
            "shape_name",
            "size_based_grouping",
            "shape_based_grouping",
            "color_based_grouping",
            "shape_and_color_based_grouping",
            "random_grouping"
        ])

        text_label_column="shape_name"

        return df, list(set(df.columns) - {text_label_column}), text_label_column

    GroupingConstraintsWidget_df, GroupingConstraintsWidget_partition_columns, GroupingConstraintsWidget_text_label_column = generate_random_clustering_data()

    return (
        GroupingConstraintsWidget_df,
        GroupingConstraintsWidget_partition_columns,
        GroupingConstraintsWidget_text_label_column,
    )


@app.cell(hide_code=True)
def _(
    GroupingConstraintsWidget_df,
    GroupingConstraintsWidget_partition_columns,
    GroupingConstraintsWidget_text_label_column,
):
    GroupingConstraintsWidget_inputs_dict = {
        "df": [
            "Required parameter | [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html).<br>A tabular dataset with data items as rows and different `partition_columns`, `text_label_column` and possibly other data attributes as columns.",
            GroupingConstraintsWidget_df,
        ],
        "partition_columns": [
            "Required parameter | List(string).<br>List of columns which contain different groupings/partitioning of the data items. These can be any categorical attribute columns, with ideally limited number of unique values.",
            GroupingConstraintsWidget_partition_columns,
        ],
        "text_label_column": [
            "Required parameter | string.<br>Text label used to identify what that data item is.", GroupingConstraintsWidget_text_label_column
        ],
    }
    return (GroupingConstraintsWidget_inputs_dict,)


@app.cell
def _(
    GroupingConstraintsWidget,
    GroupingConstraintsWidget_df,
    GroupingConstraintsWidget_partition_columns,
    mo,
):
    GroupingConstraintsWidget_widget = mo.ui.anywidget(GroupingConstraintsWidget(df = GroupingConstraintsWidget_df, partition_columns = GroupingConstraintsWidget_partition_columns, text_label_column="shape_name"))
    return (GroupingConstraintsWidget_widget,)


@app.cell(hide_code=True)
def _(GroupingConstraintsWidget_widget):
    GroupingConstraintsWidget_outputs_dict = {
        "eligible_partition_columns": [
            "Required parameter | List(string).<br>Filtered list of `partition_columns` which satisfy the gtouping constraints.",
            GroupingConstraintsWidget_widget.eligible_partition_columns,
        ],
    }
    return (GroupingConstraintsWidget_outputs_dict,)


@app.cell(column=3)
def _():
    HistogramRangeFilter_doc_description_str = r"""`HistogramRangeFilter` enables interactive filtering of a numerical array/list by selecting a contiguous range along a histogram. The selection operates on discretized intervals and snaps precisely to bin edges, ensuring alignment between the visual representation and the underlying data bins."""
    return (HistogramRangeFilter_doc_description_str,)


@app.cell(hide_code=True)
def _(mo, np):
    HistogramRangeFilter_input_array = np.random.normal(0, 1, size=100)
    HistogramRangeFilter_num_bins_slider = mo.ui.slider(
        start=1, stop=50, step=1, value=10, show_value=True
    )
    return (
        HistogramRangeFilter_input_array,
        HistogramRangeFilter_num_bins_slider,
    )


@app.cell(hide_code=True)
def _(HistogramRangeFilter_input_array, HistogramRangeFilter_num_bins_slider):
    HistogramRangeFilter_inputs_dict = {
        "input_array": [
            "Required parameter | One-dimensional [`numpy.array`](https://numpy.org/doc/stable/reference/generated/numpy.array.html) or a `list` of numbers.<br>The array to be filtered.",
            HistogramRangeFilter_input_array,
        ],
        "num_bins": [
            "Optional parameter | Default: `10` | `Integer`.<br>The number of bins used to compute the [`numpy.histogram`](https://numpy.org/doc/stable/reference/generated/numpy.histogram.html).",
            HistogramRangeFilter_num_bins_slider,
        ],
    }
    return (HistogramRangeFilter_inputs_dict,)


@app.cell
def _(HistogramRangeFilter, HistogramRangeFilter_num_bins_slider, arr, mo):
    HistogramRangeFilter_widget = mo.ui.anywidget(
        HistogramRangeFilter(arr, num_bins=HistogramRangeFilter_num_bins_slider.value)
    )
    return (HistogramRangeFilter_widget,)


@app.cell(hide_code=True)
def _(HistogramRangeFilter_widget):
    HistogramRangeFilter_outputs_dict = {
        "filtered_array": [
            "One-dimensional [`numpy.array`](https://numpy.org/doc/stable/reference/generated/numpy.array.html) or a `list` of numbers depending on `type(input_array)`.<br>The array obtained after applying filtering.",
            HistogramRangeFilter_widget.filtered_array,
        ],
        "selected_range": [
            "A `list` of two numbers.<br>It is the range selected in the widget. Due to snapping, the range is based on the bin edges computed by [`numpy.histogram`](https://numpy.org/doc/stable/reference/generated/numpy.histogram.html).",
            HistogramRangeFilter_widget.selected_range,
        ],
    }
    return (HistogramRangeFilter_outputs_dict,)


@app.cell(column=4)
def _():
    LinePatternSearcher_doc_description_str = r"""The `LinePatternSearcher` lets users draw a line and find series with a similar line pattern within a collection of series. It works even when the patterns are stretched, shifted, or vary slightly in scale. Due to technical reasons, it allows drawing only from left to right."""
    return (LinePatternSearcher_doc_description_str,)


@app.cell(hide_code=True)
def _(mo, np):
    # Generate sample time series
    def generate_random_walk(length=128, scale=0.5):
        steps = np.random.normal(loc=0, scale=scale, size=length)
        series = np.cumsum(steps)
        series = (series - series.min()) / (
            series.max() - series.min()
        )  # normalize 0-1
        return series

    LinePatternSearcher_dataset = np.array(
        [generate_random_walk() for _ in range(20000)]
    )
    LinePatternSearcher_top_k_slider = mo.ui.slider(
        start=1, stop=20, step=1, value=10, show_value=True
    )
    return LinePatternSearcher_dataset, LinePatternSearcher_top_k_slider


@app.cell(hide_code=True)
def _(LinePatternSearcher_dataset, LinePatternSearcher_top_k_slider):
    LinePatternSearcher_inputs_dict = {
        "dataset": [
            "Required parameter | [`numpy.array`](https://numpy.org/doc/stable/reference/generated/numpy.array.html) of [`numpy.array`](https://numpy.org/doc/stable/reference/generated/numpy.array.html)s.<br>An array of multiple numerical sequence data. This is the collection that is searched based on the line pattern drawn.",
            LinePatternSearcher_dataset,
        ],
        "top_k": [
            "Optional parameter | Default: `10` | Integer.<br>The number of similar results needed.",
            LinePatternSearcher_top_k_slider,
        ],
    }
    return (LinePatternSearcher_inputs_dict,)


@app.cell
def _(
    LinePatternSearcher,
    LinePatternSearcher_dataset,
    LinePatternSearcher_top_k_slider,
    mo,
):
    LinePatternSearcher_widget = mo.ui.anywidget(
        LinePatternSearcher(
            dataset=LinePatternSearcher_dataset,
            top_k=LinePatternSearcher_top_k_slider.value
        )
    )
    return (LinePatternSearcher_widget,)


@app.cell(hide_code=True)
def _(LinePatternSearcher_widget):
    LinePatternSearcher_outputs_dict = {
        "top_k_indices": [
            "`list(int)`.<br>The indices of `top_k` most similar series in the `dataset`.",
            LinePatternSearcher_widget.top_k_indices,
        ],
        "top_k_dtw_distances": [
            "`list(float)`<br>The [Dynamic Time Warping distances](https://dtaidistance.readthedocs.io/en/latest/modules/dtw.html) of `top_k` most similar series with respect to the drawn line.",
            LinePatternSearcher_widget.top_k_dtw_distances,
        ],
    }
    return (LinePatternSearcher_outputs_dict,)


@app.cell(column=5)
def _():
    ScatterplotSelector_doc_description_str = r"""The `LinePatternSearcher` lets users draw a line and find series with a similar line pattern within a collection of series. It works even when the patterns are stretched, shifted, or vary slightly in scale. Due to technical reasons, it allows drawing only from left to right."""
    return (ScatterplotSelector_doc_description_str,)


@app.cell(hide_code=True)
def _(make_blobs, make_circles, make_moons, mo, np):
    def make_different_2d_datasets():

        def label_to_colors(labels):
            palette = [
                "red", "blue", "green", "orange", "purple", "brown",
                "cyan", "magenta", "olive", "teal", "darkred", "gold"
            ]
            return [palette[i % len(palette)] for i in labels]

        def make_dataset(X, y=None):
            if y is None:
                return {"x": X[:, 0].tolist(), "y": X[:, 1].tolist()}
            return {
                "x": X[:, 0].tolist(),
                "y": X[:, 1].tolist(),
                "color": label_to_colors(y)
            }

        # Dataset 1: Gaussian blobs
        X1, y1 = make_blobs(n_samples=200, centers=4, cluster_std=0.6, random_state=1)
        dataset1 = make_dataset(X1, y1)

        # Dataset 2: Moons
        X2, y2 = make_moons(n_samples=200, noise=0.08, random_state=2)
        dataset2 = make_dataset(X2, y2)

        # Dataset 3: Concentric Circles
        X3, y3 = make_circles(n_samples=200, factor=0.45, noise=0.06, random_state=3)
        dataset3 = make_dataset(X3, y3)

        # Dataset 4: X-pattern (manually generated)
        X4 = np.random.randn(200, 2)
        y4 = (X4[:, 0] * X4[:, 1] > 0).astype(int)  # Diagonal XOR-style pattern
        dataset4 = make_dataset(X4 * 2, y4)

        # Dataset 5: Cluster chain
        X5a, y5a = make_blobs(n_samples=100, centers=[[i, 0] for i in range(5)], cluster_std=0.3, random_state=5)
        y5a = np.arange(5).repeat(20)
        dataset5 = make_dataset(X5a, y5a)

        # Dataset 6: Vertical lines
        X6 = np.vstack([
            np.random.normal(loc=i, scale=0.05, size=(50, 1)) for i in [-2, -1, 0, 1, 2]
        ])
        Y6 = np.random.uniform(-2, 2, size=(250, 1))
        X6 = np.hstack([X6, Y6])
        y6 = np.repeat(np.arange(5), 50)
        dataset6 = make_dataset(X6, y6)

        # Final dataset list
        return [dataset1, dataset2, dataset3, dataset4, dataset5, dataset6]


    ScatterplotSelector_datasets = make_different_2d_datasets()
    ScatterplotSelector_datasets_dropdown = mo.ui.dropdown(
        options=dict([(f"dataset[{i}]", i) for i in range(len(ScatterplotSelector_datasets))]),
        value="dataset[0]",
        label="Pick a dataset for viewing: ",
    )
    ScatterplotSelector_x_cols = ["x"]*len(ScatterplotSelector_datasets)
    ScatterplotSelector_y_cols = ["y"]*len(ScatterplotSelector_datasets)
    ScatterplotSelector_color_cols = ["color"]*len(ScatterplotSelector_datasets)
    ScatterplotSelector_color_cols[4] = "" # For demo purpose
    return (
        ScatterplotSelector_color_cols,
        ScatterplotSelector_datasets,
        ScatterplotSelector_datasets_dropdown,
        ScatterplotSelector_x_cols,
        ScatterplotSelector_y_cols,
    )


@app.cell(hide_code=True)
def _(
    ScatterplotSelector_color_cols,
    ScatterplotSelector_datasets,
    ScatterplotSelector_datasets_dropdown,
    ScatterplotSelector_x_cols,
    ScatterplotSelector_y_cols,
    mo,
):
    ScatterplotSelector_inputs_dict = {
        "datasets": [
            "Required parameter | `list([pandas.DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html))`.<br>A list of datasets, each with atleast two numerical attributes and possibly one categorical attribute corresponding to the color of individual data items.",
            mo.vstack([
                ScatterplotSelector_datasets_dropdown, 
                mo.ui.table(ScatterplotSelector_datasets[ScatterplotSelector_datasets_dropdown.value])
            ])
        ],
        "x_cols": [
            "Required parameter | `list(str)`.<br>The list of X-axis column names for the scatterplots for all the `datasets`.", ScatterplotSelector_x_cols
        ],
        "y_cols": [
            "Required parameter | `list(str)`.<br>The list of Y-axis column names for the scatterplots for all the `datasets`.", ScatterplotSelector_y_cols
        ],
        "color_cols": [
            "Optional parameter | Default: None | `list(str)`.<br>The list of color column names for the scatterplots for all the `datasets`. Pass empty string, if the corresponding dataset does not have any dedicated color column.", ScatterplotSelector_color_cols
        ],
    }
    return (ScatterplotSelector_inputs_dict,)


@app.cell
def _(
    ScatterplotSelector,
    ScatterplotSelector_color_cols,
    ScatterplotSelector_datasets,
    ScatterplotSelector_x_cols,
    ScatterplotSelector_y_cols,
    mo,
):
    ScatterplotSelector_widget = mo.ui.anywidget(ScatterplotSelector(
        datasets=ScatterplotSelector_datasets, 
        x_cols=ScatterplotSelector_x_cols,
        y_cols=ScatterplotSelector_y_cols,
        color_cols=ScatterplotSelector_color_cols,
    ))
    return (ScatterplotSelector_widget,)


@app.cell(hide_code=True)
def _(ScatterplotSelector_widget):
    ScatterplotSelector_outputs_dict = {
        "selected_index": [
            "`int`.<br>The index of of the selected dataset in the `datasets` list. If none selected, then it is assigned the value -1.",
            ScatterplotSelector_widget.selected_index,
        ],
    }
    return (ScatterplotSelector_outputs_dict,)


if __name__ == "__main__":
    app.run()
