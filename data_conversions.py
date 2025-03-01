import pandas as pd
from models import Dinosaur, initialize_db


def csv_to_db(csv_file_path):

    df = pd.read_csv(csv_file_path)

    initialize_db()

    for _, row in df.iterrows():
        Dinosaur.create(
            name=row["name"],
            diet=row["diet"],
            period=row["period"],
            period_name=row["period name"],
            lived_in=row["lived_in"],
            type=row["type"],
            length=row["length"],
            taxonomy=row["taxonomy"],
            clade1=row["clade1"],
            clade2=row["clade2"],
            clade3=row["clade3"],
            clade4=row["clade4"],
            clade5=row["clade5"],
            named_by=row["named_by"],
            species=row["species"],
            link=row["link"],
        )

    print("Data imported successfully!")


def db_to_csv(csv_file_path, query):
    data = [
        {
            "name": dino.name,
            "diet": dino.diet,
            "period": dino.period,
            "period_name": dino.period_name,
            "lived_in": dino.lived_in,
            "type": dino.type,
            "length": dino.length,
            "taxonomy": dino.taxonomy,
            "clade1": dino.clade1,
            "clade2": dino.clade2,
            "clade3": dino.clade3,
            "clade4": dino.clade4,
            "clade5": dino.clade5,
            "named_by": dino.named_by,
            "species": dino.species,
            "link": dino.link,
        }
        for dino in query
    ]

    df = pd.DataFrame(data)

    df.to_csv(csv_file_path, index=False)
