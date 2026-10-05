-- 00_create_schemas.sql
-- Initializes the logical schemas for the DISCHARGE project in PostgreSQL
-- Reference: AGENTS.md §8 and docs/database_schema.md

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS features;
CREATE SCHEMA IF NOT EXISTS ml;
CREATE SCHEMA IF NOT EXISTS analytics;
