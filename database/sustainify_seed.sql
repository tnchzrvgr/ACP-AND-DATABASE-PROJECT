INSERT INTO users (username, password) VALUES
('admin01', 'pass123'),
('seller_jane', 'pass234'),
('buyer_mark', 'pass345'),
('donor_luis', 'pass456');

INSERT INTO items (user_id, title, description, condition, location, category, type, quantity, price)
VALUES
(2, 'Wooden Chair', 'Slightly scratched', 'Used', 'Lipa City', 'Furniture', 'Sell', 1, 350.00),
(2, 'Old Textbooks', '5 IT books bundle', 'Used', 'Batangas', 'Books', 'Donate', 5, 0.00),
(1, 'Laptop Sleeve', 'Good condition', 'Like New', 'Lipa City', 'Accessories', 'Swap', 1, 0.00);

INSERT INTO buyers (item_id, buyer_name, buyer_email, buyer_phone, quantity, payment_method, delivery_option, note, status, delivery_address)
VALUES
(1, 'Mark Reyes', 'mark@example.com', '09171234567', 1, 'Cash', 'Pickup', 'Please reserve it for me.', 'Pending', '123 Main St, Lipa City'),
(3, 'Ana Cruz', 'ana@example.com', '09179876543', 1, 'GCash', 'Delivery', NULL, 'Completed', '456 Batangas Rd, Batangas');

INSERT INTO donations (item_id, donor_name, donor_email, donor_phone, pickup_address, pickup_time, note, status)
VALUES
(2, 'Jane Doe', 'jane@example.com', '09171234567', '789 Barangay St, Lipa City', '2025-12-10 10:00:00', 'Bundle of IT books', 'Pending');

INSERT INTO messages (sender_id, receiver_id, message)
VALUES
(1, 2, 'Hello Jane, is the wooden chair still available?'),
(2, 1, 'Yes, it is available. You can pick it up anytime.');

INSERT INTO notifications (user_id, message, link, read_status)
VALUES
(2, 'You have a new buyer inquiry for your item: Wooden Chair', 'item_details.php?id=1', 0),
(3, 'Your purchase of Laptop Sleeve has been completed', 'transaction_details.php?id=1', 1);

INSERT INTO ratings (rater_id, rated_id, item_id, rating, comment)
VALUES
(3, 2, 1, 5, 'Chair in good condition!'),
(2, 3, 3, 4, 'Laptop sleeve as described.');

INSERT INTO swaps (item_id, swapper_name, swapper_email, swapper_phone, offered_item, offered_item_condition, category, note, status)
VALUES
(3, 'Luis Torres', 'luis@example.com', '09171112222', 'Mouse Pad', 'New', 'Accessories', 'Would like to swap for your laptop sleeve', 'Pending');

INSERT INTO swap_requests (item_id, swapper_id, offered_item)
VALUES
(3, 3, 'USB Hub');

INSERT INTO transactions (item_id, type, user_from, user_to, quantity, status)
VALUES
(1, 'Buy', 2, 3, 1, 'Pending'),
(2, 'Donate', 2, 1, 5, 'Completed'),
(3, 'Swap', 3, 2, 1, 'Completed');
