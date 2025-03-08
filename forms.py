from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, Optional


# Dinozauru anketa
class DinosaurForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])

    diet = SelectField(
        "Diet",
        choices=[
            ("carnivore", "Carnivore"),
            ("herbivore", "Herbivore"),
            ("omnivore", "Omnivore"),
            ("unknown", "Unknown"),
        ],
        validators=[DataRequired()],
    )

    period = StringField("Period", validators=[DataRequired()])
    period_name = StringField("Period Name", validators=[DataRequired()])
    lived_in = StringField("Lived In", validators=[DataRequired()])

    type = SelectField(
        "Type",
        choices=[
            ("armoured dinosaur", "Armoured Dinosaur"),
            ("ceratopsian", "Ceratopsian"),
            ("euornithopod", "Euornithopod"),
            ("large theropod", "Large Theropod"),
            ("sauropod", "Sauropod"),
            ("small theropod", "Small Theropod"),
        ],
        validators=[DataRequired()],
    )

    length = FloatField("Length", validators=[Optional()])
    taxonomy = TextAreaField("Taxonomy", validators=[DataRequired()])
    clade1 = StringField("Clade 1", validators=[DataRequired()])
    clade2 = StringField("Clade 2", validators=[DataRequired()])
    clade3 = StringField("Clade 3", validators=[DataRequired()])
    clade4 = StringField("Clade 4", validators=[DataRequired()])
    clade5 = StringField("Clade 5", validators=[DataRequired()])
    named_by = StringField("Named By", validators=[DataRequired()])
    species = StringField("Species", validators=[DataRequired()])
    link = StringField("Link", validators=[DataRequired()])
    submit = SubmitField("Create Dinosaur")
