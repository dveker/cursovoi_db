SELECT
    sr.id as registration_id,
    s.name as ship_name,
    s.ship_type_id,
    sr.arrival_date,
    ut.id as team_id,
    ut.team_name,
    CONCAT(e.last_name, ' ', e.first_name) as pilot_name
FROM ship_registrations sr
JOIN ships s ON sr.ship_id = s.id
JOIN unloading_teams ut ON sr.id = ut.ship_registration_id
LEFT JOIN employees e ON sr.employee_id = e.id
WHERE sr.departure_date IS NULL
ORDER BY sr.arrival_date