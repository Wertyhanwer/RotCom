CREATE TABLE IF NOT EXISTS private_chats(
	id SERIAL PRIMARY KEY,
	user1_id INT NOT NULL,
    user2_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_event_at TIMESTAMP DEFAULT NOW(),
    last_message TEXT
)


