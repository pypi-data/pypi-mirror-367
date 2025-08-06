import * as d3 from "https://esm.sh/d3@7";

export default {
    render({ model, el }) {
        const width = model.get("width");
        const height = model.get("height");
        const counts = model.get("counts");
        const binEdges = model.get("bin_edges");
        const mainColor = "darkslateblue";
        const y_axis_visible = model.get("y_axis_visible");  // Check for y-axis visibility

        el.innerHTML = "";

        const histHeight = height;
        const sliderHeight = 80;
        const totalHeight = histHeight + sliderHeight;
        const margin = { top: 10, right: 30, bottom: 30, left: 40 };
        const sliderYStart = histHeight + 5;
        const sliderTrackY = sliderYStart + 15;

        const svg = d3
            .select(el)
            .append("svg")
            .attr("width", width)
            .attr("height", totalHeight);

        const x = d3
            .scaleLinear()
            .domain([binEdges[0], binEdges[binEdges.length - 1]])
            .range([margin.left, width - margin.right]);

        const y = d3
            .scaleLinear()
            .domain([0, d3.max(counts)])
            .nice()
            .range([histHeight - margin.bottom, margin.top]);

        // === Histogram bars ===
        const barGroup = svg.append("g").attr("class", "histogram-bars");
        const bars = barGroup
            .selectAll("rect")
            .data(counts)
            .enter()
            .append("rect")
            .attr("x", (d, i) => x(binEdges[i]))
            .attr("y", d => y(d))
            .attr("width", (d, i) => x(binEdges[i + 1]) - x(binEdges[i]) - 1)
            .attr("height", d => y(0) - y(d))
            .attr("fill", mainColor)
            .attr("fill-opacity", 1.0)
            .attr("class", "hist-bar");

        // === Axes ===
        if (y_axis_visible) {
            svg.append("g")
                .attr("transform", `translate(0,${histHeight - margin.bottom})`)
                .call(d3.axisBottom(x));
            svg.append("g")
                .attr("transform", `translate(${margin.left},0)`)
                .call(d3.axisLeft(y));
        } else {
            // Only add the x-axis if y-axis is not visible
            svg.append("g")
                .attr("transform", `translate(0,${histHeight - margin.bottom})`)
                .call(d3.axisBottom(x));
        }

        // === Snap boundaries ===
        svg.append("g")
            .attr("class", "snap-lines")
            .selectAll("line")
            .data(binEdges)
            .enter()
            .append("line")
            .attr("x1", (d, i) => x(d))
            .attr("x2", (d, i) => x(d))
            .attr("y1", sliderTrackY - 10)
            .attr("y2", sliderTrackY + 10)
            .attr("stroke", mainColor)
            .attr("stroke-opacity", 0.3)
            .attr("stroke-width", 1);

        // === Slider track ===
        svg.append("line")
            .attr("x1", margin.left)
            .attr("x2", width - margin.right)
            .attr("y1", sliderTrackY)
            .attr("y2", sliderTrackY)
            .attr("stroke", mainColor)
            .attr("stroke-width", 3)
            .attr("stroke-opacity", 0.3);

        // === D3 Brush ===
        const brush = d3.brushX()
            .extent([[margin.left, sliderTrackY - 6], [width - margin.right, sliderTrackY + 6]])
            .on("brush end", brushed);

        const brushGroup = svg.append("g")
            .attr("class", "brush")
            .call(brush);

        brushGroup.select(".selection")
            .attr("fill", mainColor)
            .attr("fill-opacity", 1);

        // === Initial brush move ===
        const [initialStart, initialEnd] = model.get("selected_range");
        brushGroup.call(brush.move, [x(initialStart), x(initialEnd)]);

        // === Highlight bars ===
        function updateHistogramHighlight() {
            const [start, end] = model.get("selected_range");
            svg.selectAll(".hist-bar")
                .attr("fill-opacity", (d, i) =>
                    binEdges[i] >= start && binEdges[i + 1] <= end ? 1.0 : 0.3
                );
        }

        // === Brushing logic ===
        function brushed(event) {
            if (!event.selection || event.sourceEvent?.type === "zoom") return;

            const [x0, x1] = event.selection;

            const snap = (slider_x) => {
                let min_diff = Infinity;
                let closestEdge = binEdges[0];
                for (let i = 0; i < binEdges.length; i++) {
                    const edge = x(binEdges[i]);
                    const diff = Math.abs(slider_x - edge);
                    if (diff < min_diff) {
                        min_diff = diff;
                        closestEdge = binEdges[i];
                    }
                }
                return [closestEdge, x(closestEdge)];
            };

            const [snappedStart_edge, snappedStart_x] = snap(x0);
            const [snappedEnd_edge, snappedEnd_x] = snap(x1);
            const minVal_x = Math.min(snappedStart_x, snappedEnd_x);
            const maxVal_x = Math.max(snappedStart_x, snappedEnd_x);
            const minVal_edge = Math.min(snappedStart_edge, snappedEnd_edge);
            const maxVal_edge = Math.max(snappedStart_edge, snappedEnd_edge);
            if (minVal_x !== x0 || maxVal_x !== x1) {
                brushGroup.call(brush.move, [minVal_x, maxVal_x]);
            }

            const [currentStart, currentEnd] = model.get("selected_range");
            if (minVal_edge !== currentStart || maxVal_edge !== currentEnd) {
                model.set("selected_range", [minVal_edge, maxVal_edge]);
                model.save_changes();
            }

            updateHistogramHighlight();
        }

        // React to changes from Python
        model.on("change:selected_range", () => {
            const [start, end] = model.get("selected_range");
            brushGroup.call(brush.move, [x(start), x(end)]);
        });
    }
};
