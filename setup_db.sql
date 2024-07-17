\c word_a_day;
CREATE TABLE IF NOT EXISTS words(
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) UNIQUE NOT NULL,
    freq FLOAT(9)
);
