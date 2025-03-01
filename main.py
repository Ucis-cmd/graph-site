from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
from mpld3 import plugins
import matplotlib
from custom_plugins.HighlightBar import HighlightBarPlugin
from custom_plugins.HighlightPie import HighlightPiePlugin
from peewee import fn
from models import Dinosaur
from data_conversions import db_to_csv, csv_to_db
from werkzeug.urls import unquote

matplotlib.use("agg")

app = Flask(__name__)
app.jinja_env.filters["unquote"] = unquote

# whats left:
# make the navbar links
# make the website responsive, but not necessary (resize depending on screen size, might be hard because of the graphs, havent checked how to resize them, since the html is difficult to access, there might have been also difficulties with resizing gifs)
# change the design of the graphs, select different colors, (check if the background can be made transparent?)


def init_db():
    if not Dinosaur.table_exists():
        csv_to_db("./static/dist/csv/dinosaur_data.csv")


def get_data_alphabetical(*comparisons):
    first_letter_query = fn.Upper(fn.Substr(Dinosaur.name, 1, 1))
    alphabetical_query = (
        Dinosaur.select(
            first_letter_query.alias("first_letter"),
            fn.GROUP_CONCAT(Dinosaur.name).alias("dinosaur_names"),
            fn.GROUP_CONCAT(Dinosaur.link).alias("dinosaur_links"),
            fn.COUNT(Dinosaur.id).alias("count"),
        )
        .where(*comparisons)
        .group_by(first_letter_query)
        .order_by(first_letter_query)
    )

    # convert the query result to a list of dictionaries
    alphabetical_groups = []
    for group in alphabetical_query:
        alphabetical_groups.append(
            {
                "first_letter": group.first_letter,
                "dinosaur_names": group.dinosaur_names.split(","),
                "dinosaur_links": group.dinosaur_links.split(","),
                "count": group.count,
            }
        )
    return alphabetical_groups


@app.route("/")
def homepage():
    query = (
        Dinosaur.select(
            Dinosaur.type, Dinosaur.link, fn.COUNT(Dinosaur.name).alias("count")
        )
        .group_by(Dinosaur.type)
        .order_by(Dinosaur.type)
    )
    unique_types = []
    type_count = []
    links = []
    for item in query:
        unique_types.append(item.type.capitalize())
        type_count.append(item.count)
        links.append(f"/{item.type}")

    fig, ax = plt.subplots()

    bars = ax.bar(unique_types, type_count, color="skyblue")

    for i, (bar, category, link) in enumerate(zip(bars, unique_types, links)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 3,
            category,
            ha="center",
            va="top",
            fontsize=10,
        )
        highlight = HighlightBarPlugin(bar, link)
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


@app.route("/<type>")
def type_page(type):
    diet_query = (
        Dinosaur.select(Dinosaur.diet, fn.COUNT(Dinosaur.name).alias("count"))
        .where(Dinosaur.type == type)
        .group_by(Dinosaur.diet)
    )

    alphabetical_groups = get_data_alphabetical(Dinosaur.type == type)

    diets = []
    diet_count = []
    for item in diet_query:
        diets.append(item.diet)
        diet_count.append(item.count)

    fig, ax = plt.subplots()
    pie, texts, autotexts = ax.pie(diet_count, labels=diets, autopct="%1.1f%%")

    for wedge, diet in zip(pie, diets):
        plugins.connect(fig, HighlightPiePlugin(wedge, f"/{type}/{diet}"))

    html_str = mpld3.fig_to_html(fig)
    with open("./templates/diet_pie.html", "w") as Html_file:
        Html_file.write(html_str)

    return render_template(
        "type_page.html",
        type=type,
        alphabetical_groups=alphabetical_groups,
        zip=zip,  # unquote is used to convert url to the same format as request.path
    )


@app.route("/<type>/<diet>")
def type_diet_page(type, diet):
    alphabetical_groups = get_data_alphabetical(
        Dinosaur.type == type, Dinosaur.diet == diet
    )

    return render_template(
        "type_page.html",
        type=type,
        diet=diet,
        alphabetical_groups=alphabetical_groups,
        zip=zip,
    )


@app.route("/download")
@app.route("/download/<type>")
@app.route("/download/<type>/<diet>")
def download(type=None, diet=None):
    if type and diet:
        query = Dinosaur.select().where(Dinosaur.type == type, Dinosaur.diet == diet)
        path = f"./downloads/dinosaur_data_{type}_{diet}.csv"
    elif type:
        query = Dinosaur.select().where(Dinosaur.type == type)
        path = f"./downloads/dinosaur_data_{type}.csv"
    else:
        query = Dinosaur.select()
        path = "./downloads/dinosaur_data_.csv"
    db_to_csv(path, query)
    return send_file(path, as_attachment=True)


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
