import * as d3 from "https://esm.sh/d3@7";

export default {
    render({ model, el }) {
        const datasets = model.get("datasets");
        const x_cols = model.get("x_cols");
        const y_cols = model.get("y_cols");
        const color_cols = model.get("color_cols");
        const columns = model.get("columns");

        const plotWidth = 200;
        const plotHeight = 200;
        const margin = { top: 10, right: 10, bottom: 30, left: 30 };

        el.innerHTML = "";

        // Main container
        const container = d3.select(el)
            .append("div")
            .style("display", "flex")
            .style("flex-direction", "column")
            .style("align-items", "center");
        // Grid of plots
        const grid = container
            .append("div")
            .style("display", "grid")
            .style("grid-template-columns", `repeat(${columns}, ${plotWidth}px)`)
            .style("gap", "20px")
            .style("margin-bottom", "20px");

        const svgs = [];

        datasets.forEach((data, i) => {
            const x_col = x_cols[i];
            const y_col = y_cols[i];
            const color_col = color_cols[i]; // May be null

            const x = data[x_col];
            const y = data[y_col];
            const color = color_col ? data[color_col] || [] : [];
            console.log("x", x, " y ", y, "color", color)


            const zipped = x.map((xVal, j) => ({
                x: xVal,
                y: y[j],
                color: (color.length > j) ? color[j] : "black",
            }));

            const xScale = d3.scaleLinear().domain(d3.extent(x)).range([margin.left, plotWidth - margin.right]);
            const yScale = d3.scaleLinear().domain(d3.extent(y)).range([plotHeight - margin.bottom, margin.top]);

            const svg = grid.append("svg")
                .attr("width", plotWidth)
                .attr("height", plotHeight)
                .style("cursor", "pointer")
                .on("click", () => {
                    model.set("selected_index", i);
                    model.save_changes();
                });

            // Background border rect
            svg.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", plotWidth)
                .attr("height", plotHeight)
                .attr("rx", 4)
                .attr("ry", 4)
                .attr("fill", "white")
                .attr("stroke", "#ccc")
                .attr("stroke-width", 1)
                .attr("class", "border-rect");

            // Points
            svg.selectAll("circle")
                .data(zipped)
                .enter()
                .append("circle")
                .attr("cx", d => xScale(d.x))
                .attr("cy", d => yScale(d.y))
                .attr("r", 3)
                .attr("fill", d => d.color)
                .attr("fill-opacity", 0.5);

            svgs.push(svg);
        });

        // Styled Reset Button after grid
        container.append("button")
        .text("Reset Selection")
        .style("padding", "6px 12px")
        .style("font-size", "14px")
        .style("background-color", "#f0f0f0")
        .style("border", "1px solid #ccc")
        .style("border-radius", "5px")
        .style("cursor", "pointer")
        .on("mouseover", function () {
            d3.select(this).style("background-color", "#e0e0e0");
        })
        .on("mouseout", function () {
            d3.select(this).style("background-color", "#f0f0f0");
        })
        .on("click", () => {
            model.set("selected_index", -1);
            model.save_changes();
        });

        // Only update border color when selection changes
        const updateSelection = () => {
            const selectedIndex = model.get("selected_index");
            svgs.forEach((svg, i) => {
                svg.select(".border-rect")
                    .attr("stroke", i === selectedIndex ? "slateblue" : "#ccc")
                    .attr("stroke-width", i === selectedIndex ? 10 : 1);
            });
        };

        model.on("change:selected_index", updateSelection);
        updateSelection();
    }
};
