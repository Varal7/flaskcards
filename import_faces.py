from app import db, Card
import os
import shutil

filename = "/Users/varal7/Downloads/celeba/img_names.txt"
directory = "/Users/varal7/Downloads/celeba/img_align_celeba"
dest = "app/static/faces/"

with open(filename) as f:
    for line in f:
        a, b = line.strip().split(" ")
        shutil.copy(os.path.join(directory, a), os.path.join(dest, a))
        card = Card(name=b, filename=a)
        db.session.add(card)

db.session.commit()


