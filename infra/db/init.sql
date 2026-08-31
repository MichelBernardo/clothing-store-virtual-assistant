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
    category VARCHAR(30) NOT NULL,  -- Ex: Camiseta, Calça, Vestido
    size VARCHAR(10),  -- Ex: P, M, G, GG
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

-- Estoque (Catálogo rico, incluindo itens sem estoque e variados tamanhos)
INSERT INTO stock (name, category, size, price, quantity_in_stock) VALUES 
('Camiseta Básica Algodão', 'Camiseta', 'P', 49.90, 15),
('Camiseta Básica Algodão', 'Camiseta', 'M', 49.90, 50),
('Camiseta Básica Algodão', 'Camiseta', 'G', 49.90, 30),
('Camiseta Estampa Vintage', 'Camiseta', 'M', 69.90, 0), -- SEM ESTOQUE
('Calça Jeans Slim', 'Calça', '38', 129.90, 10),
('Calça Jeans Slim', 'Calça', '40', 129.90, 15),
('Calça Jeans Slim', 'Calça', '42', 129.90, 5),
('Vestido Floral Verão', 'Vestido', 'P', 89.90, 10),
('Vestido Floral Verão', 'Vestido', 'M', 89.90, 2),
('Jaqueta de Couro Sintético', 'Casaco', 'G', 249.90, 8),
('Moletom com Capuz', 'Casaco', 'M', 119.90, 20),
('Bermuda Sarja', 'Bermuda', '40', 79.90, 25);

-- Pedidos (Diferentes status para testar os agentes)
INSERT INTO sales (id, customer_cpf, total_amount, status, created_at) VALUES 
(1, '11122233344', 129.90, 'PENDING', '2026-08-15 10:30:00'), -- Pedido aguardando pagamento
(2, '55566677788', 179.80, 'PAID', '2026-08-16 14:15:00'),    -- Pedido pago, aguardando envio
(3, '99988877766', 249.90, 'SHIPPED', '2026-08-10 09:00:00'), -- Pedido já enviado
(4, '44455566677', 69.90, 'CANCELED', '2026-08-01 11:20:00'), -- Pedido cancelado
(5, '12312312312', 369.80, 'PAID', '2026-08-17 08:45:00');    -- Pedido recente pago

-- Resetando a sequência de IDs para evitar erro no próximo INSERT sem ID explícito
SELECT setval('sales_id_seq', (SELECT MAX(id) FROM sales));

-- Itens dos Pedidos (Vinculando produtos às vendas acima)
INSERT INTO sale_items (sale_id, product_id, quantity, unit_price) VALUES 
(1, 6, 1, 129.90),                  -- João comprou 1 Calça 40
(2, 8, 2, 89.90),                   -- Maria comprou 2 Vestidos P
(3, 10, 1, 249.90),                 -- Carlos comprou 1 Jaqueta
(4, 4, 1, 69.90),                   -- Ana tentou comprar Camiseta Vintage (cancelado)
(5, 7, 1, 129.90),                  -- Fernanda comprou 1 Calça 42
(5, 10, 1, 249.90);                 -- Fernanda comprou 1 Jaqueta

-- Pagamentos (Somente para pedidos PAID e SHIPPED)
INSERT INTO payments (sale_id, payment_method, amount, status, processed_at) VALUES 
(2, 'PIX', 179.80, 'APPROVED', '2026-08-16 14:20:00'),
(3, 'CREDIT_CARD', 249.90, 'APPROVED', '2026-08-10 09:05:00'),
(5, 'CREDIT_CARD', 369.80, 'APPROVED', '2026-08-17 08:50:00');

-- Chamados de Suporte (Casos para o Agente de Suporte resolver)
INSERT INTO support_tickets (customer_cpf, issue_description, status, created_at) VALUES 
('99988877766', 'O código de rastreio da minha jaqueta não está funcionando.', 'OPEN', '2026-08-15 16:40:00'),
('55566677788', 'Quero alterar o endereço de entrega do meu pedido antes que seja enviado.', 'OPEN', '2026-08-17 10:00:00'),
('44455566677', 'Por que meu pedido foi cancelado?', 'RESOLVED', '2026-08-02 14:00:00');