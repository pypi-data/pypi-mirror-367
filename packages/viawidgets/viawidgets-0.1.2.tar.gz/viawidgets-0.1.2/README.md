# viawidgets

Concept sketch:
![ViaWidgets Concept Sketch](docs/viawidgets-concept-sketch.jpg)

## What are ViaWidgets?

They are interactive widgets (based on [anywidget](https://anywidget.dev/)) centered around two core concepts:

- **via**: You go "**via**" them (input data → ViaWidget → output data).
- **VIA**: They use **V**isualization for **I**nteraction **A**ugmentation.

---

A simple example is the `HistogramRangeFilter`:

- **via**: It is used to filter an input array based on a selected range. The filtered array can be used in subsequent notebook cells.
- **VIA**: The range slider is augmented by the histogram, allowing interpretation of the underlying distribution for an informed interaction.

### ⚠️ This package is in an early development stage and is currently just built as a research prototype. Expect

- Bugs 🐛🐛🐛🐛
- Frequent changes to widget names, parameters, etc.
- A lack of proper documentation.

### Some plans for the future

- Many, many more ViaWidgets. Also, new kinds of ViaWidgets (e.g., collaborative(web-based) ViaWidgets).
- Adding/modifying different visualizations to fit different data characteristics/analysis tasks/user personas.
- Providing some consistency across different ViaWidgets (e.g., common styling options, shared data models)
- Figuring out a way to combine compatible ViaWidgets dynamically for a bi-directional brushing and linking.
- Widget suggestions and widget combination templates for certain application scenarios.
