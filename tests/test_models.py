# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from random import randint
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        new_product = Product.find(product.id)
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.id, product.id)

    def test_update_a_product(self):
        """It should update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        original_product_id = product.id
        fake_description = "fake description"
        product.description = "fake description"
        product.update()
        self.assertEqual(product.description, fake_description)
        new_product = Product.find(original_product_id)
        self.assertEqual(new_product.description, fake_description)

    def test_sad_path_update_a_product(self):
        """It should fail to update a product"""
        product = ProductFactory()
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_products(self):
        """It should list all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        # Create between 1 and 10 products
        number_products = randint(1, 10)
        fake_products = ProductFactory.create_batch(number_products)
        for k in fake_products:
            k.create()
        products = Product.all()
        self.assertEqual(len(products), number_products)

    def test_find_by_name(self):
        """It should find a product by its name"""
        fake_products = ProductFactory.create_batch(5)
        for k in fake_products:
            k.create()
        first_name_fake_products: str = fake_products[0].name
        same_name_products_number: int = len([k for k in fake_products if k.name == first_name_fake_products])
        database_products = Product.find_by_name(first_name_fake_products)
        self.assertEqual(database_products.count(), same_name_products_number)
        for k in database_products:
            self.assertEqual(k.name, first_name_fake_products)

    def test_find_by_availability(self):
        """It should find a product by its availability"""
        fake_products = ProductFactory.create_batch(10)
        for k in fake_products:
            k.create()
        availability: str = fake_products[0].available
        count: int = len([k for k in fake_products if k.available == availability])
        database_products = Product.find_by_availability(availability)
        self.assertEqual(database_products.count(), count)
        for k in database_products:
            self.assertEqual(k.available, availability)

    def test_find_by_category(self):
        """It should find a product by its category"""
        fake_products = ProductFactory.create_batch(10)
        for k in fake_products:
            k.create()
        category: str = fake_products[0].category
        count: int = len([k for k in fake_products if k.category == category])
        database_products = Product.find_by_category(category)
        self.assertEqual(database_products.count(), count)
        for k in database_products:
            self.assertEqual(k.category, category)

    def test_find_by_price(self):
        """It should find a product by its category"""
        fake_products = ProductFactory.create_batch(10)
        for k in fake_products:
            k.create()
        price: str = fake_products[0].price
        count: int = len([k for k in fake_products if k.price == price])
        database_products = Product.find_by_price(price)
        self.assertEqual(database_products.count(), count)
        for k in database_products:
            self.assertEqual(k.price, price)

        # Find by string price
        str_price = str(price)
        database_products = Product.find_by_price(str_price)
        self.assertEqual(database_products.count(), count)
        for k in database_products:
            self.assertEqual(k.price, Decimal(str_price))
