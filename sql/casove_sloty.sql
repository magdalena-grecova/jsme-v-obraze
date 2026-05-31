CREATE OR REPLACE TABLE "casove_sloty" AS
SELECT CASE 
    WHEN "showtime" BETWEEN '00:00:00' AND '05:59:00' THEN 'noc'
    WHEN "showtime" BETWEEN '06:00:00' AND '08:59:00' THEN 'ranní vysílání'
    WHEN "showtime" BETWEEN '09:00:00' AND '11:59:00' THEN 'dopoledne'
    WHEN "showtime" BETWEEN '12:00:00' AND '13:59:00' THEN 'poledne'
    WHEN "showtime" BETWEEN '14:00:00' AND '17:59:00' THEN 'odpoledne'
    WHEN "showtime" BETWEEN '18:00:00' AND '19:59:00' THEN 'předprimetime'
    WHEN "showtime" BETWEEN '20:00:00' AND '22:59:00' THEN 'primetime'
    WHEN "showtime" BETWEEN '23:00:00' AND '23:59:00' THEN 'pozdní vysílání'
    END AS "time_slot"
    , COUNT("showtime") "pocet_vysilani"
FROM "filmy_program_clean"
WHERE (
    "gay_theme" = 1 OR "lgbt" = 1 OR "queer" = 1 OR "lesbian_relationship" = 1 OR "male_homosexuality" = 1 OR "closeted_homosexual" = 1 OR "transgender" = 1 OR "transsexual" = 1 OR "drag_queen" = 1 OR "coming_out" = 1 OR "lgbt_teen" = 1 OR "homophobia" = 1 OR "gay_marriage" = 1 OR "gay" = 1 OR "lesby" = 1 OR "bisexualita" = 1 OR "homosexualita" = 1 OR "transsexuality" = 1 OR "transvestita" = 1) 
    AND "showdate" BETWEEN '2020-02-01' AND '2026-01-31'
GROUP BY "time_slot"
ORDER BY "pocet_vysilani" DESC;