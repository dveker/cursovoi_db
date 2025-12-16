SELECT id FROM berths
WHERE id = %(berth_id)s
AND id NOT IN (
    SELECT berth_id FROM ship_registrations
    WHERE departure_date IS NULL
    AND berth_id IS NOT NULL
)