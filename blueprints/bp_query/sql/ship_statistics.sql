SELECT
    s.name as ship_name,
    st.type_name as ship_type,
    COUNT(sr.id) as total_visits,
    AVG(DATEDIFF(COALESCE(sr.departure_date, CURDATE()), sr.arrival_date)) as avg_stay_days,
    MAX(sr.arrival_date) as last_visit_date
FROM ships s
JOIN ship_types st ON s.ship_type_id = st.id
LEFT JOIN ship_registrations sr ON s.id = sr.ship_id
WHERE sr.arrival_date BETWEEN %s AND %s
GROUP BY s.id, s.name, st.type_name
ORDER BY total_visits DESC