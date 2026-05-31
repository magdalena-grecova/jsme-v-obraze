CREATE OR REPLACE TABLE "queer_filmy_dtb" AS
WITH "filtered_films" AS (
    SELECT DISTINCT
        fp."title",
        fp."original_title",
        fp."year",
        c."country",
        fp."runtime",
        fp."vote_average",
        fp."gay_theme", fp."lgbt", fp."queer", fp."lesbian_relationship",
        fp."male_homosexuality", fp."closeted_homosexual", fp."transgender",
        fp."transsexual", fp."drag_queen", fp."coming_out", fp."lgbt_teen",
        fp."homophobia", fp."gay_marriage", fp."gay", fp."lesby", fp."bisexualita",
        fp."homosexualita", fp."transsexuality", fp."transvestita"
    FROM "filmy_program_clean" fp
    JOIN "countries" c ON c."film_key" = CASE 
        WHEN fp."year" != 0 THEN CONCAT(fp."title", '_', fp."year")
        ELSE fp."title"
    END
    WHERE fp."showdate" BETWEEN '2020-02-01' AND '2026-01-31'
)
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'gay_theme' AS "tag"
FROM "filtered_films" WHERE "gay_theme" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'lgbt' AS "tag"
FROM "filtered_films" WHERE "lgbt" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'queer' AS "tag"
FROM "filtered_films" WHERE "queer" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'lesbian_relationship' AS "tag"
FROM "filtered_films" WHERE "lesbian_relationship" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'male_homosexuality' AS "tag"
FROM "filtered_films" WHERE "male_homosexuality" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'closeted_homosexual' AS "tag"
FROM "filtered_films" WHERE "closeted_homosexual" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'transgender' AS "tag"
FROM "filtered_films" WHERE "transgender" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'transsexual' AS "tag"
FROM "filtered_films" WHERE "transsexual" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'drag_queen' AS "tag"
FROM "filtered_films" WHERE "drag_queen" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'coming_out' AS "tag"
FROM "filtered_films" WHERE "coming_out" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'lgbt_teen' AS "tag"
FROM "filtered_films" WHERE "lgbt_teen" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'homophobia' AS "tag"
FROM "filtered_films" WHERE "homophobia" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'gay_marriage' AS "tag"
FROM "filtered_films" WHERE "gay_marriage" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'gay' AS "tag"
FROM "filtered_films" WHERE "gay" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'lesby' AS "tag"
FROM "filtered_films" WHERE "lesby" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'bisexualita' AS "tag"
FROM "filtered_films" WHERE "bisexualita" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'homosexualita' AS "tag"
FROM "filtered_films" WHERE "homosexualita" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'transsexuality' AS "tag"
FROM "filtered_films" WHERE "transsexuality" = 1
UNION ALL
SELECT "title", "original_title", "year", "country", "runtime", "vote_average", 'transvestita' AS "tag"
FROM "filtered_films" WHERE "transvestita" = 1