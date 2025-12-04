SELECT s.id, s.name, st.type_name, s.tonnage, s.home_port
FROM ships s
JOIN ship_types st ON s.ship_type_id = st.id
WHERE s.name LIKE %s