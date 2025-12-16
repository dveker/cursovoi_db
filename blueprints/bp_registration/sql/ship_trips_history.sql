SELECT
    sr.*,
    b.id as berth_id,
    bt.type_name as berth_type,
    ut.team_name,
    CONCAT(e.last_name, ' ', e.first_name) as employee_name,
    TIMESTAMPDIFF(HOUR, sr.arrival_date, sr.departure_date) as stay_hours
FROM ship_registrations sr
LEFT JOIN berths b ON sr.berth_id = b.id
LEFT JOIN berth_types bt ON b.berth_type_id = bt.id
LEFT JOIN unloading_teams ut ON sr.id = ut.ship_registration_id
LEFT JOIN employees e ON sr.employee_id = e.id
WHERE sr.ship_id = %(ship_id)s
ORDER BY sr.arrival_date DESC