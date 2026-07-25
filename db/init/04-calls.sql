CREATE TYPE IF NOT EXISTS call_status AS ENUM ('answered', 'missed');

CREATE TABLE IF NOT EXISTS calls(
	id SERIAL PRIMARY KEY,
	chat_id INT NOT NULL,
    caller_id INT NOT NULL,
	status call_status NOT NULL,
	duration INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
)


