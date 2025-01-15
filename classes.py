import os
import sqlite3
import requests
from wtforms import Form, FloatField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired


# listes des classes utilisées dans le programme

# SQL
class BDD():
    def __init__(self, db_path):
        """Initialisation de la base de donnée"""
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Connection à la base de donnée"""
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
                print("Connexion à la base de données établie.")
            except sqlite3.Error as e:
                print(f"Erreur lors de la connexion à la base de données: {e}")

    def close(self):
        """Fermer la connexion à la base de donnée"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Connexion à la base de données fermée.")

    def create_table(self, create_table_sql):
        """Créer une table dans la base de donnée"""
        self.connect()
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            self.connection.commit()
            print("Table créée avec succès.")
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de la table: {e}")

    def table_exists(self, table_name):
        """Vérifier l'existence d'une table dans la base de donnée"""
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone() is not None
        return exists

    def insert(self, table_name, columns, values):
        """Insérer dans une table dans une base de donnée"""
        self.connect()
        placeholders = ', '.join(['?'] * len(values))
        columns_str = ', '.join(columns)
        insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_sql, values)
            self.connection.commit()
            print("Données insérées avec succès.")
        except sqlite3.Error as e:
            print(f"Erreur lors de l'insertion des données: {e}")

    def db_exists(self):
        """Vérifie si la base de données existe"""
        return os.path.exists(self.db_path)

    def get_item(self, item_id):
        """Récupérer un item dans la base de donnée"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT link FROM Items WHERE Id=?", (item_id,))
        return cursor.fetchone()[0]

    def get_item_index(self, table="Items"):
        """Récupérer l'index du dernier item"""
        assert table in ["Items", "Scores"]
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT MAX(Id) FROM "+table)
        row = cursor.fetchone()
        return row[0]

    def get_scores(self, table="Scores"):
        """Récupérer les scores des joueurs"""
        assert table in ["Scores"]
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, NomItem, nom, score FROM "+table)
        return cursor.fetchall()

    def item_exists(self, link):
        """Vérifier si un item existe dans la base de donnée"""
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM Items WHERE link = ?", (link,))
        return cursor.fetchone() is not None


# API Amazon


class API:
    def __init__(self):
        self.link = ""
        self.title = ""
        self.images = []
        self.price = ""
        self.rating = ""

    def recupArticle(self, link=None):
        if link is None:
            link = self.link
        r = requests.get('http://ws.chez-wam.info/' + link)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error: {e}")
            return None
        data = r.json()  # Parse the JSON response
        self.link = link
        self.title = data.get("title", "Unknown Title")
        self.images = data.get('images', [])
        price = data.get('price', "Unknown Price")
        if price == None : price = "Unknown Price"
        price = price.replace("\u202f", "").replace("\u20ac", "").replace("€", "").replace(",", ".").replace(" ", "")
        if type(price) == str : self.price = price
        else : self.price = float(price)
        self.rating = data.get('rating', "Unknown Rating")
        data["link"] = link  # Ensure the link is included in the returned data
        return data

    def serialize(self):
        return {
            "link": self.link,
            "title": self.title,
            "images": self.images,
            "price": self.price,
            "rating": self.rating
        }

class GameForm(Form):
    price = FloatField('price', validators=[DataRequired()])

from wtforms import Form, StringField, validators

class ItemForm(Form):
    lien = StringField('Lien', validators=[validators.URL()])

class ScoreForm(Form):
    name = StringField('name', validators=[DataRequired()])