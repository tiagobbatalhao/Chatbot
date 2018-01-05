#!/usr/bin/python
# coding: iso-8859-1

import json,csv
import time
import app
import setup_database
import psycopg2
from psycopg2 import sql
from numpy.random import randint,choice

url_AWSbucket = 'https://s3-ap-southeast-1.amazonaws.com/tiagobbatalhao-chatbot/'

def persistent_menu():
    """
    Facebook payload to set up a persistent menu for a chatbot
    """
    main = []
    main.append(
        {'title': 'Olá!',
        'type': 'postback',
        'payload': 'welcome_message'}
    )
    main.append({
        'title': 'Procurar',
        'type': 'nested',
        'call_to_actions': [
            {'title': 'Camisetas',
            'type': 'postback',
            'payload': 'search-camisetas'}
        ]
    })
    main.append(
        {'title': 'Carrinho',
        'type': 'postback',
        'payload': 'view_cart'}
    )
    menu = {}
    menu['locale'] = 'default'
    menu['composer_input_disabled'] = False
    menu['call_to_actions'] = main
    return menu

def get_started():
    """
    Message to send to app when user clicks on 'Start' button.
    """
    return {'payload':'welcome_message'}

def setup_persistent_menu():
    """
    Return the Facebook payload required to set up app configurations.
    """
    menu = persistent_menu()
    start = get_started()
    data = {'get_started':start,'persistent_menu':[menu]}
    return data

def answer(message,sender_info):
    """
    Answer a message from user.
    Reply with a welcome message if the user has not sent a message
    in the last 24 hours.
    """
    sender_id = sender_info.get('id')
    time_since = time_since_last_message(sender_id)
    if time_since == None or time_since > 24*3600*1000:
        welcome_message(message, sender_info)
    else:
        pass

def welcome_message(message, sender_info = None, *args, **kwargs):
    """
    Sends a welcome message to the user.
    """
    if sender_info == None:
        sender_id = message.get('sender',{}).get('id')
        sender_info = app.get_user_information(sender_id)
    else:
        sender_id = sender_info.get('id')
    first_name = sender_info.get('first_name','')
    last_name = sender_info.get('last_name','')
    sender_name = u'{} {}'.format(first_name,last_name)
    sender_gender = sender_info.get('gender','male')
    welcome = 'bem-vindo' if sender_gender=='male' else 'bem-vinda'

    reply = u'Olá {}, {} a minha lojinha online!\n'.format(sender_name,welcome)
    reply += u'Aqui você pode encontrar camisetas de várias cores e tamanhos.\n'

    # time_since = time_since_last_message(sender_id)
    # if time_since is None:
    #     message += u'Essa é sua primeira mensagem!'
    # else:
    #     time_since = int( time_since / 1000.)
    #     message += u'Você não volta aqui há {} segundos'.format(time_since)

    quick_replies = [
        {'content_type': 'text',
        'title': 'Mostre-me camisetas.',
        'payload': 'search-camisetas'},
        {'content_type': 'text',
        'title': 'Quem somos?',
        'payload': 'who_we_are'}
    ]
    data = json.dumps({
        'messaging_type':'RESPONSE',
        'recipient': {'id': sender_id},
        'message': {'text': reply, 'quick_replies': quick_replies}
    },encoding='iso-8859-1')
    app.send_api(data)

def who_we_are(message, sender_info, payload):
    """
    This is called when the user wants to know about the store.
    """
    sender_id = message.get('sender',{}).get('id')
    sender_info = app.get_user_information(sender_id)
    first_name = sender_info.get('first_name','')
    last_name = sender_info.get('last_name','')
    sender_name = u'{} {}'.format(first_name,last_name)
    sender_gender = sender_info.get('gender','male')
    reply = u'Obrigado pelo interesse!'
    reply+= u' Esse bot foi desenvolvido por Tiago Batalhão'
    reply+= u' para aprender mais sobre como funcionam os bots de Messenger.'
    attach = {'type': 'image','payload':{'attachment_id': app.profile_photo_id}}
    data = json.dumps({
        'messaging_type':'RESPONSE',
        'recipient': {'id': sender_id},
        'message': {'text': reply}
    },encoding='iso-8859-1')
    app.send_api(data)
    quick_replies = [
        {'content_type': 'text',
        'title': 'Voltar ao menu.',
        'payload': 'welcome_message'}
    ]
    data = json.dumps({
        'messaging_type':'RESPONSE',
        'recipient': {'id': sender_id},
        'message': {'attachment': attach, 'quick_replies': quick_replies}
    },encoding='iso-8859-1')
    app.send_api(data)


def time_since_last_message(sender_id):
    """
    Return the time since the user's last message.
    """
    query = sql.SQL(u"""
        SELECT timestamp FROM messages
        WHERE id_sender = %s
        ORDER BY timestamp DESC
    ; """)
    database = setup_database.connect_database()
    cursor = database.cursor()
    try:
        execution = cursor.execute(query,[sender_id])
        for i in range(2):
            # I want the second-to-last message
            result = cursor.fetchone()
    except AttributeError:
        result = None
    if result is None:
        return None
    timestamp_current = int(1000*time.time())
    since = timestamp_current - result[0]
    return since

def search(message, sender_info, payload):
    """
    This is called when the user searches for a product category.
    """
    return search_product(message,payload[0])

def search_product(message, name):
    """
    Show a caroussel of available products.
    """
    # Find products
    query = sql.SQL(u"""
        SELECT *
        FROM products
        WHERE category = %s ;
    """)
    database = setup_database.connect_database()
    cursor = database.cursor()
    try:
        execution = cursor.execute(query,[name])
        result = cursor.fetchall()
    except AttributeError:
        result = None

    if len(result):
        reply = u'Legal que você está procurando por {}! '.format(name)
        reply+= u'Nós temos alguns modelos disponíveis.'
    else:
        reply = u'Infelizmente não temos o que você procura: {}'.format(name)

    sender_id = message.get('sender',{}).get('id')
    data = json.dumps({
        'messaging_type':'RESPONSE',
        'recipient': {'id': sender_id},
        'message': {'text': reply}
    },encoding='iso-8859-1')
    app.send_api(data)

    if len(result):
        template = {}
        template['type'] = 'template'
        template['payload'] = {}
        template['payload']['template_type'] = 'generic'
        template['payload']['sharable'] = False
        template['payload']['image_aspect_ratio'] = 'square'
        indices = choice(range(len(result)),size=3,replace=False)
        choose = [result[x] for x in indices]
        elements = []
        for product in choose:
            elements.append(gen_product_template(product))
        template['payload']['elements'] = elements

        data = json.dumps({
            u'messaging_type':u'RESPONSE',
            u'recipient': {u'id': sender_id},
            u'message': {u'attachment': template}
        },encoding='iso-8859-1')
        app.send_api(data)

    cursor.close()
    database.close()

def convert_to_iso(string):
    """
    Convert a UTF-8 string to ISO-8859-1.
    """
    return string.decode('utf-8').encode('iso-8859-1')

def gen_product_template(product):
    """
    Create a generic template element for a product.
    """
    element = {}
    element['title'] = convert_to_iso(product[2])
    element['subtitle'] = convert_to_iso(product[3])
    element['subtitle']+= convert_to_iso(u'\nPor apenas R$ {:.2f}'.format(product[6]).replace('.',','))
    element['image_url'] = url_AWSbucket + product[4]
    element['buttons'] = [{
        'type': 'postback',
        'title': 'Tenho interesse',
        'payload': 'interested-{}'.format(product[0])
    }]
    return element

def products_available():
    """
    ONLY FOR TESTING.
    Populate the 'products' table from a CSV file
    """
    products = []
    with open('Products.csv','r') as file_object:
        reader = csv.reader(file_object)
        for row in reader:
            row = [unicode(x,'utf-8') for x in row]
            products.append(row)
    description = products.pop(0)
    id_digits = 9
    for product in products:
        product_id = str(randint(0,10**id_digits)).zfill(id_digits)
        params = [product_id] + product
        blanks = sql.SQL(u' , ').join([sql.SQL(u'%s')]*len(params))
        command = sql.SQL(u"""
            INSERT INTO products VALUES ( {} );
        """).format(blanks)
        database = setup_database.connect_database()
        cursor = database.cursor()
        try:
            execution = cursor.execute(command,params)
            database.commit()
        except psycopg2.IntegrityError:
            pass
        cursor.close()
        database.close()

def interested(message, sender_info, payload):
    """
    This is called when the user shows interest in a product.
    """
    query = sql.SQL(u"""
        SELECT *
        FROM products
        WHERE id = %s ;
    """)
    database = setup_database.connect_database()
    cursor = database.cursor()
    try:
        execution = cursor.execute(query,[payload[0]])
        result = cursor.fetchone()
    except AttributeError:
        result = None

    if len(payload)==1:
        return ask_for_options(message,payload,result)
    elif len(payload)>1:
        return add_to_cart(message,payload,result)


def capitalize_first(string):
    """
    Capitalize the first letter of a string.
    """
    return string[0].upper() + string[1:]

def ask_for_options(message,payload,result):
    """
    When user has shown interest in a product, ask for product options.
    Example: size of a shirt.
    """
    reply = u'Você se interessou por {}!'.format(convert_to_iso(result[2].lower()))
    reply+= u'\nTemos algumas opções adicionais para esse produto'
    reply+= u'\nQueremos saber como você quer seu produto.'
    sender_id = message.get('sender',{}).get('id')
    data = json.dumps({
        'messaging_type':'RESPONSE',
        'recipient': {'id': sender_id},
        'message': {'text': reply}
    },encoding='iso-8859-1')
    app.send_api(data)

    options_dict = json.loads(convert_to_iso(result[5]),encoding='iso-8859-1')
    # This version only works well if there is only one type of option
    for name,options in options_dict.items():
        elements = []
        for option in options:
            element = {}
            element['title'] = capitalize_first(u'{} {}'.format(name,option))
            element['subtitle'] = u''
            element['buttons'] = [{
                'type':'postback',
                'title': u'Quero esse!',
                'payload': u'interested-{}-{}={}'.format(u'-'.join(payload),name,option)
            }]
            elements.append(element)
        payload = {}
        payload['template_type'] = 'list'
        payload['top_element_style'] = 'compact'
        payload['elements'] = elements[:4]
        template = {}
        template['type'] = 'template'
        template['payload'] = payload
        data = json.dumps({
            'messaging_type':'RESPONSE',
            'recipient': {'id': sender_id},
            'message': {'attachment': template}
        },encoding='iso-8859-1')
        app.send_api(data)

def add_to_cart(message, payload, product_info):
    """
    Add a product to cart.
    """
    product_id = payload[0]
    option = payload[1]
    client_id = message.get('sender',{}).get('id')
    timestamp_current = int(1000 * time.time())
    # Create an id for a purchase
    purchase_id = str(randint(0,10**12)).zfill(12)
    params = [
        purchase_id,
        product_id,
        option,
        1,
        product_info[6],
        client_id,
        timestamp_current
    ]
    blanks = sql.SQL(u' , ').join([sql.SQL(u'%s')]*len(params))
    command = sql.SQL(u"""
        INSERT INTO cart VALUES ( {} );
        """).format(blanks)
    database = setup_database.connect_database()
    cursor = database.cursor()
    try:
        execution = cursor.execute(command,params)
        database.commit()
    except psycopg2.IntegrityError:
        pass
    cursor.close()
    database.close()
    product_name = product_info[2]
    option = u'{} {}'.format(*payload[1].split('='))
    reply = u'Produto adicionado ao carrinho: {}, {}.'.format(product_name,option)
    quick_replies = [
        {'content_type': 'text',
        'title': 'Comprar mais',
        'payload': 'search-camisetas'},
        {'content_type': 'text',
        'title': 'Ver carrinho',
        'payload': 'view_cart'},
    ]
    data = json.dumps({
        'messaging_type':'RESPONSE',
        'recipient': {'id': client_id},
        'message': {'text': reply, 'quick_replies': quick_replies}
    },encoding='iso-8859-1')
    app.send_api(data)

def view_cart(message, sender_info, payload):
    """
    This is called when the user wants to view their items in cart
    """

    # Delete items (from all users) added more than one hour ago
    params = [int(1000*time.time()) - 3600000]
    command = sql.SQL(u"""
        DELETE FROM cart
        WHERE timestamp < %s ;
        """)
    database = setup_database.connect_database()
    cursor = database.cursor()
    try:
        execution = cursor.execute(command,params)
        database.commit()
    except psycopg2.ProgrammingError:
        pass
    cursor.close()
    database.close()

    # Find items bought by user
    query = sql.SQL(u"""
        SELECT
            cart.id_purchase,
            cart.id_product,
            products.name,
            products.image_url,
            products.options,
            cart.option,
            cart.quantity,
            cart.unit_price,
            cart.id_user,
            cart.timestamp
        FROM cart INNER JOIN products
        ON cart.id_product = products.id
        WHERE cart.id_user = %s ;
    """)
    database = setup_database.connect_database()
    cursor = database.cursor()
    sender_id = message.get('sender',{}).get('id')
    try:
        execution = cursor.execute(query,[sender_id])
        cart = cursor.fetchall()
    except AttributeError:
        cart = None

    total_items = len(cart)

    if total_items==0:
        # If user has bought nothing
        reply = u'O seu carrinho está vazio.'
        quick_replies = [
            {'content_type': 'text',
            'title': 'Mostre-me camisetas.',
            'payload': 'search-camisetas'},
        ]
        data = json.dumps({
            'messaging_type':'RESPONSE',
            'recipient': {'id': sender_id},
            'message': {'text': reply, 'quick_replies': quick_replies}
        },encoding='iso-8859-1')
        app.send_api(data)

    else:
        # If user has bought something, show a summary of his purchase
        word_item = 'item' if total_items==1 else 'itens'
        reply = u'Há {} {} no seu carrinho.'.format(total_items,word_item)
        total_price = sum([item[6]*item[7] for item in cart])
        reply+= u' O preço total é R$ {:.2f}'.format(total_price).replace('.',',') + u'.'
        data = json.dumps({
            'messaging_type':'RESPONSE',
            'recipient': {'id': sender_id},
            'message': {'text': reply}
        },encoding='iso-8859-1')
        app.send_api(data)

        # Show a list of items that the user has in his cart
        # Unfortunately, Facebook doesn't allow one-element lists
        elements = []

        options_clause = u''
        for option in item[5].split('-'):
            name, value = option.split(u'=')[0:2]
            options_clause += u'\n{}: {}'.format(capitalize_first(name),value)

        for item in cart:
            element = {}
            element['title'] = capitalize_first(u'{}'.format(item[2]))
            element['subtitle'] = u'Quantidade: {}'.format(item[6])
            element['subtitle']+= options_clause
            element['subtitle']+= u'\nPreço unitário: R$ {:.2f}'.format(item[7]).replace('.',',')
            element['image_url'] = url_AWSbucket + item[3]
            element['buttons'] = [
                {'type':'postback',
                'title': u'Remover',
                'payload': u'remove_from_cart-one-{}'.format(item[0])}
            ]
            elements.append(element)
        elements.append(
            {'title': u'Preço total: R$ {:.2f}'.format(total_price).replace('.',','),
            'subtitle': u'Total de itens: {}'.format(total_items),
            'buttons': [
                {'type': 'postback',
                'title': 'Limpar carrinho',
                'payload': 'remove_from_cart-all-{}'.format(item[8])}
            ]}
        )

        # If the number of items is even, separate in lists of 2
        # If the number is odd, the first list has 3 elements instead
        separate_lists = []
        if len(elements) % 2 == 0:
            separate_lists.append([elements.pop(0),elements.pop(0)])
        else:
            separate_lists.append([elements.pop(0),elements.pop(0),elements.pop(0)])
        while len(elements):
            separate_lists.append([elements.pop(0),elements.pop(0)])

        payload = {}
        payload['template_type'] = 'list'
        payload['top_element_style'] = 'compact'
        template = {}
        template['type'] = 'template'

        for each_list in separate_lists:
            payload['elements'] = each_list
            template['payload'] = payload
            data = json.dumps({
                'messaging_type':'RESPONSE',
                'recipient': {'id': sender_id},
                'message': {'attachment': template}
            },encoding='iso-8859-1')
            app.send_api(data)

        reply = u'Você gostaria de finalizar sua compra?'
        quick_replies = [
            {'content_type': 'text',
            'title': 'Comprar',
            'payload': 'buy'},
            {'content_type': 'text',
            'title': 'Ver mais camisetas',
            'payload': 'search-camisetas'},
        ]
        data = json.dumps({
            'messaging_type':'RESPONSE',
            'recipient': {'id': sender_id},
            'message': {'text': reply, 'quick_replies': quick_replies}
        },encoding='iso-8859-1')
        app.send_api(data)

def remove_from_cart(message, sender_info, payload):
    """
    This is called when the user wants to remove an item from cart
    or clean the cart entirely.
    """
    if payload[0] == 'all':
        command = sql.SQL(u"""
            DELETE FROM cart
            WHERE id_user = %s ;
            """)
        database = setup_database.connect_database()
        cursor = database.cursor()
        try:
            execution = cursor.execute(command,[payload[1]])
            database.commit()
        except psycopg2.ProgrammingError:
            pass
        cursor.close()
        database.close()

        reply = u'Seu carrinho agora está limpo.'
        data = json.dumps({
            'messaging_type':'RESPONSE',
            'recipient': {'id': message.get('sender',{}).get('id')},
            'message': {'text': reply}
        },encoding='iso-8859-1')
        app.send_api(data)

    elif payload[0] == 'one':
        command = sql.SQL(u"""
            DELETE FROM cart
            WHERE id_purchase = %s ;
            """)
        database = setup_database.connect_database()
        cursor = database.cursor()
        try:
            execution = cursor.execute(command,[payload[1]])
            database.commit()
        except psycopg2.ProgrammingError:
            pass
        cursor.close()
        database.close()

        reply = u'Produto removido do carrinho.'
        data = json.dumps({
            'messaging_type':'RESPONSE',
            'recipient': {'id': message.get('sender',{}).get('id')},
            'message': {'text': reply}
        },encoding='iso-8859-1')
        app.send_api(data)

def buy(message, sender_info, payload):
    """
    This is called when the user wants to finish buying.
    """
    first_name = sender_info.get('first_name','')
    last_name = sender_info.get('last_name','')
    sender_name = u'{} {}'.format(first_name,last_name)
    sender_gender = sender_info.get('gender','male')

    reply = u'Obrigado {} por comprar conosco!'.format(first_name)
    reply+= u' Agora vamos redirecionar você para o site da nossa loja.'
    data = json.dumps({
        'messaging_type':'RESPONSE',
        'recipient': {'id': message.get('sender',{}).get('id')},
        'message': {'text': reply}
    },encoding='iso-8859-1')
    app.send_api(data)

    pronoum = 'lo' if sender_gender == 'male' else 'la'
    reply = u'Infelizmente nosso site ainda está em construção.'
    reply+= u' Ficaremos felizes em atendê-{} você quando o site estiver pronto.'.format(pronoum)
    data = json.dumps({
        'messaging_type':'RESPONSE',
        'recipient': {'id': message.get('sender',{}).get('id')},
        'message': {'text': reply}
    },encoding='iso-8859-1')
    app.send_api(data)

    # Remove all items from cart if user decided to buy
    remove_from_cart(message, sender_info, ['all',sender_info.get('id')])
