from flask import Flask, render_template
import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
from mpld3 import plugins, utils
import matplotlib
from custom_plugins.HighlightBar import HighlightBarPlugin
from peewee import SqliteDatabase, fn
from models import Dinosaur, db
from data_conversions import db_to_csv, csv_to_db
import os

matplotlib.use("agg")

app = Flask(__name__)


def init_db():
    if not Dinosaur.table_exists():
        csv_to_db("./static/dist/csv/dinosaur_data.csv")


@app.route("/")
def homepage():
    # get the unique values from 'type' column, place them in an array
    # for each value in array, get the amount of values that are in the database
    # and then make a bar graph from that

    query = (
        Dinosaur.select(Dinosaur.type, fn.COUNT(Dinosaur.name).alias("count"))
        .group_by(Dinosaur.type)
        .order_by(Dinosaur.type)
    )
    unique_types = []
    type_count = []
    print(query)
    for item in query:
        unique_types.append(item.type)
        type_count.append(item.count)

    fig, ax = plt.subplots()

    bars = ax.bar(unique_types, type_count, color="skyblue")

    for i, (bar, category) in enumerate(zip(bars, unique_types)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 3,
            category,
            ha="center",
            va="top",
            fontsize=10,
        )
        highlight = HighlightBarPlugin(bar)
        plugins.connect(
            plt.gcf(), highlight
        )  # multiple plugins not working, update highlightbarplugin, if more functionality needed (just ask chatgpt or deepseek to do that)

    ax.set_xlabel("Dinosaur types")
    ax.set_ylabel("Amount")
    ax.set_title("Dinosaurs")

    ax.set_xticks([])

    html_str = mpld3.fig_to_html(fig)
    with open("./templates/graph2.html", "w") as Html_file:
        Html_file.write(html_str)

    return render_template("base.html")


@app.route("/graph1")
def graph1():
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


@app.route("/graph2")
def graph2():
    return render_template("graph2.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
