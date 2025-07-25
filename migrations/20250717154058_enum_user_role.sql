-- +goose Up
-- +goose StatementBegin
CREATE TYPE role_enum AS ENUM ('candidate', 'worker', 'admin');
-- +goose StatementEnd

-- +goose StatementBegin
ALTER TABLE users 
ALTER COLUMN role DROP DEFAULT,
ALTER COLUMN role TYPE role_enum USING role::role_enum,
ALTER COLUMN role SET DEFAULT 'candidate';
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE users
ALTER COLUMN role DROP DEFAULT,
ALTER COLUMN role TYPE VARCHAR USING role::text,
ALTER COLUMN role SET DEFAULT 'candidate';
-- +goose StatementEnd

-- +goose StatementBegin
DROP TYPE role_enum;
-- +goose StatementEnd
