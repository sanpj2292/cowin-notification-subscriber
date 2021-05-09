-- SQLite

-- DELETE FROM subscribers;
-- VACUUM
-- DROP TABLE subscribers

select * FROM states;
select * FROM districts;
select * FROM subscribers;

SELECT 
subscribers.district_id AS subscribers_district_id, 
count(subscribers.district_id) AS count_1
FROM subscribers 
GROUP BY subscribers.district_id


SELECT DISTINCT district_id from subscribers

DELETE FROM subscribers WHERE id=3