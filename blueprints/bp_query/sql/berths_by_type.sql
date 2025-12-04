SELECT b.id, bt.type_name, b.length, b.depth
FROM berths b
JOIN berth_types bt ON b.berth_type_id = bt.id
WHERE bt.type_name = %s