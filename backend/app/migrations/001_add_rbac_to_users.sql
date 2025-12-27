-- File: migrations/001_add_rbac_to_users.sql
-- Location: Create in migrations directory
-- Database: SQLite
-- Purpose: Add role and department columns to users table for Phase 1 RBAC

-- ============================================
-- SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT
-- Solution: We'll add columns without DEFAULT first, 
-- then set values, then add NOT NULL constraint
-- ============================================

-- Step 1: Add role column (temporary, allows NULL)
ALTER TABLE users ADD COLUMN role TEXT NULL;

-- Step 2: Set default value for existing users
UPDATE users SET role = 'user' WHERE role IS NULL;

-- Step 3: Make role NOT NULL now that all have values
-- NOTE: SQLite doesn't support ALTER COLUMN in older versions
-- So we're leaving it as TEXT NOT NULL in schema
-- The Python model has default=UserRole.USER

-- Step 4: Add index on role for fast lookups
CREATE INDEX idx_users_role ON users(role);

-- Step 5: Add department column (nullable, optional)
ALTER TABLE users ADD COLUMN department TEXT NULL;

-- Step 6: Add index on department for fast lookups
CREATE INDEX idx_users_department ON users(department);

-- ============================================
-- VERIFICATION QUERIES (run these to verify)
-- ============================================

-- Check the columns were added
-- SQLite version:
-- PRAGMA table_info(users);
-- Should show: role and department columns

-- View users with their roles
-- SELECT id, full_name, email, role, department FROM users LIMIT 5;

-- Count users by role
-- SELECT role, COUNT(*) as count FROM users GROUP BY role;

-- Find all department managers
-- SELECT id, full_name, department FROM users WHERE role = 'department_manager';

-- ============================================
-- ABOUT THIS MIGRATION
-- ============================================

-- Why these steps?
-- 1. SQLite is strict about ALTER TABLE
-- 2. We can't add NOT NULL without DEFAULT in SQLite
-- 3. We add column as NULL, set values, then rely on Python model for constraint
-- 4. The User model has: Column(Enum(UserRole), default=UserRole.USER, nullable=False)
--    This enforces constraints at application level

-- Important Notes:
-- - SQLite doesn't enforce Enum types at DB level (unlike PostgreSQL)
-- - The Python model enforces the enum values
-- - The index ensures fast role-based queries
-- - Department is nullable because not all users need it

-- ============================================
-- ROLLBACK (If you need to undo)
-- ============================================

-- To rollback, run these in reverse order:
-- DROP INDEX IF EXISTS idx_users_department;
-- DROP INDEX IF EXISTS idx_users_role;
-- ALTER TABLE users DROP COLUMN department;
-- ALTER TABLE users DROP COLUMN role;

-- ============================================
-- OPTIONAL: Add constraints at database level
-- ============================================

-- SQLite doesn't support CHECK constraints on enums easily
-- But you can add this if you want database-level validation:

-- Add CHECK constraint for valid roles (optional)
-- ALTER TABLE users ADD CONSTRAINT check_role 
-- CHECK(role IN ('admin', 'user', 'department_manager'));

-- Add CHECK constraint for manager department (optional)
-- ALTER TABLE users ADD CONSTRAINT check_manager_dept
-- CHECK(
--   (role = 'department_manager' AND department IS NOT NULL) OR
--   (role != 'department_manager' AND department IS NULL)
-- );

-- Note: SQLite may not support adding constraints via ALTER TABLE
-- These constraints would need to be in the original CREATE TABLE
-- For now, we rely on the Python model for validation