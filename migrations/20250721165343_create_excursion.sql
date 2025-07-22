-- +goose Up
-- +goose StatementBegin
CREATE TABLE users ( -- TODO: сделать табличку
)
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE users;
-- +goose StatementEnd
