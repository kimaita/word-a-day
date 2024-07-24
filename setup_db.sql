\c word_a_day;
-- GRANT pg_read_all_data TO "word_a_day_dev";
-- GRANT pg_write_all_data TO "word_a_day_dev";
CREATE TABLE IF NOT EXISTS words(
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) UNIQUE NOT NULL,
    freq FLOAT(9)
);
CREATE TABLE IF NOT EXISTS visitors(
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(16) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS word_history(
    day DATE NOT NULL,
    word_id INT,
    CONSTRAINT fk_whistory_word FOREIGN KEY(word_id) REFERENCES words(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS visitor_history(
    day DATE NOT NULL,
    word_id INT,
    visitor_id INT,
    CONSTRAINT fk_vhistory_visitor FOREIGN KEY(visitor_id) REFERENCES visitors(id) ON DELETE CASCADE,
    CONSTRAINT fk_vhistory_word FOREIGN KEY(word_id) REFERENCES words(id) ON DELETE CASCADE
);