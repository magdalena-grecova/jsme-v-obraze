CREATE OR REPLACE TABLE "nejcastejsi_zanr" AS
    WITH "queer_filmy" AS (
    SELECT
        CASE 
            WHEN "year" != 0 THEN CONCAT("title", '_', "year")
            ELSE "title"
        END AS "film_key",
        "title"
    FROM "filmy_program_clean"
    WHERE ("gay_theme" = 1 OR "lgbt" = 1 OR "queer" = 1 OR "lesbian_relationship" = 1 OR "male_homosexuality" = 1 OR "closeted_homosexual" = 1 OR "transgender" = 1 OR "transsexual" = 1 OR "drag_queen" = 1 OR "coming_out" = 1 OR "lgbt_teen" = 1 OR "homophobia" = 1 OR "gay_marriage" = 1 OR "gay" = 1 OR "lesby" = 1 OR "bisexualita" = 1 OR "homosexualita" = 1 OR "transsexuality" = 1 OR "transvestita" = 1)
        AND "showdate" BETWEEN '2020-02-01' AND '2026-01-31'
)
SELECT g."genre", COUNT(DISTINCT g."title") AS "pocet_filmu"
FROM "genres" g
INNER JOIN "queer_filmy" qf ON g."film_key" = qf."film_key"
WHERE g."genre" != ''
GROUP BY g."genre"
ORDER BY "pocet_filmu" DESC;