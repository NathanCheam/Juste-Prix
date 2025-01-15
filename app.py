import os

from flask import Flask, render_template, request, session, jsonify, url_for
from random import randint

import classes
from classes import GameForm, ItemForm, ScoreForm

import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def ini():
    bdd = classes.BDD("bdd.db")
    # Vérifier l'existence de la base de données
    if not bdd.db_exists(): create_bdd(bdd)
    # afficher le menu
    return menu()

@app.route('/menu')
def menu(msg = ""):
    bdd = classes.BDD("bdd.db")
    scores = bdd.get_scores()
    return render_template('menu.html', message=msg, scores=scores)

@app.route('/start')
def start():
    bdd = classes.BDD("bdd.db")
    session['in_game'] = True
    session['try'] = 0
    session['try_limit'] = 100
    session['link'], article = take_article(bdd)
    session['article_title'] = article["title"]
    session['article_price'] = article["price"]
    session['article_note'] = article["rating"]
    session['article_images'] = article["images"]
    session['difficulty'] = request.args.get('difficulty', 'facile')
    if session['difficulty'] == 'facile':
        session['try_limit'] = 40
    elif session['difficulty'] == 'normal':
        session['try_limit'] = 20
    elif session['difficulty'] == 'difficile':
        session['try_limit'] = 10
    session['tries'] = []
    print("Article à deviner: ", session['article_title'], session['article_price'])

    return play()

@app.route('/play', methods=['GET', 'POST'])
def play():
    if not session.get('in_game'):
        return menu()

    msg = ""
    form = GameForm(request.form)
    if request.method == 'POST' and form.validate():
        # gestion des tentatives
        session['try'] += 1
        if session['try'] > session['try_limit']:
            return jsonify({'message': "Perdu..."})

        # récupération du prix entré par l'utilisateur
        try:
            price = float(form.price.data)
        except ValueError:
            msg = "Veuillez entrer un nombre valide."
            return jsonify({'message': msg})

        # récupération du prix de l'article
        s_price_str = session['article_price'].replace(",", ".").replace(" ", "").replace("€", "")
        s_price_str = s_price_str.replace("\u202f", "")  # Remove non-breaking space
        try:
            s_price = float(s_price_str)
        except ValueError:
            msg = "Erreur de conversion du prix de l'article."
            return jsonify({'message': msg})

        # vérification si le prix a déjà été essayé
        if price in session['tries']:
            print("Prix déjà essayé: ", price)
            msg = "Vous avez déjà essayé ce prix."
            session['try'] -= 1
        else:
            session['tries'].append(price)

            # Comparaison des prix
            if s_price == price: return jsonify({'redirect': url_for('score')})
            else:
                if s_price > price: msg = "C'est plus cher..."
                elif s_price < price: msg = "C'est moins cher..."
    else:
        msg = "Tentez..."

    msg = msg + " " + str(session['try']) + "/" + str(session['try_limit'])

    if request.method == 'POST':
        return jsonify({'message': msg})

    return render_template('play.html', message=msg, nom=session['article_title'], images=session['article_images'], note=session['article_note'])


@app.route('/save', methods=['GET', 'POST'])
def score():
    if session is None:
        return menu()

    form = ScoreForm(request.form)
    if request.method == 'POST' and form.validate():
        print("POST")
        name = str(form.name.data)
        bdd = classes.BDD("bdd.db")
        id= bdd.get_item_index("Scores")
        if (id == None): id = 0
        else: id += 1
        bdd.insert("Scores", ["Id", "nom", "NomItem", "Item", "score"], [id, name, extract_product_name(session["article_title"]), session["article_title"], session['try']])
        session.clear()
        return menu("Score enregistré avec succès.")

    return render_template('save.html', tries=session['try'])


@app.route('/add-item', methods=['GET', 'POST'])
def addItem():
    form = ItemForm(request.form)
    if request.method == 'POST':
        if 'link' in request.form and request.form['link']:
            link = request.form['link']
            bdd = classes.BDD("bdd.db")
            if bdd.item_exists(link):
                return render_template("menu.html", message="L'article existe déjà dans la base de données.")
            bdd.insert("Items", ["link"], [link])
            return render_template("menu.html", message="Article ajouté avec succès")
        elif form.validate():
            url = form.lien.data
            try:
                start = url.index('/dp/') + len('/dp/')
                end = url.find('/', start)
                if end == -1:
                    end = len(url)
                code = url[start:end]
            except ValueError:
                return render_template('ajout-item.html', form=form, message="URL invalide")

            api = classes.API()
            item = api.recupArticle(code)
            bdd = classes.BDD("bdd.db")

            while item is None or item.get("title") is None:
                item = api.recupArticle(code)

            if item is None:
                return render_template('ajout-item.html', form=form, message="L'article n'a pas été trouvé")

            if bdd.item_exists(code):
                return render_template('ajout-item.html', form=form,
                                       message="L'article existe déjà dans la base de données.")

            bdd.insert("Items", ["link"], [code])
            return render_template('confirm_ajout.html', item=item)
        else:
            return render_template('ajout-item.html', form=form, message="This field is required.")

    return render_template('ajout-item.html', form=form)


def extract_product_name(full_name):
    pattern = r"^(.*? -)"
    match = re.match(pattern, full_name)
    if match:
        return match.group(1).strip(" -")
    return full_name

# Fonction pour prendre un article aléatoire
def take_article(bdd):
    index = randint(0, bdd.get_item_index())
    link = bdd.get_item(index)
    api = classes.API()
    article = api.recupArticle(link)

    while article["title"] is None:

        index = randint(0, bdd.get_item_index())
        link = bdd.get_item(index)
        article = api.recupArticle(link)

    if article is None:
        print("Aucun article trouvé après plusieurs tentatives.")
        return None, None

    return link, article

def create_bdd(bdd):
    assert isinstance(bdd, classes.BDD)
    print("Initialisation...")
    # Création de la table "Items"
    bdd.create_table("""
            CREATE TABLE IF NOT EXISTS Items (
                Id integer PRIMARY KEY,
                link string NOT NULL
            );""")
    # Création de la table "Scores"
    bdd.create_table("""
            CREATE TABLE Scores (
                Id INTEGER PRIMARY KEY, 
                nom TEXT,
                NomItem TEXT, 
                Item INTEGER, 
                score INTEGER,
                FOREIGN KEY(Item) REFERENCES Items(Id)
            )
        """)
    # Insertion de données dans la table "Items"
    bdd.insert("Items", ["Id", "link"], [0, "B0CQMFJ888"])
    bdd.insert("Items", ["Id", "link"], [1, "B0BBPZNXR1"])


if __name__ == '__main__':
    app.run()
