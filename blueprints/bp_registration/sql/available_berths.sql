SELECT
    b.id,
    b.berth_type_id,
    bt.type_name as berth_type,
    b.length,
    b.depth,
    CASE
        WHEN sr.id IS NOT NULL AND sr.departure_date IS NULL THEN 'Занят'
        ELSE 'Свободен'
    END as status
FROM berths b
LEFT JOIN berth_types bt ON b.berth_type_id = bt.id
LEFT JOIN ship_registrations sr ON b.id = sr.berth_id
    AND sr.departure_date IS NULL
WHERE sr.id IS NULL OR sr.departure_date IS NOT NULL
ORDER BY b.id