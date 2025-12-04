SELECT id, first_name, last_name, profession, hire_date
FROM employees
WHERE first_name LIKE %s OR last_name LIKE %s