-- +goose Up
-- +goose StatementBegin
DELETE FROM excursion_registrations
WHERE id IN (
    SELECT id
    FROM (
        SELECT
            id,
            ROW_NUMBER() OVER (PARTITION BY excursion_id, user_telegram_id ORDER BY created_at, id) as rn
        FROM
            excursion_registrations
    ) AS subquery
    WHERE subquery.rn > 1
);

ALTER TABLE excursion_registrations
ADD CONSTRAINT unique_excursion_user UNIQUE (excursion_id, user_telegram_id);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE excursion_registrations
DROP CONSTRAINT unique_excursion_user;
-- +goose StatementEnd