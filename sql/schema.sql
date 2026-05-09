-- schema.sql for SQLite database

-- Drop tables if they exist (for clean re-runs)
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS patents;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;

-- Create patents table
CREATE TABLE patents (
    patent_id TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    filing_date TEXT,
    year INTEGER
);

-- Create inventors table
CREATE TABLE inventors (
    inventor_id TEXT PRIMARY KEY,
    name TEXT,
    country TEXT
);

-- Create companies table
CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    name TEXT
);

-- Create relationships table
CREATE TABLE relationships (
    patent_id TEXT,
    inventor_id TEXT,
    company_id TEXT,
    FOREIGN KEY (patent_id) REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- Create indexes for query performance
CREATE INDEX idx_patents_year ON patents(year);
CREATE INDEX idx_relationships_patent ON relationships(patent_id);
CREATE INDEX idx_relationships_inventor ON relationships(inventor_id);
CREATE INDEX idx_relationships_company ON relationships(company_id);