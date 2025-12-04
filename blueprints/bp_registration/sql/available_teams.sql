SELECT
    ut.id,
    ut.team_name,
    COUNT(tm.employee_id) as member_count,
    GROUP_CONCAT(CONCAT(e.last_name, ' ', e.first_name, ' (', e.profession, ')') SEPARATOR ', ') as team_members
FROM unloading_teams ut
LEFT JOIN team_members tm ON ut.id = tm.team_id
LEFT JOIN employees e ON tm.employee_id = e.id
WHERE ut.ship_registration_id IS NULL
GROUP BY ut.id, ut.team_name
HAVING COUNT(tm.employee_id) > 0
ORDER BY ut.team_name