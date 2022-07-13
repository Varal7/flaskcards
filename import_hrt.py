from app import db, Card
import os
import shutil

filename = "/Users/varal7/Projects/hrt/faces/index.csv"
directory = "/Users/varal7/Projects/hrt/faces"
dest = "app/static/faces/"

with open(filename) as f:
    for line in f:
        name, role, url, filename = line.strip().split(",")
        if filename == "":
            continue
        shutil.copy(os.path.join(directory, filename), os.path.join(dest, filename + ".jpg"))
        card = Card(name=name, role=role, filename=filename + ".jpg")
        db.session.add(card)

db.session.commit()


