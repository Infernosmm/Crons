import requests
import mysql.connector
from mysql.connector import Error

# Configuration: Replace these values with your own API and database details
API_KEY = '9b39db9956a7674caecdfe7ec83acb74'  # Replace with your actual API key
API_URL = 'https://smmboat.com/orders/status'  # This is your provided API URL

DB_HOST = 'localhost'  # Replace with your database host (e.g., 'localhost' or a remote IP)
DB_NAME = 'u488996979_inferno'  # Replace with your database name
DB_USER = 'u488996979_inferno'  # Replace with your database user
DB_PASSWORD = '@Matrix12345'  # Replace with your database password

# Database connection setup
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Function to fetch all orders from your database (not just pending)
def fetch_all_orders(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        # Fetch orders that are either pending, in progress, or partially completed (or any other status you want to track)
        cursor.execute("SELECT order_id, api_order_id, status FROM orders WHERE status IN ('pending', 'in progress', 'partially completed')")
        orders = cursor.fetchall()
        return orders
    except Error as e:
        print(f"Error fetching orders: {e}")
        return []

# Function to update the status of an order
def update_order_status(connection, order_id, new_status):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s", (new_status, order_id))
        connection.commit()
    except Error as e:
        print(f"Error updating order status: {e}")

# Function to check order status via the API
def check_order_status(api_order_id):
    # Construct the API request URL with the API key and order ID
    api_url = f"{API_URL}?order_id={api_order_id}&api_key={API_KEY}"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            order_data = response.json()
            return order_data.get('status', None)  # Assuming the API returns a 'status' field
        else:
            print(f"API request failed with status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error connecting to API: {e}")
        return None

# Main function to track all orders
def track_orders():
    # Step 1: Connect to the database
    connection = create_db_connection()
    if connection is None:
        return

    # Step 2: Fetch all relevant orders (pending, in progress, partially completed)
    all_orders = fetch_all_orders(connection)
    
    # Step 3: Loop through each order and check its status via the API
    for order in all_orders:
        order_id = order['order_id']
        api_order_id = order['api_order_id']
        current_status = order['status']
        
        new_status = check_order_status(api_order_id)
        
        if new_status and new_status != current_status:  # Update only if status has changed
            # Step 4: Update order status in the database
            update_order_status(connection, order_id, new_status)
            print(f"Order {order_id} status updated from {current_status} to {new_status}")
        else:
            print(f"Order {order_id} status remains {current_status}")
    
    # Step 5: Close the database connection
    connection.close()

# Schedule this script to run every 5-10 minutes using cron or another scheduler.
if __name__ == "__main__":
    track_orders()