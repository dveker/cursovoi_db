-- Оборот кораблей по конкретному типу
SELECT
    st.type_name as ship_type,
    COUNT(DISTINCT s.id) as total_ships_of_type,
    COUNT(sr.id) as total_visits,
    AVG(s.tonnage) as avg_tonnage,
    AVG(TIMESTAMPDIFF(HOUR, sr.arrival_date, sr.departure_date)) as avg_stay_hours,
    SUM(CASE WHEN sr.departure_date IS NULL THEN 1 ELSE 0 END) as current_in_port,
    MIN(sr.arrival_date) as first_visit,
    MAX(sr.arrival_date) as last_visit
FROM ship_types st
LEFT JOIN ships s ON st.id = s.ship_type_id
LEFT JOIN ship_registrations sr ON s.id = sr.ship_id
    AND sr.arrival_date >= DATE_SUB(NOW(), INTERVAL 90 DAY)
WHERE st.type_name = %s
GROUP BY st.type_name