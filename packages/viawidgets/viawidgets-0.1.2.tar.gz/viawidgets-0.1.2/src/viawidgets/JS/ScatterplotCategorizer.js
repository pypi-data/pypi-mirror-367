import * as d3 from "https://esm.sh/d3@7";

export default {
    render({ model, el }) {
        const width = 600;
        const height = 400;
        const margin = { top: 20, right: 20, bottom: 40, left: 40 };

        // Create a container to hold both scatterplot and categories
        const container = d3.select(el).append("div")
            .style("display", "flex") // Use flexbox to align them side by side
            .style("align-items", "flex-start");

        // Create the scatterplot SVG with padding
        const svg = container.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const points = model.get("points");
        let categories = model.get("categories");
        let selectedCategory = model.get("selected_category");

        // Initialize the points with their categories (set to gray initially if no category)
        points.forEach((point, index) => {
            if (!point.category) {
                point.category = ""; // No category initially
            }
        });

        // Create scales for the x and y axes based on the points' data
        const xScale = d3.scaleLinear()
            .domain([d3.min(points, d => d[0]) - 1, d3.max(points, d => d[0]) + 1])
            .range([0, width]);

        const yScale = d3.scaleLinear()
            .domain([d3.min(points, d => d[1]) - 1, d3.max(points, d => d[1]) + 1])
            .range([height, 0]); // Invert the Y axis so that values increase upwards

        // Add gridlines along the X and Y axes
        svg.append("g")
            .attr("class", "grid")
            .selectAll("line")
            .data(xScale.ticks())
            .enter()
            .append("line")
            .attr("x1", d => xScale(d))
            .attr("x2", d => xScale(d))
            .attr("y1", 0)
            .attr("y2", height)
            .attr("stroke", "#ccc")
            .attr("stroke-dasharray", "2,2");

        svg.append("g")
            .attr("class", "grid")
            .selectAll("line")
            .data(yScale.ticks())
            .enter()
            .append("line")
            .attr("y1", d => yScale(d))
            .attr("y2", d => yScale(d))
            .attr("x1", 0)
            .attr("x2", width)
            .attr("stroke", "#ccc")
            .attr("stroke-dasharray", "2,2");

        // Plot points with gray as the default color (uncategorized)
        const circles = svg.selectAll("circle")
            .data(points)
            .enter()
            .append("circle")
            .attr("cx", d => xScale(d[0]))
            .attr("cy", d => yScale(d[1]))
            .attr("r", 5)
            .attr("fill", "gray") // Initially all points are gray (uncategorized)
            .attr("class", "scatter-point");

        // Add brush for selection, adjust the extent to match plot area
        const brush = d3.brush()
            .extent([[0, 0], [width, height]]) // Brush extent matches the plot area (excluding margins)
            .on("start", brushStart)
            .on("brush", brushMove)
            .on("end", brushEnd);

        svg.append("g")
            .attr("class", "brush")
            .call(brush);

        function brushStart(event) {
            // Handle brush start
        }

        function brushMove(event) {
            // No color change while selecting, just handle brush behavior
        }

        function brushEnd(event) {
            if (!event.selection) return;

            const selection = event.selection;

            // Ensure the brush selection is correctly mapped to the scatterplot area, considering Y inversion
            const selectedPoints = [];
            circles.each(function(d) {
                const xInRange = d[0] >= xScale.invert(selection[0][0]) && d[0] <= xScale.invert(selection[1][0]);
                const yInRange = d[1] <= yScale.invert(selection[0][1]) && d[1] >= yScale.invert(selection[1][1]); // Account for Y-axis inversion

                if (xInRange && yInRange) {
                    selectedPoints.push(d);
                }
            });

            // Store the selected points for categorization
            model.set("selected_points", selectedPoints);
            model.save_changes();
        }

        // Category circle interactions
        const categoryContainer = container.append("div")
            .style("display", "flex")
            .style("flex-direction", "column")
            .style("margin-left", "20px")
            .style("width", "200px");

        categories.forEach((category, index) => {
            const categoryDiv = categoryContainer.append("div")
                .attr("class", "category")
                .style("margin-bottom", "15px")
                .style("display", "flex")
                .style("align-items", "center");

            // Color indicator (no pop-up for color change)
            categoryDiv.append("div")
                .attr("class", "color-indicator")
                .style("width", "20px")
                .style("height", "20px")
                .style("background-color", getCategoryColor(category))
                .style("cursor", "pointer")
                .on("click", function() {
                    // Set the selected category when the color indicator is clicked
                    selectedCategory = category;
                    model.set("selected_category", selectedCategory);
                    model.save_changes();

                    // Highlight the selected category by adding a border
                    categoryDiv.style("border", "2px solid black");

                    // Remove borders from all other categories
                    categoryContainer.selectAll(".category").each(function() {
                        if (this !== categoryDiv.node()) {
                            d3.select(this).style("border", "none");
                        }
                    });
                });

            // Category text input
            categoryDiv.append("input")
                .attr("type", "text")
                .attr("value", category)
                .style("margin-left", "10px")
                .style("padding", "5px")
                .style("font-size", "14px")
                .style("width", "100px")
                .on("change", function() {
                    categories[index] = this.value;
                    model.set("categories", categories);
                    model.save_changes();
                });
        });

        // "Categorize them" button
        const categorizeButton = categoryContainer.append("button")
            .text("Categorize Selection")
            .style("margin-top", "20px")
            .style("padding", "10px 20px")
            .style("font-size", "16px")
            .style("cursor", "pointer")
            .style("background-color", "#6c757d") // Neutral gray color
            .style("color", "white")
            .style("border", "none")
            .style("border-radius", "5px")
            .style("transition", "background-color 0.3s ease")
            .on("click", function() {
                const selectedPoints = model.get("selected_points");
                if (selectedPoints.length === 0 || !selectedCategory) {
                    alert("Please select points and a category first.");
                    return;
                }

                // Categorize the points in the selected area
                selectedPoints.forEach(point => {
                    point.category = selectedCategory;  // Update the point's category
                });

                // Update the points' categorization
                model.set("points", points);
                model.save_changes();

                // Categorize the points in the UI
                circles.each(function(d) {
                    if (selectedPoints.includes(d)) {
                        d3.select(this).attr("fill", getCategoryColor(selectedCategory));
                    }
                });

                // Reset brush selection by calling brush.move to clear the selection
                svg.select(".brush").call(brush.move, null);

                // Deselect the current category by resetting the selectedCategory to an empty string
                selectedCategory = "";
                model.set("selected_category", selectedCategory);
                model.save_changes();

                // Remove border from all categories
                categoryContainer.selectAll(".category").style("border", "none");
            });

        // Add Reset Button (aligned with Categorize Button)
        const resetButton = categoryContainer.append("button")
            .text("Reset")
            .style("margin-top", "10px")
            .style("padding", "10px 20px")
            .style("font-size", "16px")
            .style("cursor", "pointer")
            .style("background-color", "#f8f9fa") // Neutral background color
            .style("color", "#6c757d")
            .style("border", "1px solid #6c757d")
            .style("border-radius", "5px")
            .style("transition", "background-color 0.3s ease")
            .on("click", function() {
                // Reset categories and colors
                points.forEach(point => {
                    point.category = "";  // Remove category
                });

                // Update the points and reset their colors
                model.set("points", points);
                model.save_changes();

                circles.attr("fill", "gray"); // Reset to gray (uncategorized)
            });

        function getCategoryColor(category) {
            const colors = ["red", "blue", "green", "orange", "purple"];
            return category ? colors[categories.indexOf(category)] : "gray";
        }

        // Add X and Y axes
        const xAxis = d3.axisBottom(xScale);
        const yAxis = d3.axisLeft(yScale);

        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(xAxis);

        svg.append("g")
            .call(yAxis);
    }
};
