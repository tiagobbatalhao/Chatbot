#!/usr/bin/python
# coding: iso-8859-1

import os
import sys
import json
from datetime import datetime
import os
import urlparse
import psycopg2
from psycopg2 import sql

def connect_database():
    """
    Connect to a Postgres database on Heroku server
    """
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    connection = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return connection

def check_database():
    """
    Check the status of the database
    """
    database = connect_database()
    cursor = database.cursor()
    execution = cursor.execute("""SELECT * FROM messages ;""")
    messages = cursor.fetchall()
    execution = cursor.execute("""SELECT * FROM attachments ;""")
    attachments = cursor.fetchall()
    execution = cursor.execute("""SELECT * FROM users ;""")
    users = cursor.fetchall()
    execution = cursor.execute("""SELECT * FROM products ;""")
    products = cursor.fetchall()
    execution = cursor.execute("""SELECT * FROM cart ;""")
    cart = cursor.fetchall()
    output = 'Checking database...'
    output+= '\n\nRetrieved {} messages.'.format(len(messages))
    output+= '\n\nRetrieved {} attachments.'.format(len(attachments))
    output+= '\n\nRetrieved {} users.'.format(len(users))
    output+= '\n\nRetrieved {} products.'.format(len(products))
    output+= '\n\nRetrieved {} items in cart.'.format(len(cart))
    print(users)
    return output, 200

def create_table_messages():
    """
    Create a table to store received messages
    """
    command = sql.SQL(u"""
                CREATE TABLE messages (
                    id_message varchar(64) PRIMARY KEY,
                    id_sender varchar(64),
                    id_recipient varchar(64),
                    message_text text,
                    timestamp bigint,
                    seq integer,
                    quickreply_payload text
                );
                """)
    database = connect_database()
    cursor = database.cursor()
    execution = cursor.execute(command)
    database.commit()
    cursor.close()
    database.close()
    return 'OK', 200

def create_table_attachments():
    """
    Create a table to store attachments
    """
    command = sql.SQL(u"""
                CREATE TABLE attachments (
                    id_message varchar(64) REFERENCES messages,
                    type varchar(64),
                    url text,
                    coordinates_lat numeric,
                    coordinates_lon numeric,
                    title text
                );
                """)
    database = connect_database()
    cursor = database.cursor()
    execution = cursor.execute(command)
    database.commit()
    cursor.close()
    database.close()
    return 'OK', 200

def create_table_users():
    """
    Create a table to store information about users
    """
    command = sql.SQL(u"""
                CREATE TABLE users (
                    id varchar(64) PRIMARY KEY,
                    first_name text,
                    last_name text,
                    profile_pic text,
                    gender varchar(16),
                    locale varchar(16),
                    timezone integer
                );
                """)
    database = connect_database()
    cursor = database.cursor()
    execution = cursor.execute(command)
    database.commit()
    cursor.close()
    database.close()
    return 'OK', 200

def create_table_products():
    """
    Create a table to store information about products
    """
    command = sql.SQL(u"""
                CREATE TABLE products (
                    id varchar(64) PRIMARY KEY,
                    category text,
                    name text,
                    description text,
                    image_url text,
                    options text,
                    price numeric
                );
                """)
    database = connect_database()
    cursor = database.cursor()
    execution = cursor.execute(command)
    database.commit()
    cursor.close()
    database.close()
    return 'OK', 200

def create_table_cart():
    """
    Create a table to store information about products
    """
    command = sql.SQL(u"""
                CREATE TABLE cart (
                    id_purchase varchar(64) PRIMARY KEY,
                    id_product varchar(64) REFERENCES products,
                    option text,
                    quantity integer,
                    unit_price numeric,
                    id_user varchar(64) REFERENCES users,
                    timestamp bigint
                );
                """)
    database = connect_database()
    cursor = database.cursor()
    execution = cursor.execute(command)
    database.commit()
    cursor.close()
    database.close()
    return 'OK', 200

def delete_table(table_name = None):
    """
    Delete a table
    """
    if table_name == None:
        table_name = request.args.get('table')
    if table_name:
        command = sql.SQL(u"""
                    DROP TABLE IF EXISTS {};
                    """).format(sql.Identifier(table_name))
        database = connect_database()
        cursor = database.cursor()
        execution = cursor.execute(command)
        database.commit()
        cursor.close()
        database.close()
        return 'Deleted table {}'.format(table_name), 200
    return 'Nothing to delete', 200

def reset_database():
    """
    One-time setup of the database
    """
    delete_table('cart')
    delete_table('products')
    delete_table('users')
    delete_table('attachments')
    delete_table('messages')
    create_table_messages()
    create_table_attachments()
    create_table_users()
    create_table_products()
    create_table_cart()
    return 'OK', 200
