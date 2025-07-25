-- +goose Up
-- +goose StatementBegin
ALTER TABLE users ADD COLUMN last_use TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE users DROP COLUMN last_use;
-- +goose StatementEnd