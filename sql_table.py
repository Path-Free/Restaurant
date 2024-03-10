import sqlite3 as sl

con = sl.connect('stolovka.db')

with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            login TEXT,
            password TEXT,
            last_address TEXT,
            is_admin INTEGER DEFAULT 0,
            email TEXT,
            tel INTEGER,
            tg_id INTEGER,
            vk_id INTEGER
        );
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS ORDERS (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date_time TEXT,
            status INTEGER DEFAULT 1
        );
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS CART (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            good_id INTEGER,
            count INTEGER,
            user_id INTEGER
        );
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS GOODS (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            description TEXT,
            category INTEGER
        );
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS CATEGORIES (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS STATUSES (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
    """)

sql_insert = "INSERT OR IGNORE INTO GOODS (id, name, price, description, category) values(?, ?, ?, ?, ?)"
with con:
    con.execute(sql_insert, [1, "Карпаччо из говядины", 20, "говяжья вырезка, "
                                                            "лимон, черри, пармезан, зелень", 1])
    con.execute(sql_insert, [2, "Мясная тарелка", 23, "грудинка копченая, колбаса с/к, ветчина, пряная буженина, "
                                                      "солёный огурец, маринованные томаты, гренки с чесноком, "
                                                      "айсберг, свежая зелень", 1])
    con.execute(sql_insert, [3, "Пряная буженина с маринадами", 15, "буженина запеченая из свинины, пряная морковь, "
                                                                    "солёный огурец, горчица, зелень", 1])
    con.execute(sql_insert, [4, "Овощное плато", 15, "огурец, томат, сладкий перец, черри, стебли сельдерея, айсберг, "
                                                     "маслины, оливки, ассорти из свежей зелени", 1])
    con.execute(sql_insert, [5, "Сырная палитра", 35, "сыр пармезан, сыр камамбер, сыр дор блю, брынза, моцарелла, "
                                                      "виноград, мед, гриссини с сезамом, мята, кунжут, "
                                                      "грецкий орех", 1])


sql_insert = "INSERT OR IGNORE INTO CATEGORIES (id, name) values(?, ?)"
with con:
    con.execute(sql_insert, [1, "Холодные закуски и салаты"])
    con.execute(sql_insert, [2, "Горячие закуски"])
    con.execute(sql_insert, [3, "Супы и пасты"])
    con.execute(sql_insert, [4, "Горячие блюда и гарниры"])
    con.execute(sql_insert, [5, "Десерты"])

sql_insert = "INSERT OR IGNORE INTO STATUSES (id, name) values(?, ?)"
with con:
    con.execute(sql_insert, [1, "в обработке"])
    con.execute(sql_insert, [2, "принят"])
    con.execute(sql_insert, [3, "курьер отправлен"])
    con.execute(sql_insert, [4, "доставлен"])

sql_insert = "INSERT OR IGNORE INTO USERS (id, login, password, last_address, is_admin, email, tel) values(?, ?, ?, ?, ?, ?, ?)"
with con:
    con.execute(sql_insert, [1, "OPENEWAY", "18062003", "Пугачевская 9", 1, "alex.pathfree@yandex.by", "+375334695200"])
    # executemany - для двумерного
    con.execute(sql_insert, [2, "Денис", "qweqwe", "Колотушкина 228", 0, "", ""])

with con:
    data = con.execute("SELECT * FROM STATUSES").fetchall()
    print(data)

    # data = con.execute("PRAGMA table_info(CLIENTS);").fetchall()
    # for x in data:
    #     print(x[1])