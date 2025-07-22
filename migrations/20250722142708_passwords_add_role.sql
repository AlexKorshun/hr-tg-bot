-- +goose Up
-- +goose StatementBegin
ALTER TABLE passwords
ADD COLUMN role role_enum DEFAULT 'candidate';
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE passwords
DROP COLUMN role;
-- +goose StatementEnd
