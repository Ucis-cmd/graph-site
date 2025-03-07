from flask import Flask, render_template, send_file, redirect, url_for
import numpy as np
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins
import matplotlib
from custom_plugins.HighlightBar import HighlightBarPlugin
from custom_plugins.HighlightPie import HighlightPiePlugin
from peewee import fn
from models import Dinosaur
from data_conversions import db_to_csv, csv_to_db
from werkzeug.urls import unquote
from forms import DinosaurForm


matplotlib.use("agg")

app = Flask(__name__)
app.jinja_env.filters["unquote"] = unquote
app.config["SECRET_KEY"] = (
    "my key..."  # make this ignored by git, or change when sending
)

# whats left:
# add comments
# add init tutorial to github


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

    fig, ax = plt.subplots(figsize=(6, 6))

    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))

    # Set the extent to match the plot's data range
    x_min, x_max = -1, len(unique_types)  # Number of categories
    y_min, y_max = 0, max(type_count) + 10  # Add some padding to the y-axis
    ax.imshow(
        gradient,
        aspect="auto",
        cmap=plt.get_cmap("rainbow"),
        extent=(x_min, x_max, y_min, y_max),
        alpha=0.2,
    )

    bars = ax.bar(unique_types, type_count, color="skyblue")

    for i, (bar, category, link) in enumerate(zip(bars, unique_types, links)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 3,
            category,
            ha="center",
            va="top",
            color="black",
        )
        highlight = HighlightBarPlugin(bar, link)
        plugins.connect(
            plt.gcf(), highlight
        )  # multiple plugins not working, update highlightbarplugin, if more functionality needed (just ask chatgpt or deepseek to do that)

    ax.set_xlabel("Dinosaur types")
    ax.set_ylabel("Amount")

    ax.set_xticks([])

    html_str = mpld3.fig_to_html(fig)
    with open("./templates/graph2.html", "w") as Html_file:
        Html_file.write(html_str)

    return render_template("base.html")


@app.route("/create", methods=["GET", "POST"])
def create_dinosaur():
    form = DinosaurForm()
    if form.validate_on_submit():
        dinosaur = Dinosaur(
            name=form.name.data,
            diet=form.diet.data,
            period=form.period.data,
            period_name=form.period_name.data,
            lived_in=form.lived_in.data,
            type=form.type.data,
            length=form.length.data,
            taxonomy=form.taxonomy.data,
            clade1=form.clade1.data,
            clade2=form.clade2.data,
            clade3=form.clade3.data,
            clade4=form.clade4.data,
            clade5=form.clade5.data,
            named_by=form.named_by.data,
            species=form.species.data,
            link=form.link.data,
        )
        # Save the dinosaur to the database
        dinosaur.save()
        return redirect(url_for("homepage"))
    return render_template("create_dinosaur.html", form=form)


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

    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))

    PIE_LIM = 1.6

    # Set the extent to match the pie chart's unit circle
    ax.imshow(
        gradient,
        aspect="auto",
        cmap=plt.get_cmap("rainbow"),
        extent=(-PIE_LIM, PIE_LIM, -PIE_LIM, PIE_LIM),
        alpha=0.3,
    )

    pie, texts, autotexts = ax.pie(diet_count, labels=diets, autopct="%1.1f%%")

    ax.set_xlim(-PIE_LIM, PIE_LIM)
    ax.set_ylim(-PIE_LIM, PIE_LIM)

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
        path = "./downloads/dinosaur_data.csv"
    db_to_csv(path, query)
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
