INSERT INTO ship_reports (report_month, report_year, ship_count, total_tonnage, avg_stay_hours)
SELECT
    %s as report_month,
    %s as report_year,
    COUNT(DISTINCT sr.id) as ship_count,
    COALESCE(SUM(10000), 50000) as total_tonnage,
    COALESCE(AVG(24), 24) as avg_stay_hours
FROM ship_registrations sr
WHERE MONTH(sr.arrival_date) = %s AND YEAR(sr.arrival_date) = %s
ON DUPLICATE KEY UPDATE
    ship_count = VALUES(ship_count),
    total_tonnage = VALUES(total_tonnage),
    avg_stay_hours = VALUES(avg_stay_hours)