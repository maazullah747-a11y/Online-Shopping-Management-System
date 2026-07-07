import sqlite3

# Connect to Database
conn = sqlite3.connect("shopping.db")
cursor = conn.cursor()

# Create Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Create Products Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price INTEGER
)
""")

conn.commit()

# Add Products Only Once
cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]

if count == 0:
    total_products = int(input("How many products do you want to add? "))

    for i in range(total_products):
        print(f"\nEnter Details of Product {i + 1}")

        product_name = input("Product Name: ")
        product_price = int(input("Product Price: "))

        cursor.execute(
            "INSERT INTO products(name,price) VALUES(?,?)",
            (product_name, product_price)
        )

    conn.commit()


# ---------------- USER CLASS ----------------

class User:

    def register(self):

        username = input("Enter Username: ")
        password = input("Enter Password: ")

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()
            print("\nRegistration Successful!\n")

        except sqlite3.IntegrityError:
            print("\nUsername already exists!\n")

    def login(self):

        username = input("Enter Username: ")
        password = input("Enter Password: ")

        # Admin Login
        if username == "admin" and password == "admin":
            admin_menu()
            return

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:
            customer_menu(username)
        else:
            print("\nInvalid Username or Password!\n")


# ---------------- VIEW PRODUCTS ----------------

def view_products():

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    print("\n--------- Product List ---------")

    for product in products:
        print(f"ID: {product[0]}")
        print(f"Name: {product[1]}")
        print(f"Price: Rs.{product[2]}")
        print("-----------------------------")


# ---------------- ADMIN MENU ----------------

def admin_menu():

    while True:

        print("\n===== ADMIN MENU =====")
        print("1. View Products")
        print("2. Add Product")
        print("3. Delete Product")
        print("4. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":

            view_products()

        elif choice == "2":

            product_name = input("Enter Product Name: ")
            product_price = int(input("Enter Product Price: "))

            cursor.execute(
                "INSERT INTO products(name,price) VALUES(?,?)",
                (product_name, product_price)
            )

            conn.commit()

            print("\nProduct Added Successfully!")

        elif choice == "3":

            product_id = input("Enter Product ID: ")

            cursor.execute(
                "DELETE FROM products WHERE id=?",
                (product_id,)
            )

            conn.commit()

            print("\nProduct Deleted Successfully!")

        elif choice == "4":
            break

        else:
            print("\nInvalid Choice!")


# ---------------- CUSTOMER MENU ----------------

def customer_menu(username):

    while True:

        print(f"\nWelcome {username}")
        print("1. View Products")
        print("2. Buy Product")
        print("3. Logout")

        choice = input("Enter your choice: ")

        if choice == "1":

            view_products()

        elif choice == "2":

            product_id = input("Enter Product ID: ")

            cursor.execute(
                "SELECT * FROM products WHERE id=?",
                (product_id,)
            )

            product = cursor.fetchone()

            if product:

                print("\nPurchase Successful!")
                print("Product:", product[1])
                print("Price: Rs.", product[2])

            else:
                print("\nProduct Not Found!")

        elif choice == "3":
            break

        else:
            print("\nInvalid Choice!")


# ---------------- MAIN PROGRAM ----------------

user = User()

while True:

    print("\n========== ONLINE SHOPPING SYSTEM ==========")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":

        user.register()

    elif choice == "2":

        user.login()

    elif choice == "3":

        print("\nThank You for Using Online Shopping System!")
        break

    else:

        print("\nInvalid Choice!")

conn.close()