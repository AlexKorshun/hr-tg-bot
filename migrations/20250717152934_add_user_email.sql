-- +goose Up
-- +goose StatementBegin
ALTER TABLE users
ADD COLUMN email TEXT UNIQUE;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE users
DROP COLUMN email;
-- +goose StatementEnd
