SELECT current_catalog() AS catalog_name, current_schema() AS schema_name;

CREATE SCHEMA IF NOT EXISTS workspace.it_capstone;

CREATE VOLUME IF NOT EXISTS workspace.it_capstone.raw_files;

CREATE TABLE IF NOT EXISTS workspace.it_capstone.employees (
  employee_id  STRING,
  full_name    STRING,
  department   STRING,
  location     STRING,
  is_active    BOOLEAN
);

CREATE TABLE IF NOT EXISTS workspace.it_capstone.assets (
  asset_id      STRING,
  asset_type    STRING,
  model         STRING,
  purchase_date DATE,
  warranty_end  DATE,
  status        STRING
);

CREATE TABLE IF NOT EXISTS workspace.it_capstone.asset_assignments (
  assignment_id INT,
  asset_id      STRING,
  employee_id   STRING,
  action        STRING,
  action_date   DATE,
  note          STRING,
  updated_by    STRING
);

SHOW TABLES IN workspace.it_capstone;

TRUNCATE TABLE workspace.it_capstone.employees;
TRUNCATE TABLE workspace.it_capstone.assets;
TRUNCATE TABLE workspace.it_capstone.asset_assignments;

INSERT INTO workspace.it_capstone.employees VALUES
  ('E001','Asha Rao','Finance','Bengaluru',true),
  ('E002','Ravi Kumar','Sales','Chennai',true),
  ('E003','Meena Iyer','HR','Bengaluru',true),
  ('E004','John Paul','Sales','Chennai',false),
  ('E005','Divya Nair','IT','Bengaluru',true);

INSERT INTO workspace.it_capstone.assets VALUES
  ('A001','Laptop','Dell Latitude 5440','2024-02-10','2027-02-10','Assigned'),
  ('A002','Laptop','Dell Latitude 5440','2024-02-10','2027-02-10','Assigned'),
  ('A003','Laptop','HP EliteBook 840','2023-06-15','2026-12-15','Assigned'),
  ('A004','Laptop','Lenovo T14','2025-01-20','2028-01-20','Available'),
  ('A005','Monitor','Dell U2723','2023-09-01','2026-11-30','Assigned'),
  ('A006','Monitor','Dell U2723','2023-09-01','2026-11-30','Available'),
  ('A007','Phone','iPhone 14','2024-05-05','2026-05-05','Repair');

INSERT INTO workspace.it_capstone.asset_assignments VALUES
  (1,'A001','E001','Assign','2024-02-15','New joiner','priya'),
  (2,'A002','E002','Assign','2024-03-01','Sales laptop','priya'),
  (3,'A003','E004','Assign','2023-07-01','Sales laptop','priya'),
  (4,'A005','E003','Assign','2023-09-10','Desk setup','priya'),
  (5,'A006','E005','Assign','2024-01-10','Test monitor','priya'),
  (6,'A006','E005','Return','2025-06-01','Returned','priya');

SELECT employee_id, full_name, department, location, is_active
FROM workspace.it_capstone.employees;

SELECT asset_id, asset_type, model, purchase_date, warranty_end, status
FROM workspace.it_capstone.assets;

SELECT assignment_id, asset_id, employee_id, action, action_date, note, updated_by
FROM workspace.it_capstone.asset_assignments;

SELECT 'employees' AS table_name, COUNT(*) AS row_count FROM workspace.it_capstone.employees
UNION ALL
SELECT 'assets', COUNT(*) FROM workspace.it_capstone.assets
UNION ALL
SELECT 'asset_assignments', COUNT(*) FROM workspace.it_capstone.asset_assignments;

CREATE OR REPLACE VIEW workspace.it_capstone.v_available_laptops AS
SELECT asset_id, model, purchase_date, warranty_end
FROM workspace.it_capstone.assets
WHERE asset_type = 'Laptop'
    AND status = 'Available';

SELECT asset_id, model, warranty_end
FROM workspace.it_capstone.v_available_laptops
ORDER BY warranty_end;

CREATE OR REPLACE VIEW workspace.it_capstone.v_current_holdings AS
SELECT asset_id, employee_id, action_date
FROM (
  SELECT
    asset_id,
    employee_id,
    action,
    action_date,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id
      ORDER BY action_date DESC, assignment_id DESC
    ) AS rn
  FROM workspace.it_capstone.asset_assignments
) latest
WHERE rn = 1
  AND action = 'Assign';

--QUERIES SAMPLE
-- Q1 (filter): Which laptops are available to give out?
SELECT asset_id, model, purchase_date, warranty_end
FROM workspace.it_capstone.assets
WHERE asset_type = 'Laptop'
  AND status = 'Available'
ORDER BY purchase_date;

-- Q2 (joins): Who currently holds which asset?
SELECT
  a.asset_id,
  a.asset_type,
  a.model,
  e.full_name,
  e.department,
  h.action_date AS assigned_on
FROM workspace.it_capstone.v_current_holdings h
JOIN workspace.it_capstone.assets a ON a.asset_id = h.asset_id
JOIN workspace.it_capstone.employees e ON e.employee_id = h.employee_id
ORDER BY e.full_name;

-- Q3 (aggregate): How many assets per type and status?
SELECT
  asset_type,
  status,
  COUNT(*) AS asset_count
FROM workspace.it_capstone.assets
GROUP BY asset_type, status
ORDER BY asset_type, asset_count DESC;

-- Q4 (join + aggregate): How many assets does each department hold?
SELECT
  e.department,
  COUNT(h.asset_id) AS assets_held
FROM workspace.it_capstone.employees e
LEFT JOIN workspace.it_capstone.v_current_holdings h
  ON h.employee_id = e.employee_id
GROUP BY e.department
ORDER BY assets_held DESC;

-- Q5 (filter + join): Which assets are still held by inactive employees?
SELECT
  a.asset_id,
  a.model,
  e.full_name,
  e.department,
  h.action_date AS assigned_on
FROM workspace.it_capstone.v_current_holdings h
JOIN workspace.it_capstone.assets a ON a.asset_id = h.asset_id
JOIN workspace.it_capstone.employees e ON e.employee_id = h.employee_id
WHERE e.is_active = false
ORDER BY h.action_date;


--- ROW FILTER SQL - Session 8 ----------
SELECT employee_id, full_name, department, location, current_user() AS running_as
FROM workspace.it_capstone.employees
ORDER BY employee_id
LIMIT :row_limit

----Session 9: GRANTS & AUDITS------
GRANT SELECT ON TABLE workspace.it_capstone.assets TO `<SERVICE_PRINCIPAL>`;
GRANT SELECT ON TABLE workspace.it_capstone.employees TO `<SERVICE_PRINCIPAL>`;
GRANT SELECT ON TABLE workspace.it_capstone.asset_assignments TO `<SERVICE_PRINCIPAL>`;

GRANT USE CATALOG ON CATALOG workspace TO `<SERVICE_PRINCIPAL>`;

GRANT USE SCHEMA ON SCHEMA workspace.it_capstone TO `<SERVICE_PRINCIPAL>`;

show grants on catalog workspace;

show grants on schema workspace.it_capstone;

SHOW GRANTS ON TABLE workspace.it_capstone.assets;

SHOW GRANTS ON TABLE workspace.it_capstone.employees;

SHOW GRANTS ON TABLE workspace.it_capstone.asset_assignments;

show schemas in system;

SELECT event_time, service_name, action_name, user_identity.email AS actor
FROM system.access.audit
WHERE event_date >= current_date() - 7
  AND user_identity.email = '<SERVICE_PRINCIPAL>'
  AND service_name = 'workspace'
ORDER BY event_time DESC
LIMIT 100;

SELECT service_name, action_name, COUNT(*) AS event_count
FROM system.access.audit
WHERE event_date >= current_date() - 7
  AND user_identity.email = '<SERVICE_PRINCIPAL>'
GROUP BY service_name, action_name
ORDER BY event_count DESC
LIMIT 20;