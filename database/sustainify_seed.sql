
CREATE DATABASE sustainify;
USE sustainify;

CREATE TABLE users (
    id INT AUTO_INCREMENT,
    username VARCHAR(100),
    password VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

INSERT INTO users (username, password) VALUES
('admin01', 'pass123'),
('seller_jane', 'pass234'),
('buyer_mark', 'pass345'),
('donor_luis', 'pass456');

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
    type VARCHAR(50),
    quantity INT DEFAULT 1,
    price DECIMAL(10,2),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO items (user_id, title, description, condition, location, category, type, quantity, price)
VALUES
(2, 'Wooden Chair', 'Slightly scratched', 'Used', 'Lipa City', 'Furniture', 'Sell', 1, 350.00),
(2, 'Old Textbooks', '5 IT books bundle', 'Used', 'Batangas', 'Books', 'Donate', 5, 0.00),
(1, 'Laptop Sleeve', 'Good condition', 'Like New', 'Lipa City', 'Accessories', 'Swap', 1, 0.00);

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

INSERT INTO buyers (item_id, buyer_name, buyer_email, buyer_phone, quantity, payment_method, delivery_option, note, status, delivery_address)
VALUES
(1, 'Mark Reyes', 'mark@example.com', '09171234567', 1, 'Cash', 'Pickup', 'Please reserve it for me.', 'Pending', '123 Main St, Lipa City'),
(3, 'Ana Cruz', 'ana@example.com', '09179876543', 1, 'GCash', 'Delivery', NULL, 'Completed', '456 Batangas Rd, Batangas');

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

INSERT INTO donations (item_id, donor_name, donor_email, donor_phone, pickup_address, pickup_time, note, status)
VALUES
(2, 'Jane Doe', 'jane@example.com', '09171234567', '789 Barangay St, Lipa City', '2025-12-10 10:00:00', 'Bundle of IT books', 'Pending');

CREATE TABLE messages (
    id INT AUTO_INCREMENT,
    sender_id INT,
    receiver_id INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

INSERT INTO messages (sender_id, receiver_id, message)
VALUES
(1, 2, 'Hello Jane, is the wooden chair still available?'),
(2, 1, 'Yes, it is available. You can pick it up anytime.');

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

INSERT INTO notifications (user_id, message, link, read_status)
VALUES
(2, 'You have a new buyer inquiry for your item: Wooden Chair', 'item_details.php?id=1', 0),
(3, 'Your purchase of Laptop Sleeve has been completed', 'transaction_details.php?id=1', 1);

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

INSERT INTO ratings (rater_id, rated_id, item_id, rating, comment)
VALUES
(3, 2, 1, 5, 'Chair in good condition!'),
(2, 3, 3, 4, 'Laptop sleeve as described.');

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

INSERT INTO swaps (item_id, swapper_name, swapper_email, swapper_phone, offered_item, offered_item_condition, category, note, status)
VALUES
(3, 'Luis Torres', 'luis@example.com', '09171112222', 'Mouse Pad', 'New', 'Accessories', 'Would like to swap for your laptop sleeve', 'Pending');

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

INSERT INTO swap_requests (item_id, swapper_id, offered_item)
VALUES
(3, 3, 'USB Hub');

CREATE TABLE transactions (
    id INT AUTO_INCREMENT,
    item_id INT,
    type ENUM('Buy', 'Swap', 'Donate') DEFAULT NULL,
    user_from INT,
    user_to INT,
    quantity INT DEFAULT 1,
    status ENUM('Pending', 'Completed') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (user_from) REFERENCES users(id),
    FOREIGN KEY (user_to) REFERENCES users(id)
);

INSERT INTO transactions (item_id, type, user_from, user_to, quantity, status)
VALUES
(1, 'Buy', 2, 3, 1, 'Pending'),
(2, 'Donate', 2, 1, 5, 'Completed'),
(3, 'Swap', 3, 2, 1, 'Completed');
