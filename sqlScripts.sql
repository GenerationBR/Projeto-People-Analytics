USE generation;
SELECT * FROM emp_find_jobs_robot;

SELECT *
FROM emp_find_jobs_robot
WHERE LOWER(description) LIKE '%afirmativ%'
  AND (
      LOWER(description) LIKE '%mulher%'
      OR LOWER(description) LIKE '%feminin%'
  );
