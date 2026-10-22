-- Person-year histories already link stable identity to that wave's family ID.
-- Early/prime ages refer to interview age; income is for the previous calendar year.
CREATE TEMP TABLE prime_mean AS
SELECT pid, AVG(income_real) AS avg_income, COUNT(*) AS n_years
FROM panel WHERE age BETWEEN 35 AND 44
GROUP BY pid HAVING COUNT(*) >= 3;

CREATE TEMP TABLE prime_one AS
SELECT pid,income_real AS income_one,age FROM (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY pid ORDER BY ABS(age-40),wave) AS rn
 FROM panel WHERE age BETWEEN 35 AND 44
) WHERE rn=1;

CREATE TEMP TABLE early_one AS
SELECT pid,income_real AS income_early,age AS age_early FROM (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY pid ORDER BY ABS(age-27),wave) AS rn
 FROM panel WHERE age BETWEEN 25 AND 29
) WHERE rn=1;

-- Aggregate within people FIRST, then join generations to avoid multiplying years.
CREATE TEMP TABLE matched AS
SELECT l.child_pid,l.parent_pid,c.avg_income AS child_avg,p.avg_income AS parent_avg,
       co.income_one AS child_one,po.income_one AS parent_one,
       e.income_early AS child_early,c.n_years AS child_years,p.n_years AS parent_years,
       co.age AS child_age,po.age AS parent_age,e.age_early
FROM links l
JOIN prime_mean c ON c.pid=l.child_pid
JOIN prime_mean p ON p.pid=l.parent_pid
JOIN prime_one co ON co.pid=l.child_pid
JOIN prime_one po ON po.pid=l.parent_pid
JOIN early_one e ON e.pid=l.child_pid;
