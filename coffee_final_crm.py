import sqlite3
import os
import csv
from sqlite3 import IntegrityError
from datetime import datetime
from faker import Faker
from tabulate import tabulate

class Employee:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

class CoffeeShopCrm:
    def __init__(self):
        self.fake = None
        self.init_faker()
        self.conn = sqlite3.connect('coffee_shop_crm.db')
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.conn.cursor()
        self.initialize_database()
        if self.fake:
            self.fake_data_generator()


    def init_faker(self):
        if not os.path.exists("coffee_shop_crm.db"):
            self.fake = Faker()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone_number TEXT NOT NULL
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                clerk_id INTEGER,
                delivery_id INTEGER,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'Incomplete',
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (clerk_id) REFERENCES employees(id),
                FOREIGN KEY (delivery_id) REFERENCES employees(id)
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );
        ''')
        self.conn.commit()
    
    def login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        self.cursor.execute('SELECT * FROM employees WHERE username=? AND password=?;', (username, password))
        result = self.cursor.fetchone()

        if result:
            return result[3], result[0]
        else:
            print("Invalid credentials. Please try again.")
            exit()

    def __del__(self):
        self.conn.close()

    def fake_data_generator(self):
        for username, role in zip(['clerk_fred', 'clerk_john', 'delivery1', 'delivery2', 'manager_elon'], ['clerk', 'clerk', 'delivery', 'delivery', 'manager']):
            self.cursor.execute('''
                INSERT INTO employees (username, password, role) VALUES (?, ?, ?);
            ''', (username, '123', role))

        for _ in range(5):
            self.cursor.execute('''
                INSERT INTO customers (name, address, phone_number) VALUES (?, ?, ?);
            ''', (self.fake.name(), self.fake.address(), self.fake.phone_number()))

        for _ in range(7):
            self.cursor.execute('''
                INSERT INTO orders (customer_id, description, date, total_amount, clerk_id) VALUES (?, ?, ?, ?, ?);
            ''', (self.fake.random_int(min=1, max=5), self.fake.text(), self.fake.date_this_decade(), self.fake.random_int(min=250, max=1000), self.fake.random_int(min=1, max=2)))

        self.conn.commit()

    def export_to_csv(self, table_name, filename):
        self.cursor.execute(f'SELECT * FROM {table_name};')
        rows = self.cursor.fetchall()

        with open(filename + '.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([desc[0] for desc in self.cursor.description])
            csv_writer.writerows(rows)

class Manager(Employee):
    def __init__(self, username, password):
        super().__init__(username, password, 'manager')

    def menu(self):
        print("1. Customer profile")
        print("2. Number of orders in a specific day")
        print("3. Pending orders")
        print("4. Total number of orders per clerk")
        print("5. Export data to CSV")
        print("6. Exit")

    def customer_profile(self, cursor):
        try:
            customer_id = int(input("Enter customer ID: "))
        except ValueError as e:
            print(e)
            raise Exception("Wrong customer id type: should be a number, not text")
        cursor.execute('SELECT name, address, phone_number FROM customers WHERE id = ?;', (customer_id,))
        customer_data = cursor.fetchone()

        if customer_data:
            print('\n')
            print("Customer Profile:")
            print(tabulate([customer_data], headers=['Name', 'Address', 'Phone'], tablefmt='simple'))
            print('\n')
        else:
            print("Customer not found.")

    def orders_in_specific_day(self, cursor):
        specific_day = input("Enter specific day (YYYY-MM-DD): ")
        cursor.execute('SELECT COUNT(id), SUM(total_amount) FROM orders WHERE date LIKE ?;', (f'{specific_day}%',))
        result = cursor.fetchone()

        if result:
            print(f"\nNumber of orders on {specific_day}: {result[0]}")
            print(f"Total amount of orders on {specific_day}: {result[1]}\n")
        else:
            print("\nNo orders on the specified day.")

    def pending_orders(self, cursor):
        cursor.execute('SELECT id, customer_id, date, total_amount, clerk_id, delivery_id, status FROM orders WHERE status = "Incomplete" OR status = "Assigned";')
        rows = cursor.fetchall()
        info = [row[1::] for row in rows]

        if rows:
            print("Pending Orders:")
            print(tabulate(info, headers=['Customer ID', 'Date', 'Total Amount', 'Clerk ID', 'Delivery ID', 'Status'], tablefmt='double_outline'))
        else:
            print("No pending orders.")

    def total_orders_per_clerk(self, cursor):
        cursor.execute('SELECT clerk_id, COUNT(id) as "Total orders", SUM(total_amount) as "Total amount" FROM orders GROUP BY clerk_id')
        rows = cursor.fetchall()

        if rows:
            print("Total Orders per Clerk:")
            print(tabulate(rows, headers=['Clerk ID', 'Number of orders', 'Summ amount'], tablefmt='double_outline'))
        else:
            print("No data available.")

class Clerk(Employee):
    def __init__(self, username, password):
        super().__init__(username, password, 'clerk')

    def menu(self):
        print("1. Place an order")
        print("2. Assign order to delivery")
        print("3. Check incomplete orders")
        print("4. Exit")
    
    def check_incomplete_orders(self, userid, cursor):
        cursor.execute('SELECT id, customer_id, date, total_amount, status FROM orders WHERE (status = "Assigned" OR status = "Incomplete") AND clerk_id = ?;', (userid,))
        rows = cursor.fetchall()

        if rows:
            print("YOUR INCOMPLETED ORDERS")
            print(tabulate(rows, headers=['Order ID', 'Customer ID', 'Date', 'Total Amount', 'Status'], tablefmt='double_outline'))
        else:
            print("No incomplete orders.")

    def place_order(self, cursor, conn, userid):
        try:
            customer_id = int(input("Enter customer ID: "))
        except ValueError as e:
            print(e)
            raise Exception("Wrong customer id type: should be a number, not text")
        description = input("Enter order description: ")
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            total_amount = float(input("Enter total amount: "))
        except ValueError as e:
            print(e)
            raise Exception(f"Wrong total amount type: should be a number, not text")

        try:
            cursor.execute('''
                INSERT INTO orders (customer_id, description, date, total_amount, clerk_id) VALUES (?, ?, ?, ?, ?);
            ''', (customer_id, description, date, total_amount, userid))
            conn.commit()
        except IntegrityError as fk_e:
            print("Customer does not exist. Please add it now")
            name = input("Enter customer name: ")
            address = input("Enter customer address: ")
            phone = input("Enter customer phone number: ")

            cursor.execute('''
                INSERT INTO customers (id, name, address, phone_number) VALUES (?, ?, ?, ?);
            ''', (customer_id, name, address, phone))
            conn.commit()
            cursor.execute('''
                INSERT INTO orders (customer_id, description, date, total_amount, clerk_id) VALUES (?, ?, ?, ?, ?);
            ''', (customer_id, description, date, total_amount, userid))
            conn.commit()
        print("Order placed successfully.")

    def assign_order_to_delivery(self, cursor, conn, delivery_id):
        cursor.execute('SELECT * FROM employees WHERE role = "delivery" AND id = ?;', (delivery_id,))
        rows = cursor.fetchall()
        if not rows:
            print(f"Delivery employee does not exist: ID {delivery_id}")
            return
        order_id = int(input("Enter order ID to assign to delivery: "))
        cursor.execute('UPDATE orders SET status = "Assigned", delivery_id = ? WHERE id = ?;', (delivery_id, order_id))
        if cursor.rowcount < 1:
            print(f"The order with ID `{order_id}` does not exist")
            return
        conn.commit()
        print("Order assigned to delivery.")

class Delivery(Employee):
    def __init__(self, username, password):
        super().__init__(username, password, 'delivery')

    def menu(self):
        print("1. Mark order as completed")
        print("2 Exit")

    def mark_order_as_completed(self, cursor, conn):
        order_id = int(input("Enter order ID to mark as completed: "))
        cursor.execute('UPDATE orders SET status = "Completed" WHERE id = ?;', (order_id,))
        if cursor.rowcount < 1:
            print(f"The order with ID `{order_id}` does not exist")
            return
        conn.commit()
        print("Order marked as completed.")

def main():
    coffee_shop_crm = CoffeeShopCrm()
    role, user_id = coffee_shop_crm.login()
    
    if role:
        try:
            if role == 'manager':
                manager = Manager(role, user_id)
                while True:
                    manager.menu()
                    choice = input("Enter your choice: ")

                    if choice == '1':
                        manager.customer_profile(coffee_shop_crm.cursor)
                    elif choice == '2':
                        manager.orders_in_specific_day(coffee_shop_crm.cursor)
                    elif choice == '3':
                        manager.pending_orders(coffee_shop_crm.cursor)
                    elif choice == '4':
                        manager.total_orders_per_clerk(coffee_shop_crm.cursor)
                    elif choice == '5':
                        filename = input("Enter database name (`employees`, `orders` or `customers`): ")
                        coffee_shop_crm.export_to_csv('orders', filename)
                        print(f"Data exported to {filename}")
                    elif choice == '6':
                        raise KeyboardInterrupt
                    else:
                        print("Invalid choice. Try again.")

            elif role == 'clerk':
                clerk = Clerk(role, user_id)
                while True:
                    clerk.menu()
                    choice = input("Enter your choice: ")
                    if choice == '1':
                        clerk.place_order(coffee_shop_crm.cursor, coffee_shop_crm.conn, user_id)
                    elif choice == '2':
                        delivery_id = int(input("Enter delivery ID to assign: "))
                        clerk.assign_order_to_delivery(coffee_shop_crm.cursor, coffee_shop_crm.conn, delivery_id)
                    elif choice == '3':
                        clerk.check_incomplete_orders(user_id, coffee_shop_crm.cursor)
                    elif choice == '4':
                        raise KeyboardInterrupt
                    else:
                        print("Invalid choice. Try again.")

            elif role == 'delivery':
                delivery = Delivery(role, user_id)
                while True:
                    delivery.menu()
                    choice = input("Enter your choice: ")

                    if choice == '1':
                        delivery.mark_order_as_completed(coffee_shop_crm.cursor, coffee_shop_crm.conn)
                    elif choice == '2':
                        raise KeyboardInterrupt
                    else:
                        print("Invalid choice. Try again.")
        except (KeyboardInterrupt, EOFError):
            del coffee_shop_crm
            print("Bye!")

if __name__ == "__main__":
    main()
