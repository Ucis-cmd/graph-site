from flask import Flask, render_template
import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
from mpld3 import plugins, utils
import matplotlib

matplotlib.use("agg")

app = Flask(__name__)


class HighlightBarPlugin(plugins.PluginBase):
    JAVASCRIPT = """
    mpld3.register_plugin("highlightbar", HighlightBarPlugin);
    HighlightBarPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    HighlightBarPlugin.prototype.constructor = HighlightBarPlugin;
    HighlightBarPlugin.prototype.requiredProps = ["id"];
    HighlightBarPlugin.prototype.defaultProps = {};

    function HighlightBarPlugin(fig, props) {
        mpld3.Plugin.call(this, fig, props);
    };

    HighlightBarPlugin.prototype.draw = function() {
        var obj = mpld3.get_element(this.props.id);
        console.log(obj);
        var bars = obj.elements();
        console.log(bars);

        bars.on("mouseover", function(d, i) {
            d3.select(this).style("fill", "orange");
        }).on("mouseout", function(d, i) {
            d3.select(this).style("fill", "skyblue");
        });
    };
    """

    def __init__(self, bar):
        self.dict_ = {"type": "highlightbar", "id": utils.get_id(bar)}


@app.route("/")
def hello_world():
    categories = ["Apples", "Bananas", "Oranges", "Grapes", "Pineapples"]
    np.random.seed(42)
    values = np.random.randint(10, 100, size=len(categories))

    fig, ax = plt.subplots()

    bars = ax.bar(categories, values, color="skyblue")

    labels = []

    for i, (bar, category) in enumerate(zip(bars, categories)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 3,
            category,
            ha="center",
            va="top",
            fontsize=10,
        )
        tooltip = plugins.LineLabelTooltip(bar, label=str(i))
        highlight = HighlightBarPlugin(bar)
        plugins.connect(plt.gcf(), tooltip, highlight)

    ax.set_xlabel("Fruits")
    ax.set_ylabel("Values")
    ax.set_title("Fruit Values Bar Histogram")

    ax.set_xticks([])

    html_str = mpld3.fig_to_html(fig)
    with open("./templates/graph.html", "w") as Html_file:
        Html_file.write(html_str)

    return render_template("graph.html")


@app.route("/graph1")
def interactive_graph():
    fig, ax = plt.subplots()
    ax.grid(True, alpha=0.3)

    N = 50
    df = pd.DataFrame(index=range(N))
    df["x"] = np.random.randn(N)
    df["y"] = np.random.randn(N)
    df["z"] = np.random.randn(N)

    labels = []
    targets = []
    for i in range(N):
        label = df.iloc[[i], :].T
        label.columns = ["Row {0}".format(i)]
        target = round((df.iloc[i, 0]))
        labels.append(str(label.to_html()))
        targets.append(f"/{target}")

    points = ax.plot(df.x, df.y, "o", color="b", mec="k", ms=15, mew=1, alpha=0.6)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("HTML tooltips", size=20)

    tooltip = plugins.PointHTMLTooltip(
        points[0], labels, targets, voffset=10, hoffset=10
    )
    plugins.connect(fig, tooltip)

    html_str = mpld3.fig_to_html(fig)

    with open("./templates/graph1.html", "w") as Html_file:
        Html_file.write(html_str)

    return render_template("graph1.html")


if __name__ == "__main__":
    app.run(debug=True)
