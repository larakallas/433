import psycopg2
from flask import Flask, redirect, render_template, request, jsonify, url_for
from datetime import date


app = Flask(__name__)

def connect_to_db():
        connection = psycopg2.connect(
            user="postgres",
            password="lara",
            host="127.0.0.1",
            port="5432",
            database="project-433"
        )
        return connection
def fetch_table_data(connection, table_name):
    try:
        cursor = connection.cursor()
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        cursor.close()
        if not rows:
            return [], headers
        return rows, headers
    except psycopg2.Error as error:
        print(f"Error fetching data from {table_name} table:", error)
        return [], []

@app.route('/')
def index():
    connection = connect_to_db()
    
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    num_customers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM books")
    num_books = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    num_orders = cursor.fetchone()[0]

    cursor.close()
    connection.close()
    
    return render_template('index.html', num_customers=num_customers, num_books=num_books, num_orders=num_orders)

@app.route('/display_all_data')
def display_all_data():
    connection = connect_to_db()
    book, book_headers = fetch_table_data(connection, "books")
    author, author_headers = fetch_table_data(connection, "authors")
    publisher, publisher_headers = fetch_table_data(connection, "publisher")    
    customers, customers_headers = fetch_table_data(connection, "customers")
    orders, orders_headers = fetch_table_data(connection, "orders")
    order_items, order_items_headers = fetch_table_data(connection, "order_item")
    bookstore_storage, bookstore_storage_headers = fetch_table_data(connection, "book_storage")
    order_contains, order_contains_headers = fetch_table_data(connection, "order_contains")
    staff, staff_headers = fetch_table_data(connection, "staff")

    connection.close()
    return render_template('display_tables.html', book=book, book_headers=book_headers, author=author, author_headers=author_headers, publisher=publisher, publisher_headers=publisher_headers, customers=customers, customers_headers=customers_headers, orders=orders, orders_headers=orders_headers, order_items=order_items, order_items_headers=order_items_headers, bookstore_storage=bookstore_storage, bookstore_storage_headers=bookstore_storage_headers, order_contains=order_contains, order_contains_headers=order_contains_headers, staff=staff, staff_headers=staff_headers)



@app.route('/display_author_info')
def display_author_info():
    author_id = request.args.get('author_id')
    if not author_id:
        return "Author ID is required", 400
    
    connection = connect_to_db()
    author_info_query = f"SELECT * FROM authors WHERE authorID = %s"
    cursor = connection.cursor()
    cursor.execute(author_info_query, (author_id,))
    author_info = cursor.fetchone()
    cursor.close()
    
    if not author_info:
        return f"No author found with ID {author_id}", 404
   
    books_query = f"SELECT * FROM books WHERE authorID = %s"
    cursor = connection.cursor()
    cursor.execute(books_query, (author_id,))
    books = cursor.fetchall()
    cursor.close()
    
    connection.close()
    
    return render_template('display_author_info.html', author=author_info, books=books)
@app.route('/search_customer')
def search_customer():
    customer_id = request.args.get('customer_id')
    if not customer_id:
        return "Customer ID is required", 400
    
    connection = connect_to_db()
    
    customer_query = "SELECT * FROM customers WHERE CustomerID = %s"
    cursor = connection.cursor()
    cursor.execute(customer_query, (customer_id,))
    customer = cursor.fetchone()
    
    orders_query = "SELECT * FROM orders WHERE customerID = %s"
    cursor.execute(orders_query, (customer_id,))
    orders = cursor.fetchall()
    
    cursor.close()
    
    if not customer:
        return f"No customer found with ID {customer_id}", 404
   
    connection.close()
    
    return render_template('display_customer_info.html', customer=customer, orders=orders)

@app.route('/insert_customer', methods=['POST'])
def insert_customer():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        if not first_name or not last_name or not email:
            return "All fields are required", 400        
        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            insert_query = "INSERT INTO CUSTOMERS (CustomerID,FirstName, LastName, Email) VALUES (%s,%s, %s, %s) RETURNING CustomerID"
            cursor.execute(insert_query, (customer_id,first_name, last_name, email))
            connection.commit()
            customer_id = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return f"Customer with ID {customer_id} inserted successfully"
        except psycopg2.Error as error:
            return f"Error inserting customer: {error}", 500
@app.route('/orders_assigned_to_staff', methods=['GET'])
def orders_assigned_to_staff():
    staff_id = request.args.get('staff_id')

    connection = connect_to_db()
    cursor = connection.cursor()

    query = "SELECT o.orderID, o.customerID, o.orderdate, o.price, s.first_name, s.last_name FROM Orders o JOIN staff s ON o.StaffID = s.staffID WHERE o.StaffID = %s"
    cursor.execute(query, (staff_id,))
    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('orders_assigned_to_staff.html', orders=orders)

@app.route('/book_storage')
def book_storage():
    book_id = request.args.get('book_id')
    if not book_id:
        return "Book ID is required", 400
    
    connection = connect_to_db()
    

    book_storage_query = "SELECT * FROM book_storage WHERE bookID = %s"
    cursor = connection.cursor()
    cursor.execute(book_storage_query, (book_id,))
    book_storage_info = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    if not book_storage_info:
        return f"No book storage found for book with ID {book_id}", 404
   
    return render_template('book_storage.html', book_storage_info=book_storage_info)

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        if not first_name or not last_name:
            return "Both first name and last name are required for deletion", 400

        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            
            # Check if the customer exists
            cursor.execute("SELECT * FROM customers WHERE FirstName = %s AND LastName = %s", (first_name, last_name))
            customer = cursor.fetchone()
            if not customer:
                return f"No customer found with name {first_name} {last_name}", 404
            
            # Delete the customer
            cursor.execute("DELETE FROM customers WHERE FirstName = %s AND LastName = %s", (first_name, last_name))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return f"Customer {first_name} {last_name} deleted successfully"
        except psycopg2.Error as error:
            return f"Error deleting customer: {error}", 500
@app.route('/delete_book', methods=['POST'])
def delete_book():
    if request.method == 'POST':
        title = request.form['title']

        if not title:
            return "Book title is required for deletion", 400

        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            
            cursor.execute("SELECT * FROM books WHERE title = %s", (title,))
            book = cursor.fetchone()
            if not book:
                return f"No book found with title {title}", 404
            
            cursor.execute("DELETE FROM books WHERE title = %s", (title,))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return f"Book '{title}' deleted successfully"
        except psycopg2.Error as error:
            return f"Error deleting book: {error}", 500
@app.route('/update_customer_id', methods=['POST'])
def update_customer_id():
    if request.method == 'POST':
        old_customer_id = request.form['old_customer_id']
        new_customer_id = request.form['new_customer_id']

        if not old_customer_id or not new_customer_id:
            return "Both old and new CustomerIDs are required", 400

        try:
            connection = connect_to_db()
            cursor = connection.cursor()

            # Check if the old customer ID exists
            cursor.execute("SELECT * FROM customers WHERE CustomerID = %s", (old_customer_id,))
            customer = cursor.fetchone()
            if not customer:
                return f"No customer found with ID {old_customer_id}", 404

            # Update the customer ID
            cursor.execute("UPDATE customers SET CustomerID = %s WHERE CustomerID = %s",
                           (new_customer_id, old_customer_id))
            connection.commit()

            cursor.close()
            connection.close()

            return f"Customer with ID {old_customer_id} updated to {new_customer_id} successfully"
        except psycopg2.Error as error:
            return f"Error updating customer ID: {error}", 500


@app.route('/update_staff_id', methods=['POST'])
def update_staff_id():
    if request.method == 'POST':
        old_staff_id = request.form['old_staff_id']
        new_staff_id = request.form['new_staff_id']

        if not old_staff_id or not new_staff_id:
            return "Both old and new StaffIDs are required", 400

        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM staff WHERE StaffID = %s", (old_staff_id,))
            staff = cursor.fetchone()
            if not staff:
                return f"No staff found with ID {old_staff_id}", 404
            cursor.execute("UPDATE staff SET StaffID = %s WHERE StaffID = %s",
                           (new_staff_id, old_staff_id))
            connection.commit()

            cursor.close()
            connection.close()

            return f"Staff with ID {old_staff_id} updated to {new_staff_id} successfully"
        except psycopg2.Error as error:
            return f"Error updating staff ID: {error}", 500

if __name__ == '__main__':
    app.run(debug=True)
