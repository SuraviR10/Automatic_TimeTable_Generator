-- =====================================================
-- MIGRATION: Admin system + Open Elective + Global Settings
-- Run this in Supabase SQL Editor
-- =====================================================

-- 1. Global Settings table (admin-controlled, applies to whole system)
CREATE TABLE IF NOT EXISTS global_settings (
    id BIGSERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE global_settings ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on global_settings" ON global_settings;
CREATE POLICY "Allow all on global_settings" ON global_settings FOR ALL USING (true);

-- Insert MIT Mysore defaults (upsert so re-running is safe)
INSERT INTO global_settings (setting_key, setting_value) VALUES
  ('work_days',               '["Tuesday","Wednesday","Thursday","Friday","Saturday"]'),
  ('periods_per_day',         '6'),
  ('start_time',              '09:00'),
  ('end_time',                '16:00'),
  ('period_duration',         '60'),
  ('tea_break_start',         '11:00'),
  ('tea_break_end',           '11:15'),
  ('tea_break_after_period',  '2'),
  ('lunch_break_start',       '13:15'),
  ('lunch_break_end',         '14:00'),
  ('lunch_break_after_period','4')
ON CONFLICT (setting_key) DO NOTHING;

-- 2. Open Electives table (admin locks OE slot college-wide)
CREATE TABLE IF NOT EXISTS open_electives (
    id BIGSERIAL PRIMARY KEY,
    academic_year    VARCHAR(10)  NOT NULL,
    year             INTEGER      NOT NULL,
    semester         INTEGER      NOT NULL,
    oe_subject_code  VARCHAR(20)  NOT NULL,
    oe_subject_name  VARCHAR(100) NOT NULL,
    locked_day       VARCHAR(20)  NOT NULL,
    locked_time_slot INTEGER      NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(academic_year, year, semester, oe_subject_code)
);

ALTER TABLE open_electives ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on open_electives" ON open_electives;
CREATE POLICY "Allow all on open_electives" ON open_electives FOR ALL USING (true);

-- 3. Add is_open_elective flag to subjects (if not already there)
ALTER TABLE subjects ADD COLUMN IF NOT EXISTS is_open_elective BOOLEAN DEFAULT FALSE;
ALTER TABLE subjects ADD COLUMN IF NOT EXISTS classes_per_week  INTEGER DEFAULT NULL;

-- 4. Admin users table (separate from department users)
CREATE TABLE IF NOT EXISTS admin_users (
    id BIGSERIAL PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on admin_users" ON admin_users;
CREATE POLICY "Allow all on admin_users" ON admin_users FOR ALL USING (true);

-- Insert default admin (username: admin, password: Admin@1234)
INSERT INTO admin_users (username, password) VALUES ('admin', 'Admin@1234')
ON CONFLICT (username) DO NOTHING;

-- 5. Fix users table: some versions stored plain password in wrong column
ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(255);

-- 6. Timetable: add is_oe_locked column if missing
ALTER TABLE timetables ADD COLUMN IF NOT EXISTS is_oe_locked BOOLEAN DEFAULT FALSE;

-- Done
SELECT '✅ Migration complete' AS status;
