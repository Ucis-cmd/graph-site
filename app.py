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
app.jinja_env.filters["unquote"] = unquote  # Pārveido URL uz pareizo formātu
app.config["SECRET_KEY"] = "your_key"


def init_db():
    if not Dinosaur.table_exists():
        csv_to_db("./static/dist/csv/dinosaur_data.csv")


# Atlasa datus no datubāzes un atgriež tos sagrupētus pēc alfabēta
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

    alphabetical_groups = []
    for group in alphabetical_query:
        alphabetical_groups.append(
            {
                "first_letter": group.first_letter,
                "dinosaur_names": group.dinosaur_names.split(","),
                "dinosaur_links": group.dinosaur_links.split(","),
            }
        )
    return alphabetical_groups


# Atgriež kļūmes lapu, ja netiek atrasta neviena cita uz to saiti
@app.errorhandler(404)
def not_found(e):
    return render_template("404_page.html")


# Galvenā lapa
@app.route("/")
def homepage():

    # Atlasa dinozauru grupas un skaitu katrā
    query = (
        Dinosaur.select(Dinosaur.type, fn.COUNT(Dinosaur.name).alias("count"))
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

    # Nosaka fona krāsu
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))

    # Nosaka fona izmēru, lai sakristu ar grafika izmēriem
    x_min, x_max = -1, len(unique_types)
    y_min, y_max = 0, max(type_count) + 10

    # Attēlo fonu
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

        # Teksts, kas ir virs katra stabiņa
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 3,
            category,
            ha="center",
            va="top",
            color="black",
        )

        # Savieno ar izveidotu spraudni, kas iekrāso stabiņu, kad uz tā ir kursors un novirza uz citu saiti, ja uzklikšķina
        highlight = HighlightBarPlugin(bar, link)
        plugins.connect(plt.gcf(), highlight)

    ax.set_xlabel("Dinosaur types")
    ax.set_ylabel("Amount")

    # Noņem iedaļas no x ass
    ax.set_xticks([])

    # Saglabā grafiku kā HTML failu
    html_str = mpld3.fig_to_html(fig)
    with open("./templates/_types_hist.html", "w") as Html_file:
        Html_file.write(html_str)

    return render_template("base.html")


# Ļauj saglabāt jaunu dinozauru datubāzē, tad atgriež uz galveno lapu
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
        dinosaur.save()
        return redirect(url_for("homepage"))
    return render_template("create_dinosaur.html", form=form)


@app.route("/<type>")
def type_page(type):
    data_count = Dinosaur.select().where(Dinosaur.type == type).count()
    if data_count == 0:
        return render_template("404_page.html")

    # Atlasa dinozauru skaitu pēc diētas, kas ir tajā tipu grupā
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

    # Nosaka fona malas attālumu no centra
    PIE_LIM = 1.6

    # Attēlo fonu
    ax.imshow(
        gradient,
        aspect="auto",
        cmap=plt.get_cmap("rainbow"),
        extent=(-PIE_LIM, PIE_LIM, -PIE_LIM, PIE_LIM),
        alpha=0.3,
    )

    pie, texts, autotexts = ax.pie(diet_count, labels=diets, autopct="%1.1f%%")

    # Nosaka grafika izmērus, lai sakristu ar fonu
    ax.set_xlim(-PIE_LIM, PIE_LIM)
    ax.set_ylim(-PIE_LIM, PIE_LIM)

    # Savieno katru sektoru ar spraudni, kas iekrāso, kad uz tā ir kursors un novirza uz citu saiti, ja uzklikšķina
    for wedge, diet in zip(pie, diets):
        plugins.connect(fig, HighlightPiePlugin(wedge, f"/{type}/{diet}"))

    html_str = mpld3.fig_to_html(fig)
    with open("./templates/_diet_pie.html", "w") as Html_file:
        Html_file.write(html_str)

    return render_template(
        "type_page.html",
        type=type,
        alphabetical_groups=alphabetical_groups,
        zip=zip,
    )


# Atgriež lapu, kur ir noteikta tipa un diētas dinozauri
@app.route("/<type>/<diet>")
def type_diet_page(type, diet):
    data_count = (
        Dinosaur.select().where(Dinosaur.type == type, Dinosaur.diet == diet).count()
    )
    if data_count == 0:
        return render_template("404_page.html")

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


# Atgriež lejupielādētu csv failu, kurā ir pieprasītā tipa un diētas dinozauri
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
