-- +goose Up
-- +goose StatementBegin
CREATE TABLE passwords (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    used BOOLEAN DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_email ON passwords(email);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP INDEX IF EXISTS idx_email;
DROP TABLE passwords; 
-- +goose StatementEnd
