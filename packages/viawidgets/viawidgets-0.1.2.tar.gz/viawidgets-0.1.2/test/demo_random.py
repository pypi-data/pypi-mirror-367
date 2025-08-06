import marimo

__generated_with = "0.14.12"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import altair as alt

    from viawidgets.widgets import ScatterplotCategorizer
    return ScatterplotCategorizer, alt, mo, np, pd


@app.cell
def _(mo):
    n_slider = mo.ui.slider(start=0, stop=10, step=0.1, value=1, full_width=True)
    return (n_slider,)


@app.cell
def _(alt, mo, n_slider, np, pd):
    n = n_slider.value

    # Generate data for the curve
    x = np.linspace(0, 5, 1000)
    y = np.sin(n * np.pi * x)

    # Create a DataFrame
    data = pd.DataFrame({'x': x, 'y': y})

    # Create the Altair line chart
    chart = alt.Chart(data).mark_line().encode(
        x='x',
        y='y'
    ).properties(
        title=f'sin({n}*pi*x)'
    )

    # Show the widget
    mo.vstack([
        mo.ui.altair_chart(chart),
        n_slider
    ])
    return


@app.cell
def _(ScatterplotCategorizer, np):
    from sklearn.datasets import make_blobs

    # Generate 500 points with 3 clusters (blobs)
    X, _ = make_blobs(n_samples=1000, centers=3, random_state=42)

    # Calculate the min and max values of the X axis from the blobs data
    x_min, x_max = np.min(X[:, 0]), np.max(X[:, 0])

    # Generate outliers outside the X range
    # We'll generate outliers with X values that are either less than x_min or greater than x_max
    outliers_x = np.random.uniform(np.min(X[:, 0]), np.max(X[:, 0]), 50)
    outliers_y = np.random.uniform(np.min(X[:, 1]), np.max(X[:, 1]), 50)  # Random Y values within the existing Y range

    # Combine the outliers and the blobs
    outliers = np.column_stack((outliers_x, outliers_y))

    # Combine the blobs and outliers into one dataset
    points = np.vstack([X, outliers])

    # Now ensure that the scatterplot includes a sufficient range for both blobs and outliers
    scatter_widget = ScatterplotCategorizer(points=points.tolist())

    scatter_widget

    return


if __name__ == "__main__":
    app.run()
