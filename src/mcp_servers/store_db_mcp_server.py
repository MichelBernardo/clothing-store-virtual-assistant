from fastmcp import FastMCP
import psycopg
from psycopg.rows import dict_row
import json

from src.core.config import settings


server = FastMCP("Store Server")

def execute_sql_command(query, params=None):
    try:
        with psycopg.connect(settings.database_url) as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, params)

                if cursor.description:
                    result = cursor.fetchall()
                    return json.dumps(result, default=str, ensure_ascii=False)
                
                conn.commit()
                return "Command executed successfully."
    except Exception as e:
        return f"Error accessing the database: {str(e)}"

# ==========================================
# SALES AGENT TOOLS
# ==========================================

@server.tool()
def check_customer(cpf: str) -> str:
    """
    Checks if a customer exists in database using their CPF.
    The agent should use this before attempting to create a sales order.
    """
    cpf_clean = cpf.strip().replace("-","").replace(".","")
    query = "SELECT cpf, name FROM customers WHERE cpf = %s"
    result = execute_sql_command(query, (cpf_clean,))

    if result == "[]":
        # Mudamos a mensagem para não acionar o gatilho do Suporte
        return "Customer not found. You must register the customer before creating an order."

    return result

@server.tool()
def register_customer(cpf: str, name: str, phone: str) -> str:
    """
    Registers a new customer in the database.
    Use this tool when check_customer returns that the customer does not exist.
    """
    cpf_clean = cpf.strip().replace(".", "").replace("-", "")
    
    query = """
        INSERT INTO customers (cpf, name, phone) 
        VALUES (%s, %s, %s) 
        RETURNING cpf, name;
    """
    
    # Inserindo o telefone também!
    result = execute_sql_command(query, (cpf_clean, name, phone))
    
    if "Error" in result:
        return f"Failed to register customer. Detail: {result}"
        
    return f"Customer {name} successfully registered with CPF {cpf_clean}. You can now proceed with the order."

@server.tool()
def get_stock(product_name: str, size: str) -> str:
    """
    Checks for available stock. Returns the ID, Name, Price and Quantity.
    Use the ID and price returned here to pass on when creating the sale.
    """
    # Agora busca tanto no nome quanto na categoria
    sql_select = """
        SELECT id, name, price, quantity_in_stock 
        FROM stock 
        WHERE (category ILIKE %s OR name ILIKE %s) AND size = %s
    """

    term = f"%{product_name}%"
    result = execute_sql_command(sql_select, (term, term, size))
    
    if result == "[]":
        return "Product Unavailable or without stock in this category/name and size."
    return result

@server.tool()
def create_sales_order(customer_cpf: str, product_id: int, quantity: int, unit_price: float) -> str:
    """
    Creates a sales order and update the inventory.
    ATTENTION: The product_id and unit_price must come from the results of the 'get_stock' tool.
    """
    cpf = customer_cpf.strip().replace(".", "").replace("-", "")
    total_amount = quantity * unit_price

    sql_transaction = """
        WITH new_sale AS (
            INSERT INTO sales (customer_cpf, total_amount, status) 
            VALUES (%s, %s, 'PENDING') 
            RETURNING id
        ),
        new_item AS (
            INSERT INTO sale_items (sale_id, product_id, quantity, unit_price)
            SELECT id, %s, %s, %s FROM new_sale
        )
        UPDATE stock 
        SET quantity_in_stock = quantity_in_stock - %s 
        WHERE id = %s 
        RETURNING id as stock_updated;
    """

    params = (
        cpf, total_amount,          # For sales
        product_id, quantity, unit_price, # For sale_items
        quantity, product_id              # To update the stock
    )

    result = execute_sql_command(sql_transaction, params)

    if "Error" in result:
        return f"Error creating the order. Check if the customer exists or if there is stock. Detail: {result}"

    return f"Order successfully created! Status: PENDING. Total amount: R$ {total_amount:.2f}."

# ==========================================
# PAYMENT AGENT TOOLS
# ==========================================

@server.tool()
def get_pending_orders(customer_cpf: str) -> str:
    """
    Retrieves all pending orders (sales) for a specific customer.
    Use this to show the customer what they need to pay.
    """
    cpf_clean = customer_cpf.strip().replace(".", "").replace("-", "")
    
    query = """
        SELECT id as sale_id, total_amount, created_at 
        FROM sales 
        WHERE customer_cpf = %s AND status = 'PENDING'
    """
    
    result = execute_sql_command(query, (cpf_clean,))
    if result == "[]":
        return "No pending orders found for this customer."
    return result

@server.tool()
def process_payment(sale_id: int, payment_method: str, amount: float) -> str:
    """
    Processes the payment for a specific sale and updates the sale status to 'PAID'.
    Allowed payment_method values: 'PIX', 'CREDIT_CARD'.
    """
    # Using a CTE to insert the payment and update the sale status in one transaction
    sql_transaction = """
        WITH new_payment AS (
            INSERT INTO payments (sale_id, payment_method, amount, status)
            VALUES (%s, %s, %s, 'APPROVED')
            RETURNING id
        )
        UPDATE sales 
        SET status = 'PAID' 
        WHERE id = %s 
        RETURNING id as sale_updated;
    """
    
    params = (sale_id, payment_method, amount, sale_id)
    result = execute_sql_command(sql_transaction, params)
    
    if "Error" in result:
        return f"Payment processing failed. Details: {result}"
        
    return f"Payment of R$ {amount:.2f} via {payment_method} approved successfully. Sale {sale_id} status updated to PAID."

# ==========================================
# SUPPORT AGENT TOOLS
# ==========================================

@server.tool()
def get_order_history(customer_cpf: str) -> str:
    """
    Retrieves the complete order history for a customer, including items and statuses.
    Use this when a customer asks about the status of a past or current order.
    """
    cpf_clean = customer_cpf.strip().replace(".", "").replace("-", "")
    
    # We JOIN sales, sale_items, and stock to give a complete view to the agent
    query = """
        SELECT 
            s.id as sale_id, 
            s.status as sale_status, 
            s.created_at,
            st.name as product_name,
            si.quantity
        FROM sales s
        JOIN sale_items si ON s.id = si.sale_id
        JOIN stock st ON si.product_id = st.id
        WHERE s.customer_cpf = %s
        ORDER BY s.created_at DESC
    """
    
    result = execute_sql_command(query, (cpf_clean,))
    if result == "[]":
        return "No order history found for this customer."
    return result

@server.tool()
def open_support_ticket(customer_cpf: str, issue_description: str) -> str:
    """
    Opens a new support ticket for a customer when they have a complaint, 
    return request, or unresolved issue.
    """
    cpf_clean = customer_cpf.strip().replace(".", "").replace("-", "")
    
    query = """
        INSERT INTO support_tickets (customer_cpf, issue_description, status)
        VALUES (%s, %s, 'OPEN')
        RETURNING id as ticket_id;
    """
    
    result = execute_sql_command(query, (cpf_clean, issue_description))
    
    if "Error" in result:
        return f"Failed to open support ticket. Details: {result}"
        
    return f"Support ticket opened successfully. Issue recorded and forwarded to the human service team."


if __name__ == "__main__":
    server.run(transport="sse", port=8080)