SELECT s.name, st.type_name, sr.arrival_date, b.id as berth_id
FROM ship_registrations sr
JOIN ships s ON sr.ship_id = s.id
JOIN ship_types st ON s.ship_type_id = st.id
JOIN berths b ON sr.berth_id = b.id
WHERE sr.departure_date IS NULL