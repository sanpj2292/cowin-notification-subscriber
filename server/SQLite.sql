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

SELECT district_name, count(district_name) FROM districts
GROUP BY district_name
HAVING count(district_name) > 1

-- SELECT * FROM districts
-- where district_name = 'Bilaspur'

--Role update for cloud sql postgres
GRANT USAGE ON SCHEMA "public" TO postgres;
GRANT SELECT ON ALL TABLES IN SCHEMA "public" TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA "public" GRANT SELECT ON TABLES TO postgres;