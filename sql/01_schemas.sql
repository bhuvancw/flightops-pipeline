IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'staging') EXEC ('CREATE SCHEMA staging');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'core') EXEC('CREATE SCHEMA core');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'mart') EXEC('CREATE SCHEMA mart');
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'ops') EXEC('CREATE SCHEMA ops');