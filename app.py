from flask import Flask, render_template, request, session, redirect, url_for,jsonify,flash
import mysql.connector
import datetime
import decimal



app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = 'your_secret_key'

db_config = {
    'host': 'localhost',
    'user': 'karthi',
    'password': '123',

}


@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        balance = request.form['balance']
        
        connection = mysql.connector.connect(**db_config)
       
        items_cursor = connection.cursor()
        items_cursor.execute("USE kadai")
        query = "INSERT INTO users (username, password, balance) VALUES (%s, %s, %s)"
        items_cursor.execute(query, (username, password, balance))
        connection.commit()
        connection.close()
        
        return redirect(url_for('login_page'))  # Redirect to the login page
    
    return render_template('create_user.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Replace this with your MySQL connection and query logic
    connection = mysql.connector.connect(**db_config)

    log_cursor = connection.cursor(dictionary=True)
    log_cursor.execute("USE kadai")
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    log_cursor.execute(query, (username, password))
    user = log_cursor.fetchone()
    connection.close()
    
    if user:
        session['username'] = user['username']
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login_page'))  # Redirect to the login page

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', buy_phase_url=url_for('buy_phase'), sell_phase_url=url_for('sell_phase'))
    else:
        return redirect(url_for('login_page'))


@app.route('/buy_phase')
def buy_phase():
    # Replace this with your MySQL connection and query logic
    connection = mysql.connector.connect(**db_config)
    list_cursor = connection.cursor()
    list_cursor.execute("USE item_list")

    list_cursor.execute("SELECT item_name, Item_price FROM items")
    items = list_cursor.fetchall()

    list_cursor.close()  # Close the cursor
    connection.close()  # Close the connection

    return render_template('buy.html', items=items)



# New route for calculating total and storing purchase history
@app.route('/calculate_total', methods=['POST'])
def calculate_total():
    if 'username' in session:
        username = session['username']
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        selected_items = request.form.getlist('selected_item')
        
        connection = mysql.connector.connect(**db_config)

        # Connect to the 'purchase_hist' database
        purchase_hist_cursor = connection.cursor()
        total_cost = float(request.form['total-cost'])
        purchase_hist_cursor.execute("USE purchase_hist")


        
       

     
        for item in selected_items:
            item_name = item.split(':')[0]
            quantity = int(request.form.get(item_name))
            item_price = float(item.split(':')[1])
            amount = item_price * quantity

            # Insert purchase history into the 'transactions' table
            query = "INSERT INTO transactions (user_name, timestamp, item_name, qty, rate, amount) VALUES (%s, %s, %s, %s, %s, %s)"
            purchase_hist_cursor.execute(query, (username, timestamp, item_name, quantity, item_price, amount))
        
        connection.commit()
        purchase_hist_cursor.close()
        connection.close()
        
        return render_template('finish_purchase.html', total_cost=total_cost)
    else:
        return redirect(url_for('login_page'))
    

@app.route('/finish_purchase', methods=['POST'])
def finish_purchase():
    if 'username' in session:
        username = session['username']
        total_cost = float(request.form['total_cost'])
        
        connection = mysql.connector.connect(**db_config)
        balance_cursor = connection.cursor()
        balance_cursor.execute("USE kadai")
        
        # Retrieve user's current balance
        balance_query = "SELECT balance FROM users WHERE username = %s"
        balance_cursor.execute(balance_query, (username,))
        current_balance = float(balance_cursor.fetchone()[0])
        
        new_balance = current_balance - total_cost
        
        if new_balance < 0:
            return "Insufficient balance. Please add funds."
        
        # Update the user's balance in the database
        update_balance_query = "UPDATE users SET balance = %s WHERE username = %s"
        balance_cursor.execute(update_balance_query, (new_balance, username))
        connection.commit()
        connection.close()
        flash("Purchase successful. New balance: {:.2f}".format(new_balance), "success")
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login_page'))
    # New route for the selling phase

@app.route('/sell_phase')
def sell_phase():
    connection = mysql.connector.connect(**db_config)
    list_cursor = connection.cursor()
    list_cursor.execute("USE item_list")
    list_cursor.execute("SELECT item_name, Item_price FROM items")
    items = list_cursor.fetchall()
    list_cursor.close()
    connection.close()
    return render_template('sell.html', items=items)


@app.route('/calculate_sell_total', methods=['POST'])
def calculate_sell_total():
    if 'username' in session:
        username = session['username']
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        selected_items = request.form.getlist('selected_item')
        total_cost = float(request.form['total-cost'])
        connection = mysql.connector.connect(**db_config)

        # Connect to the 'purchase_hist' database
        list_cursor = connection.cursor()
        list_cursor.execute("USE sell_hist")


        
       

     
        for item in selected_items:
            item_name = item.split(':')[0]
            quantity = int(request.form.get(item_name))
            item_price = float(item.split(':')[1])
            amount = item_price * quantity

            # Insert purchase history into the 'transactions' table
            query = "INSERT INTO tran (user_name, timestamp, item_name, qty, rate, amount) VALUES (%s, %s, %s, %s, %s, %s)"
            list_cursor.execute(query, (username, timestamp, item_name, quantity, item_price, amount))
        
        connection.commit()
        list_cursor.close()
        connection.close()
        
        return render_template('finish_sell_purchase.html', total_cost=total_cost)
    else:
        return redirect(url_for('login_page'))



@app.route('/finish_sell_purchase', methods=['POST'])
def finish_sell_purchase():
    if 'username' in session:
        username = session['username']
        total_cost = float(request.form['total_cost'])
        
        connection = mysql.connector.connect(**db_config)
        balance_cursor = connection.cursor()
        balance_cursor.execute("USE kadai")
        
        # Retrieve user's current balance
        balance_query = "SELECT balance FROM users WHERE username = %s"
        balance_cursor.execute(balance_query, (username,))
        current_balance = float(balance_cursor.fetchone()[0])
        
        new_balance = current_balance + total_cost
        
        if new_balance < 0:
            return "Insufficient balance. Please add funds."
        
        # Update the user's balance in the database
        update_balance_query = "UPDATE users SET balance = %s WHERE username = %s"
        balance_cursor.execute(update_balance_query, (new_balance, username))
        connection.commit()
        connection.close()
        flash("sold successful. New balance: {:.2f}".format(new_balance), "success")
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login_page'))
    # New route for the selling phase
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'username' in session:
        if request.method == 'POST':
            item_name = request.form['item_name']
            item_price = float(request.form['item_price'])
            
            connection = mysql.connector.connect(**db_config)
            list_cursor = connection.cursor()
            list_cursor.execute("USE item_list")
            
            # Insert the new item into the 'items' table
            query = "INSERT INTO items (item_name, Item_price) VALUES (%s, %s)"
            list_cursor.execute(query, (item_name, item_price))
            
            connection.commit()
            list_cursor.close()
            connection.close()
            flash("Item added successfully.", "success")
            return redirect(url_for('dashboard'))
        
        return render_template('add_item.html')  # Render the form to add items
    else:
        return redirect(url_for('login_page'))
    

@app.route('/view_items')
def view_items():
    connection = mysql.connector.connect(**db_config)
    list_cursor = connection.cursor(dictionary=True)
    list_cursor.execute("USE item_list")
    
    # Retrieve all items from the 'items' table
    list_cursor.execute("SELECT * FROM items")
    items = list_cursor.fetchall()
    
    list_cursor.close()
    connection.close()
    
    return render_template('view_items.html', items=items)

@app.route('/transaction_history')
def transaction_history():
    if 'username' in session:
        username = session['username']
        connection = mysql.connector.connect(**db_config)
        hist_cursor = connection.cursor(dictionary=True)
        hist_cursor.execute("USE purchase_hist")
        
        # Retrieve all transactions for the logged-in user
        query = "SELECT id, user_name, timestamp, item_name, qty, rate, amount FROM transactions WHERE user_name = %s"
        hist_cursor.execute(query, (username,))
        transactions = hist_cursor.fetchall()
        
        hist_cursor.close()
        connection.close()
        
        return render_template('transaction_history.html', transactions=transactions, username=username)
    else:
        return redirect(url_for('login_page'))
    

# Add this route to fetch and display purchase history
@app.route('/purchase_history')
def purchase_history():
    if 'username' in session:
        username = session['username']
        
        connection = mysql.connector.connect(**db_config)
        history_cursor = connection.cursor()
        history_cursor.execute("USE purchase_hist")
        
        # Fetch purchase history for the logged-in user
        history_query = "SELECT id, user_name, timestamp, item_name, qty, rate, amount FROM transactions WHERE user_name = %s"
        history_cursor.execute(history_query, (username,))
        purchase_history = history_cursor.fetchall()
        
        history_cursor.close()
        connection.close()
        
        return render_template('purchase_history.html', purchase_history=purchase_history, username=username)
    else:
        return redirect(url_for('login_page'))
    
# ... (previous code)

@app.route('/sold_transaction_history')
def sold_transaction_history():
    if 'username' in session:
        username = session['username']
        
        # Replace this with your MySQL connection and query logic
        connection = mysql.connector.connect(**db_config)
        transaction_cursor = connection.cursor()
        transaction_cursor.execute("USE sell_hist")
        
        # Retrieve all sold transactions for the logged-in user
        query = "SELECT id, timestamp, item_name, qty, rate, amount FROM tran WHERE user_name = %s"
        transaction_cursor.execute(query, (username,))
        sold_transactions = transaction_cursor.fetchall()
        
        transaction_cursor.close()
        connection.close()
        
        return render_template('sold_transaction_history.html', sold_transactions=sold_transactions, username=username)
    else:
        return redirect(url_for('login_page'))
# ... (previous code)

# ... (previous code)

@app.route('/available_balance')
def available_balance():
    if 'username' in session:
        username = session['username']
        
        # Fetch user's balance from the 'kadai' database
        connection = mysql.connector.connect(**db_config)
        bal_cursor = connection.cursor()
        bal_cursor.execute("USE kadai")
        balance_query = "SELECT balance FROM users WHERE username = %s"
        bal_cursor.execute(balance_query, (username,))
        balance = bal_cursor.fetchone()[0]
        connection.close()
        
        return render_template('available_balance.html', username=username, balance=balance)
    else:
        return redirect(url_for('login_page'))

# ... (remaining code)


# ... (remaining code)


# ... (remaining code)

if __name__ == '__main__':
    app.run(debug=True)



