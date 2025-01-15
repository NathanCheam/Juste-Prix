import os
import unittest

from classes import BDD, API


class MyTestCase(unittest.TestCase):
    # SQL
    def setUp(self):
        """Initialisation de la BDD"""
        self.db_path = 'base.db'
        self.bdd = BDD(self.db_path)
        self.bdd.connect()

    def test_db_exists(self):
        """Test de l'existence de la base de données"""
        self.assertTrue(self.bdd.db_exists())


    def test_create_table(self):
        """Test de la création d'une table"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS Items (
            Id integer PRIMARY KEY,
            link string NOT NULL
        );"""
        self.bdd.create_table(create_table_sql)
        self.assertTrue(self.bdd.table_exists('Items'))

    def test_insert_get_item_index(self):
        """Test de l'insertion de données dans une table"""
        self.bdd.insert('Items', ['Id', 'link'], [1, 'https://www.google.com'])
        # récupérer l'item inséré
        row = self.bdd.get_item(1)
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'https://www.google.com')
        print(row[0])
        # récupérer l'index du dernier item
        index = self.bdd.get_item_index()
        self.assertEqual(index, 1)

    # API Amazon
    #test qui renvoie vrai
    def test_recupArticle(self):
        article = API()
        article.recupArticle("B08T1HR5CS")
        self.assertEqual(article.title,"HP 305 Pack de 2 Cartouches d'Encre Noire et Trois Couleurs Authentiques (6ZD17AE)")

    # Formulaire


if __name__ == '__main__':
    unittest.main()
