UPDATE ship_registrations
SET departure_date = NOW()
WHERE id = %s;

UPDATE unloading_teams
SET ship_registration_id = NULL
WHERE ship_registration_id = %s