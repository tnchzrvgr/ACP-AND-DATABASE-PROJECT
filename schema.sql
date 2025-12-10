CREATE DATABASE sustainify;

CREATE TABLE users (
  id INT AUTO_INCREMENT,
  username VARCHAR(100),
  password VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (id)
);

CREATE TABLE buyers (
    id INT AUTO_INCREMENT,
    item_id INT,
    buyer_name VARCHAR(100),
    buyer_email VARCHAR(100),
    buyer_phone VARCHAR(50),
    quantity INT DEFAULT 1,
    payment_method ENUM('Cash', 'GCash', 'Bank Transfer') DEFAULT 'Cash',
    delivery_option ENUM('Pickup', 'Delivery') DEFAULT 'Pickup',
    note TEXT,
    status ENUM('Pending', 'Completed', 'Cancelled') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_address TEXT,
    PRIMARY KEY (id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);


CREATE TABLE donations (
    id INT AUTO_INCREMENT,
    item_id INT,
    donor_name VARCHAR(255),
    donor_email VARCHAR(255),
    donor_phone VARCHAR(50),
    pickup_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pickup_time DATETIME,
    note TEXT,
    status ENUM('Pending', 'Completed', 'Cancelled') DEFAULT 'Pending',
    PRIMARY KEY (id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE items (
    id INT AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(255),
    description TEXT,
    condition VARCHAR(100),
    location VARCHAR(100),
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(100),
    type VARCHAR(50) ,
    quantity INT(11) DEFAULT 1,
    price DECIMAL(10,2),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE messages (
    id INT NOT NULL AUTO_INCREMENT,
    sender_id INT,
    receiver_id INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (sender_id) REFERENCES users(id), 
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

CREATE TABLE notifications (
    id INT AUTO_INCREMENT,
    user_id INT,
    message TEXT,
    link VARCHAR(255),
    read_status TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE ratings (
    id INT AUTO_INCREMENT,
    rater_id INT,
    rated_id INT,
    item_id INT,
    rating INT,
    comment TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (rater_id) REFERENCES users(id),
    FOREIGN KEY (rated_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE swaps (
    id INT AUTO_INCREMENT,
    item_id INT,
    swapper_name VARCHAR(255),
    swapper_email VARCHAR(255),
    swapper_phone VARCHAR(50),
    offered_item VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    offered_item_condition ENUM('New', 'Like New', 'Used') DEFAULT 'Used',
    category VARCHAR(50),
    note TEXT,
    status ENUM('Pending', 'Accepted', 'Rejected') DEFAULT 'Pending',
    PRIMARY KEY (id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE swap_requests (
    id INT AUTO_INCREMENT,
    item_id INT,
    swapper_id INT,
    offered_item VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (swapper_id) REFERENCES users(id)
);

CREATE TABLE transactions (
  id INT AUTO_INCREMENT,
  item_id INT,
  type ENUM('Buy', 'Swap', 'Donate') DEFAULT NULL,
  user_from INT,
  user_to INT,
  quantity INT DEFAULT 1,
  status ENUM('Pending', 'Completed') DEFAULT 'Pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (id),
  FOREIGN KEY (item_id) REFERENCES items(id),
  FOREIGN KEY (user_from) REFERENCES users(id),
  FOREIGN KEY (user_to) REFERENCES users(id)
);

INSERT INTO users (username, password) VALUES
('admin01', 'pass123'),
('seller_jane', 'pass234'),
('buyer_mark', 'pass345'),
('donor_luis', 'pass456');

INSERT INTO items (user_id, title, description, `condition`, location, category, type, quantity, price) VALUES
(2, 'Wooden Chair', 'Slightly scratched', 'Used', 'Lipa City', 'Furniture', 'Sell', 1, 350.00),
(2, 'Old Textbooks', '5 IT books bundle', 'Used', 'Batangas', 'Books', 'Donate', 5, 0.00),
(1, 'Mouse', 'Good condition', 'Like New', 'Lipa City', 'Electronics', 'Swap', 1, 0.00);

SELECT * FROM users;

UPDATE items
SET quantity = 2
WHERE title = 'Wooden Chair';

DELETE FROM items
WHERE title = 'Old Textbooks';

SELECT b.buyer_name, i.title AS item_name, u.username AS seller_name, b.quantity
FROM buyers b
JOIN items i ON b.item_id = i.id
JOIN users u ON i.user_id = u.id;

SELECT category, COUNT(*) AS total_items
FROM items
GROUP BY category;

SELECT title
FROM items
WHERE id NOT IN (SELECT item_id FROM buyers);



