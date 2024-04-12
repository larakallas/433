import psycopg2
from flask import Flask, redirect, render_template, request, jsonify, url_for
from datetime import date


app = Flask(__name__)

def connect_to_db():
        connection = psycopg2.connect(
            user="postgres",
            password="j",
            host="127.0.0.1",
            port="5432",
            database="project"
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
    return render_template('index.html')


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


if __name__ == '__main__':
    app.run(debug=True)
