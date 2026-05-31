CREATE OR REPLACE TABLE "datovy_projekt_countries" AS

WITH "country_mapping" AS (
    SELECT 'CZ' AS "code", 'Czech Republic' AS "name" UNION ALL
    SELECT 'XC', 'Czechoslovakia' UNION ALL
    SELECT 'US', 'United States' UNION ALL
    SELECT 'GB', 'United Kingdom' UNION ALL
    SELECT 'FR', 'France' UNION ALL
    SELECT 'DE', 'Germany' UNION ALL
    SELECT 'SK', 'Slovakia' UNION ALL
    SELECT 'PL', 'Poland' UNION ALL
    SELECT 'IT', 'Italy' UNION ALL
    SELECT 'HU', 'Hungary' UNION ALL
    SELECT 'MX', 'Mexico' UNION ALL
    SELECT 'EE', 'Estonia'
),
"films" AS (
    SELECT
        CASE 
            WHEN "year" != 0 THEN CONCAT("title", '_', "year")
            ELSE "title"
        END AS "film_key",
        "title",
        CASE
            WHEN "production_countries" = '[]' OR "production_countries" = ''
            THEN CONCAT('[''', cm."name", ''']')
            ELSE "production_countries"
        END AS "production_countries"
    FROM "filmy_program_clean" fp
    LEFT JOIN "country_mapping" cm
        ON TRIM(REPLACE(REPLACE(fp."origin_country", '\\[|\\]', ''), '''', '')) = cm."code"
)
SELECT
    "film_key",
    "title",
    TRIM(REPLACE(REPLACE(value::STRING, '''', ''), '"', '')) AS "country"
FROM "films",
LATERAL FLATTEN(
    INPUT => SPLIT(
        REGEXP_REPLACE("production_countries", '\\[|\\]', ''),
        ', '
    )
)
WHERE TRIM(REPLACE(REPLACE(value::STRING, '''', ''), '"', '')) != ''