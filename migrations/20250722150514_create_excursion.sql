-- +goose Up
-- +goose StatementBegin
CREATE TABLE excursions (
    id SERIAL PRIMARY KEY,
    admin_id BIGINT UNIQUE NOT NULL,
    date TIMESTAMP NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE excursions;
-- +goose StatementEnd
