-- +goose Up
-- +goose StatementBegin
ALTER TABLE users
  DROP CONSTRAINT IF EXISTS users_email_key;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_id
  ON users (telegram_id);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP INDEX IF EXISTS idx_users_telegram_id;

ALTER TABLE users
  ADD CONSTRAINT users_email_key UNIQUE (email);
-- +goose StatementEnd
