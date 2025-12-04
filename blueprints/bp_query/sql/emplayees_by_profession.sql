SELECT id, first_name, last_name, hire_date
FROM employees
WHERE profession = %s AND dismissal_date IS NULL