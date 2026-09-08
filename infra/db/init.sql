DROP TABLE IF EXISTS support_tickets;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS sale_items;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS customers;


CREATE TABLE customers(
    cpf VARCHAR(11) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

CREATE TABLE stock(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(30) NOT NULL,  -- Ex: T-shirt, Pants, Dress
    size VARCHAR(10),  -- Ex: S, M, L, XL
    price DECIMAL(10,2) NOT NULL,
    quantity_in_stock INT NOT NULL DEFAULT 0
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    customer_cpf VARCHAR(11) REFERENCES customers(cpf),
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'PENDING',  -- Status: PENDING, PAID, SHIPPED, CANCELED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sale_items (
    sale_id INT REFERENCES sales(id) ON DELETE CASCADE,
    product_id INT REFERENCES stock(id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (sale_id, product_id)
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    sale_id INT REFERENCES sales(id),
    payment_method VARCHAR(50),  -- Ex: PIX, CREDIT_CARD
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'APPROVED',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE support_tickets (
    id SERIAL PRIMARY KEY,
    customer_cpf VARCHAR(11) REFERENCES customers(cpf),
    issue_description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'OPEN',  -- Status: OPEN, RESOLVED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Initial Data Load for MCP Testing 
INSERT INTO customers (cpf, name, phone) VALUES 
('11122233344', 'João Silva', '11999998888'),
('55566677788', 'Maria Oliveira', '21988887777'),
('99988877766', 'Carlos Mendes', '31977776666'),
('44455566677', 'Ana Costa', '85966665555'),
('12312312312', 'Fernanda Lima', '41955554444'),
('98798798798', 'Roberto Alves', '71944443333');

-- Stock (Rich catalog, including out-of-stock items and various sizes)
INSERT INTO stock (name, category, size, price, quantity_in_stock) VALUES 
('Basic Cotton T-shirt', 'T-shirt', 'S', 49.90, 15),
('Basic Cotton T-shirt', 'T-shirt', 'M', 49.90, 50),
('Basic Cotton T-shirt', 'T-shirt', 'L', 49.90, 30),
('Vintage Print T-shirt', 'T-shirt', 'M', 69.90, 0), -- OUT OF STOCK
('Slim Jeans', 'Pants', '38', 129.90, 10),
('Slim Jeans', 'Pants', '40', 129.90, 15),
('Slim Jeans', 'Pants', '42', 129.90, 5),
('Summer Floral Dress', 'Dress', 'S', 89.90, 10),
('Summer Floral Dress', 'Dress', 'M', 89.90, 2),
('Faux Leather Jacket', 'Jacket', 'L', 249.90, 8),
('Hoodie', 'Jacket', 'M', 119.90, 20),
('Twill Shorts', 'Shorts', '40', 79.90, 25);

-- Orders (Different statuses to test the agents)
INSERT INTO sales (id, customer_cpf, total_amount, status, created_at) VALUES 
(1, '11122233344', 129.90, 'PENDING', '2026-08-15 10:30:00'), -- Order awaiting payment
(2, '55566677788', 179.80, 'PAID', '2026-08-16 14:15:00'),    -- Order paid, awaiting shipment
(3, '99988877766', 249.90, 'SHIPPED', '2026-08-10 09:00:00'), -- Order already shipped
(4, '44455566677', 69.90, 'CANCELED', '2026-08-01 11:20:00'), -- Order canceled
(5, '12312312312', 369.80, 'PAID', '2026-08-17 08:45:00');    -- Recent order paid

-- Resetting the ID sequence to avoid errors in the next INSERT without an explicit ID
SELECT setval('sales_id_seq', (SELECT MAX(id) FROM sales));

-- Order Items (Linking products to the sales above)
INSERT INTO sale_items (sale_id, product_id, quantity, unit_price) VALUES 
(1, 6, 1, 129.90),                  -- João bought 1 Pants 40
(2, 8, 2, 89.90),                   -- Maria bought 2 Dresses S
(3, 10, 1, 249.90),                 -- Carlos bought 1 Jacket
(4, 4, 1, 69.90),                   -- Ana tried to buy Vintage T-shirt (canceled)
(5, 7, 1, 129.90),                  -- Fernanda bought 1 Pants 42
(5, 10, 1, 249.90);                 -- Fernanda bought 1 Jacket

-- Payments (Only for PAID and SHIPPED orders)
INSERT INTO payments (sale_id, payment_method, amount, status, processed_at) VALUES 
(2, 'PIX', 179.80, 'APPROVED', '2026-08-16 14:20:00'),
(3, 'CREDIT_CARD', 249.90, 'APPROVED', '2026-08-10 09:05:00'),
(5, 'CREDIT_CARD', 369.80, 'APPROVED', '2026-08-17 08:50:00');

-- Support Tickets (Cases for the Support Agent to resolve)
INSERT INTO support_tickets (customer_cpf, issue_description, status, created_at) VALUES 
('99988877766', 'The tracking code for my jacket is not working.', 'OPEN', '2026-08-15 16:40:00'),
('55566677788', 'I want to change the delivery address of my order before it is shipped.', 'OPEN', '2026-08-17 10:00:00'),
('44455566677', 'Why was my order canceled?', 'RESOLVED', '2026-08-02 14:00:00');