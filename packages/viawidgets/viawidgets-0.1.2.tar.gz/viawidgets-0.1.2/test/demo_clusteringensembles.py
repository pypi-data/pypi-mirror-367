import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def importing_python_modules():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import altair as alt

    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.datasets import make_blobs, make_moons, make_circles

    from drawdata import ScatterWidget
    from viawidgets.widgets import ScatterplotSelector
    return (
        AgglomerativeClustering,
        DBSCAN,
        KMeans,
        ScatterWidget,
        ScatterplotSelector,
        alt,
        make_blobs,
        make_circles,
        make_moons,
        mo,
        np,
        pd,
    )


@app.cell
def _(mo):
    mo.callout(mo.md("### Note: You are seeing the marimo notebook in **app view** mode."))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Same data - different clustering results

    In the previous session, we learned about clustering and different clustering algorithms. Now let us see how different clustering algorithms (with pre-defined hyperparameters) cluster the data items from the same dataset differently.

    For this example, you can work with your own dataset - by either choosing one of the pre-existing two-dimensional dataset, or drawing your own new dataset.
    """
    )
    return


@app.cell(hide_code=True)
def generate_random_2d_datasets(make_blobs, make_circles, make_moons, mo, np):
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
        ScatterplotSelector_x_cols,
        ScatterplotSelector_y_cols,
    )


@app.cell
def scatterplot_selector_widget(
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


@app.cell
def drawdata_scatterwidget(ScatterWidget, mo):
    scatter_widget = mo.ui.anywidget(ScatterWidget())
    return (scatter_widget,)


@app.cell
def dataset_input_method_choices(
    ScatterplotSelector_widget,
    mo,
    scatter_widget,
):
    mo.accordion(
        {
            "Choose among a pre-built dataset": mo.vstack([
                mo.md("""
                If you want to select, one of the pre-existing dataset, please tap on one of the scatterplots below. 

    Please note that by selecting a dataset, you withdraw from the option of using a drawn dataset(below).
                """),
                ScatterplotSelector_widget
            ]),
            "Draw your own dataset": mo.vstack([
                mo.md("""
                Please use the scatterplot widget below to visualize your dataset. If you'd like to compare your interpretation of clusters with the actual clustering results, feel free to use up to four different colors for the clusters.
                """),
                scatter_widget
            ])
        }, multiple=True
    )
    return


@app.cell
def clustering_data(
    AgglomerativeClustering,
    DBSCAN,
    KMeans,
    ScatterplotSelector_datasets,
    ScatterplotSelector_widget,
    pd,
    scatter_widget,
):
    def add_clustering_label(df, method, params):
        """
        df: pandas DataFrame with columns 'x', 'y'
        method: string, clustering method ('kmeans',  or 'dbscan' for now)
        params: dict of hyperparameters

        returns: df with new cluster label column
        """
        if method == 'kmeans':
            n_clusters = params.get('n_clusters', 5)
            random_state = params.get('random_state', 42)
            model = KMeans(n_clusters=n_clusters, random_state=random_state)
            col_name = f'kmeans_{n_clusters}'
        elif method == 'dbscan':
            eps = params.get('eps', 0.5)
            min_samples = params.get('min_samples', 5)
            model = DBSCAN(eps=eps, min_samples=min_samples)
            col_name = f'dbscan_{eps}_{min_samples}'
        elif method == 'hier': 
            linkage = params.get('linkage', 'ward')
            n_clusters = params.get('n_clusters', 4)
            model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
            clusters = model.fit_predict(df[['x', 'y']])
            col_name = f'hier_{linkage}_{n_clusters}'
        else:
            raise ValueError(f"Clustering method '{method}' not supported")

        clusters = model.fit_predict(df[['x', 'y']])
        df[col_name] = clusters
        return df

    def add_multiple_clustering_labels(df):
        add_clustering_label(df, 'kmeans', {'n_clusters': 4})
        add_clustering_label(df, 'dbscan', {'eps': 5})
        add_clustering_label(df, 'hier', {'n_clusters': 4})

    if ScatterplotSelector_widget.selected_index != -1:
        df = pd.DataFrame(ScatterplotSelector_datasets[ScatterplotSelector_widget.selected_index])
    else:
        df = scatter_widget.data_as_pandas

    if len(df.index) > 0:
        current_columns = set(df.columns)
        add_multiple_clustering_labels(df)
        clustering_cols = list(set(df.columns) - current_columns)

    return clustering_cols, df


@app.cell
def displaying_clustering_results(alt, clustering_cols, df, mo):
    # Ensure original 'color' column is not modified
    if len(df.index) > 0:
        # Initialize new columns for clustering colors, preserving the original color
        for clustering_col in clustering_cols:
            df[clustering_col + "_color"] = ["None"]*len(df.index)

            # Step 1: Count all combinations (do not alter the 'color' column here)
            pair_counts = df.value_counts(subset=['color', clustering_col]).reset_index(name='count')

            # Step 2: Sort by count descending
            pair_counts = pair_counts.sort_values(by='count', ascending=False)

            # Step 3: Create mapping from clusters to colors
            used_colors = set()
            used_colBs = set()
            cluster_to_color_dict = {}

            for _, row in pair_counts.iterrows():
                colB, color, count = row[clustering_col], row['color'], row['count']
                # Ensure we don't reuse colors or clusters already assigned
                if color not in used_colors and colB not in used_colBs:
                    cluster_to_color_dict[colB] = color
                    used_colors.add(color)
                    used_colBs.add(colB)

            # Assign colors based on the clustering column without affecting the 'color' column
            df[clustering_col + "_color"] = df.apply(
                lambda row: cluster_to_color_dict.get(row[clustering_col], None),
                axis=1
            )

        # Handling remaining categories with additional colors if needed
        additional_colors = ["violet", "gold", "gray", "lime", "brown", "black", "pink", "olive"]

        for _i in range(len(clustering_cols)):
            clustering_col1 = clustering_cols[_i]
            clustering_col1_remaining_ids = df[df[clustering_col1 + "_color"].isnull()][clustering_col1].value_counts().index.tolist()

            for clustering_col1_id in clustering_col1_remaining_ids:
                df.loc[df[clustering_col1] == clustering_col1_id, clustering_col1 + "_color"] = additional_colors[0]
                additional_colors = additional_colors[1:]

            if _i == len(clustering_cols) - 1:
                continue

            clustering_col2 = clustering_cols[_i + 1]

        # Create individual charts
        color_columns = ["color"] + [_clustering_col + "_color" for _clustering_col in clustering_cols]
        charts = []
        for color_col in color_columns:
            chart = alt.Chart(df).mark_point().encode(
                x='x:Q',
                y='y:Q',
                color=alt.Color(f'{color_col}:N', title=color_col, legend=None)
            ).properties(
                width=190,
                height=190,
                title=color_col.removesuffix("_color") if color_col != "color" else "Original"
            )
            charts.append(chart)

        # Combine charts horizontally
        combined_chart = alt.hconcat(*charts)

        output_final = mo.vstack([
            mo.md("## Clustering results:"),
            mo.ui.altair_chart(combined_chart)
        ])
    else:
        output_final = mo.md("Please draw or select a dataset to see the clustering results.")

    output_final

    return


if __name__ == "__main__":
    app.run()
