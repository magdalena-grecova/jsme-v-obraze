CREATE OR REPLACE TABLE "trend_queer_filmy" AS

WITH "parsed" AS (
    SELECT *,
        TRY_TO_DATE("showdate") AS "showdate_parsed"
    FROM "filmy_program_clean"
)
SELECT 
    DATE_TRUNC('month', "showdate_parsed") AS "mesic",
    COUNT(DISTINCT "title") AS "pocet_queer_filmu"
FROM "parsed"
WHERE "showdate_parsed" BETWEEN '2020-02-01' AND '2026-01-31'
    AND ("gay_theme" = 1 OR "lgbt" = 1 OR "queer" = 1 OR "lesbian_relationship" = 1 OR "male_homosexuality" = 1 OR "closeted_homosexual" = 1 OR "transgender" = 1 OR "transsexual" = 1 OR "drag_queen" = 1 OR "coming_out" = 1 OR "lgbt_teen" = 1 OR "homophobia" = 1 OR "gay_marriage" = 1 OR "gay" = 1 OR "lesby" = 1 OR "bisexualita" = 1 OR "homosexualita" = 1 OR "transsexuality" = 1 OR "transvestita" = 1)
GROUP BY DATE_TRUNC('month', "showdate_parsed")
ORDER BY "mesic";