import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Investment Allocation""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(mo.md("You are looking at the notebook in its default **edit mode**."))
    return


@app.cell
def loading_python_modules():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import altair as alt

    # These two are pre-built viaWidgets we import
    from viawidgets.widgets import LinePatternSearcher
    from drawdata import BarWidget
    # the last one is constructed within this notebook
    return BarWidget, LinePatternSearcher, alt, mo, np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Generating a dummy time series dataset for stock prices:""")
    return


@app.cell
def generate_stock_prices_dataset(np):
    # Generate sample time series
    def generate_random_walk(length=128, scale=0.5):
        steps = np.random.normal(loc=0, scale=scale, size=length)
        series = np.cumsum(steps)
        series = (series - series.min()) / (
            series.max() - series.min()
        )  # normalize 0-1
        return series

    # Dummy dataset
    stock_prices_dataset = np.array(
        [generate_random_walk() for _ in range(20000)]
    )
    dummy_company_names = ["Company_"+str(i) for i in range(len(stock_prices_dataset))] 
    return dummy_company_names, stock_prices_dataset


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Draw a line to describe the pattern you are looking for:""")
    return


@app.cell
def filtering_based_on_line_pattern_drawn(
    LinePatternSearcher,
    mo,
    stock_prices_dataset,
):
    LinePatternSearcher_widget = mo.ui.anywidget(
        LinePatternSearcher(
            dataset=stock_prices_dataset,
            top_k=3
        )
    )
    LinePatternSearcher_widget
    return (LinePatternSearcher_widget,)


@app.cell
def _(LinePatternSearcher_widget, dummy_company_names, mo):
    company_names_top3_similar = []
    if len(LinePatternSearcher_widget.top_k_indices) == 3:
        company_names_top3_similar = [dummy_company_names[i] for i in LinePatternSearcher_widget.top_k_indices]
        output_company_selection_text = "The following companies had similar stock price over the last year:\n\n"
        for _company_name in company_names_top3_similar:
            output_company_selection_text += ("- "+_company_name + "\n\n")

        output_company_selection_text += "### Now, please assign your estimated ROI probability distribution for each of these companies."
        output_company_selection = mo.md(output_company_selection_text)
    else:
        output_company_selection = mo.md("")
    output_company_selection
    return (company_names_top3_similar,)


@app.cell
def _(BarWidget, company_names_top3_similar):
    bar_widget = BarWidget(collection_names=company_names_top3_similar, n_bins=100)
    bar_widget
    return (bar_widget,)


@app.cell
def normalizing_roi_probability_distributions(bar_widget):
    roi_probability_distributions_df = bar_widget.data_as_pandas
    # Group by company and normalize the 'value' column
    if len(roi_probability_distributions_df.index)>0:
        roi_probability_distributions_df['normalized_value'] = roi_probability_distributions_df.groupby('collection')['value'].transform(lambda x: x / x.sum())
    roi_probability_distributions_df
    return (roi_probability_distributions_df,)


@app.cell
def defining_sliders_for_allocator_widget(company_names_top3_similar, mo):
    company_slider_1 = mo.ui.slider(0, 100, value=0, show_value=True)
    company_slider_2 = mo.ui.slider(0, 100, value=0, show_value=True)
    company_slider_3 = mo.ui.slider(0, 100, value=0, show_value=True)
    all_sliders = [company_slider_1, company_slider_2, company_slider_3]

    allocation_sliders = {}
    for _company_name, _slider in zip(company_names_top3_similar, all_sliders):
        allocation_sliders[_company_name] = _slider
    return (
        allocation_sliders,
        company_slider_1,
        company_slider_2,
        company_slider_3,
    )


@app.cell
def computing_bar_chart_for_allocator_widget(
    allocation_sliders,
    alt,
    company_slider_1,
    company_slider_2,
    company_slider_3,
    mo,
    pd,
    roi_probability_distributions_df,
):
    def compute_combined_roi_df(allocation_sliders, roi_probability_distributions_df):
        # Assuming roi_probability_distributions_df has 'bin' and 'collection' columns
        # Step 1: Prepare a dictionary of allocation weights
        allocation_weights = {
            company_name: slider.value / 100  # Normalize the slider values to be between 0 and 1
            for company_name, slider in allocation_sliders.items()
        }

        # Step 2: Compute the combined_value for each bin
        def compute_combined_value(bin_data, allocation_weights):
            combined_value = 0
            for company_name, weight in allocation_weights.items():
                company_data = bin_data[bin_data['collection'] == company_name]  # Get data for the current company
                if not company_data.empty:
                    # Add the weighted value for this company and bin
                    combined_value += company_data['value'].iloc[0] * weight
            return combined_value

        # Step 3: Apply the computation for each bin
        combined_values = []
        for bin_value in roi_probability_distributions_df['bin'].unique():
            bin_data = roi_probability_distributions_df[roi_probability_distributions_df['bin'] == bin_value]
            combined_value = compute_combined_value(bin_data, allocation_weights)
            combined_values.append({'Predicted ROI(Profit %)': bin_value, 'Probability': combined_value})

        # Step 4: Create a DataFrame for the combined values
        combined_roi_df = pd.DataFrame(combined_values)
        return combined_roi_df

    allocation_percentages = []
    allocation_percentages.append(company_slider_1.value)
    allocation_percentages.append(company_slider_2.value)
    allocation_percentages.append(company_slider_3.value)

    if len(roi_probability_distributions_df.index)>0:

        combined_roi_df = compute_combined_roi_df(allocation_sliders, roi_probability_distributions_df)

        # Format the sliders in a markdown table
        table_md = "| Company Name | Allocation Percentage |\n|--------------|-----------------------|\n"
        for company_name, _slider in allocation_sliders.items():
            table_md += f"| {company_name} | {_slider} |\n"
        table_md += f"| Total | {sum([_slider.value for _slider in allocation_sliders.values()])} |\n"
        mo.md(table_md)

        # Create Altair chart
        chart = alt.Chart(combined_roi_df).mark_bar().encode(
            x='Predicted ROI(Profit %)',          # Nominal (categorical) encoding for the 'bin' column
            y='Probability'  # Quantitative encoding for the 'combined_values' column
        ).properties(
            width=650,
            height=120
        )
    return allocation_percentages, chart, table_md


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Please use the widget to decide the capital allocation percentages""")
    return


@app.cell
def displaying_allocator_widget(
    chart,
    mo,
    roi_probability_distributions_df,
    table_md,
):
    if len(roi_probability_distributions_df.index)>0:
        allocator_widget = mo.hstack([mo.md(table_md), mo.ui.altair_chart(chart)])
    else:
        allocator_widget = mo.md("")
    allocator_widget
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## If a valid allocation is availaible, the results will be displayed below.
    The results (dataset) will be shown as a widget with a "Download" button in bottom right corner.
    """
    )
    return


@app.cell
def downloadable_allocation_results(
    allocation_percentages,
    company_names_top3_similar,
    mo,
    pd,
):
    # Adding checks to 
    if len(company_names_top3_similar) == 3 and sum(allocation_percentages) <= 100 and sum(allocation_percentages) > 0:
        allocation_results = pd.DataFrame({
            "Company name": company_names_top3_similar,
            "Allocation percentage": allocation_percentages
        })
        output_results = allocation_results
    else:
        output_results = mo.md("")
    output_results
    return


if __name__ == "__main__":
    app.run()
