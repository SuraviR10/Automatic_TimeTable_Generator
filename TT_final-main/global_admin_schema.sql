-- Global Settings Table for Admin Control
CREATE TABLE IF NOT EXISTS global_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(100)
);

-- Insert default MIT Mysore settings
INSERT INTO global_settings (setting_key, setting_value, updated_by) VALUES
('work_days', '["Tuesday","Wednesday","Thursday","Friday","Saturday"]', 'SYSTEM'),
('start_time', '09:00', 'SYSTEM'),
('end_time', '16:00', 'SYSTEM'),
('period_duration', '60', 'SYSTEM'),
('tea_break_start', '11:00', 'SYSTEM'),
('tea_break_end', '11:15', 'SYSTEM'),
('lunch_break_start', '13:15', 'SYSTEM'),
('lunch_break_end', '14:00', 'SYSTEM'),
('periods_per_day', '6', 'SYSTEM'),
('tea_break_after_period', '2', 'SYSTEM'),
('lunch_break_after_period', '4', 'SYSTEM')
ON CONFLICT (setting_key) DO NOTHING;

-- Open Electives Table (Mega-Constraint)
CREATE TABLE IF NOT EXISTS open_electives (
    id SERIAL PRIMARY KEY,
    academic_year VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 4),
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    oe_subject_code VARCHAR(50) NOT NULL,
    oe_subject_name VARCHAR(200) NOT NULL,
    locked_day VARCHAR(20) NOT NULL,
    locked_time_slot INTEGER NOT NULL CHECK (locked_time_slot BETWEEN 1 AND 10),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(academic_year, year, semester, oe_subject_code)
);

-- Users Table (Admin vs Department Head)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'DEPT_HEAD')),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Enhanced Timetables Table with Global Locking
ALTER TABLE timetables ADD COLUMN IF NOT EXISTS is_oe_locked BOOLEAN DEFAULT FALSE;
ALTER TABLE timetables ADD COLUMN IF NOT EXISTS faculty_department VARCHAR(100);
ALTER TABLE timetables ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);

-- Trigger to prevent faculty double-booking
CREATE OR REPLACE FUNCTION check_faculty_conflict()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM timetables 
        WHERE faculty_name = NEW.faculty_name 
        AND day = NEW.day 
        AND time_slot = NEW.time_slot
        AND academic_year = NEW.academic_year
        AND id != COALESCE(NEW.id, -1)
        AND is_finalized = TRUE
    ) THEN
        RAISE EXCEPTION 'Faculty % is already scheduled on % at period %', 
            NEW.faculty_name, NEW.day, NEW.time_slot;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER faculty_conflict_check
BEFORE INSERT OR UPDATE ON timetables
FOR EACH ROW EXECUTE FUNCTION check_faculty_conflict();

-- Trigger to validate lab placement across breaks
CREATE OR REPLACE FUNCTION validate_lab_placement()
RETURNS TRIGGER AS $$
DECLARE
    tea_break_period INTEGER;
    lunch_break_period INTEGER;
BEGIN
    IF NEW.type = 'lab' THEN
        -- Get break periods from global_settings
        SELECT CAST(setting_value AS INTEGER) INTO tea_break_period 
        FROM global_settings WHERE setting_key = 'tea_break_after_period';
        
        SELECT CAST(setting_value AS INTEGER) INTO lunch_break_period 
        FROM global_settings WHERE setting_key = 'lunch_break_after_period';
        
        -- Check if lab spans across tea break
        IF NEW.time_slot = tea_break_period OR NEW.time_slot = tea_break_period - 1 THEN
            RAISE EXCEPTION 'Lab cannot be placed across tea break (Period % and %)', 
                tea_break_period, tea_break_period + 1;
        END IF;
        
        -- Check if lab spans across lunch break
        IF NEW.time_slot = lunch_break_period OR NEW.time_slot = lunch_break_period - 1 THEN
            RAISE EXCEPTION 'Lab cannot be placed across lunch break (Period % and %)', 
                lunch_break_period, lunch_break_period + 1;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER lab_placement_check
BEFORE INSERT OR UPDATE ON timetables
FOR EACH ROW EXECUTE FUNCTION validate_lab_placement();

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_timetables_faculty_time ON timetables(faculty_name, day, time_slot, academic_year);
CREATE INDEX IF NOT EXISTS idx_timetables_oe_locked ON timetables(is_oe_locked, year, semester);
CREATE INDEX IF NOT EXISTS idx_open_electives_lookup ON open_electives(academic_year, year, semester);
