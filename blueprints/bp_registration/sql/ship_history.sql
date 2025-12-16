
SELECT
    s.id as ship_id,
    s.name as ship_name,
    st.type_name as ship_type,
    s.tonnage,
    s.home_port,
    sr.id as registration_id,
    sr.arrival_date,
    sr.departure_date,
    b.id as berth_id,
    bt.type_name as berth_type,
    ut.team_name,
    TIMESTAMPDIFF(HOUR, sr.arrival_date, sr.departure_date) as stay_hours,
    CASE
        WHEN sr.departure_date IS NULL THEN 'В порту'
        ELSE 'Ушел'
    END as status
FROM ships s
LEFT JOIN ship_types st ON s.ship_type_id = st.id
LEFT JOIN ship_registrations sr ON s.id = sr.ship_id
LEFT JOIN berths b ON sr.berth_id = b.id
LEFT JOIN berth_types bt ON b.berth_type_id = bt.id
LEFT JOIN unloading_teams ut ON sr.id = ut.ship_registration_id
ORDER BY sr.arrival_date DESC, s.name