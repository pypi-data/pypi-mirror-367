import * as d3 from "https://esm.sh/d3@7";

export default {
    render({ model, el }) {
        const width = model.get("width");
        const height = model.get("height");

        el.innerHTML = "";

        const wrapper = d3.select(el)
            .style("display", "flex")
            .style("gap", "20px");

        // --- Left: Drawing Area ---
        const left = wrapper.append("div")
            .style("display", "flex")
            .style("flex-direction", "column")
            .style("gap", "10px");

        const svg = left.append("svg")
            .attr("width", width)
            .attr("height", height)
            .style("border", "1px solid #ccc")
            .style("cursor", "crosshair");

        let drawing = false;
        let pointMap = new Map();
        let lastX = null;

        const line = d3.line()
            .x(d => d[0])
            .y(d => d[1])
            .curve(d3.curveLinear);

        const path = svg.append("path")
            .attr("fill", "none")
            .attr("stroke", "slateblue")
            .attr("stroke-width", 3);

        svg.on("mousedown", (event) => {
            drawing = true;
            pointMap.clear();
            lastX = null;

            const [x, y] = d3.pointer(event, svg.node());
            pointMap.set(Math.round(x), y);
            path.attr("d", line(Array.from(pointMap.entries())));
        });

        window.addEventListener("mousemove", (event) => {
            if (!drawing) return;
            const [x, y] = d3.pointer(event, svg.node());
            const xKey = Math.round(x);
            if (lastX === null || xKey > lastX) {
                pointMap.set(xKey, y);
                lastX = xKey;
                path.attr("d", line(Array.from(pointMap.entries())));
            }
        });

        window.addEventListener("mouseup", () => {
            if (drawing) {
                drawing = false;
                const sorted = Array.from(pointMap.entries()).sort((a, b) => a[0] - b[0]);
                const flat = sorted.flat();
                model.set("_raw_points", flat);
                model.save_changes();
            }
        });

        // --- Right: Results Area ---
        const right = wrapper.append("div")
            .style("display", "flex")
            .style("flex-direction", "column")
            .style("flex", "1")
            .style("height", `${height}px`)
            .style("border-left", "1px solid #ccc")
            .style("padding", "10px");

        // Scrollable result content (excluding button)
        const scrollArea = right.append("div")
            .style("flex", "1")
            .style("overflow-y", "auto");

        const resultContainer = scrollArea.append("div")
            .attr("id", "results");

        // Bottom: Reset button (separate from scroll area)
        const resetContainer = right.append("div")
            .style("padding-top", "10px");

        const resetButton = resetContainer.append("button")
            .text("Reset")
            .on("click", () => {
                path.attr("d", null);
                pointMap.clear();
                model.set("_raw_points", []);
                model.save_changes();
            });

        const drawMiniChart = (container, data, color = "slateblue") => {
            const w = 200;
            const h = 60;

            const x = d3.scaleLinear()
                .domain([0, data.length - 1])
                .range([0, w]);

            const yExtent = d3.extent(data);
            const y = d3.scaleLinear()
                .domain([yExtent[0], yExtent[1]])
                .nice()
                .range([h, 0]);

            const miniSvg = container.append("svg")
                .attr("width", w)
                .attr("height", h);

            const l = d3.line()
                .x((d, i) => x(i))
                .y(d => y(d))
                .curve(d3.curveBasis);

            miniSvg.append("path")
                .datum(data)
                .attr("fill", "none")
                .attr("stroke", color)
                .attr("stroke-width", 1.5)
                .attr("d", l);
        };

        const updateResults = () => {
            const distances = model.get("top_k_dtw_distances");
            const series = model.get("_top_dtw_series");

            resultContainer.html("");  // Clear old

            const searchQuerySeries = model.get("_search_query_series");

            if (searchQuerySeries.length == 0) {
                resultContainer.append("div")
                    .style("margin-top", "10px")
                    .style("color", "#888")
                    .text("Draw a line to see top matches.");
            }
            // else
            // {
            //     resultContainer.append("div")
            //         .text("Query:")
            //         .style("font-weight", "bold")
            //         .style("margin-bottom", "4px");
            //     drawMiniChart(resultContainer, searchQuerySeries, "black");
            // }

            series.forEach((s, i) => {
                const row = resultContainer.append("div")
                    .style("margin-bottom", "14px");

                row.append("div")
                    .html(`<strong>Match #${i + 1}</strong> <span style="color: #666;">(Distance: ${distances?.[i]?.toFixed(2) ?? "?"})</span>`)
                    .style("margin-bottom", "4px");

                drawMiniChart(row, s);
            });
        };

        updateResults();
        model.on("change:_top_dtw_series", updateResults);
    }
};
