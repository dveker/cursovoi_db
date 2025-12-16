SELECT
    s.*,
    st.type_name as ship_type_name,
    COUNT(sr.id) as total_trips,
    AVG(TIMESTAMPDIFF(HOUR, sr.arrival_date, sr.departure_date)) as avg_stay_hours
FROM ships s
LEFT JOIN ship_types st ON s.ship_type_id = st.id
LEFT JOIN ship_registrations sr ON s.id = sr.ship_id
WHERE s.id = %(ship_id)s
GROUP BY s.id, s.name