-- ============================================================
-- CLINIC MARKETPLACE DATABASE
-- Run step 1: psql -U postgres -c "CREATE DATABASE clinic;"
-- Run step 2: psql -U postgres -d clinic -f clinic_setup.sql
-- ============================================================

-- ============================================================
-- SCHEMA
-- ============================================================

CREATE TABLE specialities (
    id   SERIAL       PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE doctors (
    id                  SERIAL        PRIMARY KEY,
    first_name          VARCHAR(50)   NOT NULL,
    last_name           VARCHAR(50)   NOT NULL,
    email               VARCHAR(100)  NOT NULL UNIQUE,
    phone               VARCHAR(15)   NOT NULL UNIQUE,
    registration_number VARCHAR(50)   NOT NULL UNIQUE,
    speciality_id       INT           NOT NULL REFERENCES specialities(id),
    bio                 TEXT,
    consultation_fee    NUMERIC(8, 2) NOT NULL DEFAULT 500.00,
    is_active           BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- Weekly recurring availability; day_of_week: 0=Sun, 1=Mon, ..., 6=Sat
CREATE TABLE doctor_schedules (
    id                    SERIAL   PRIMARY KEY,
    doctor_id             INT      NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    day_of_week           SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    start_time            TIME     NOT NULL,
    end_time              TIME     NOT NULL,
    slot_duration_minutes SMALLINT NOT NULL DEFAULT 30,
    is_active             BOOLEAN  NOT NULL DEFAULT TRUE,
    UNIQUE (doctor_id, day_of_week, start_time),
    CHECK (end_time > start_time)
);

CREATE TABLE patients (
    id            SERIAL       PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    email         VARCHAR(100) UNIQUE,
    phone         VARCHAR(15)  NOT NULL UNIQUE,
    date_of_birth DATE,
    gender        VARCHAR(10)  CHECK (gender IN ('Male', 'Female', 'Other')),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE appointments (
    id               SERIAL      PRIMARY KEY,
    doctor_id        INT         NOT NULL REFERENCES doctors(id),
    patient_id       INT         NOT NULL REFERENCES patients(id),
    appointment_date DATE        NOT NULL,
    start_time       TIME        NOT NULL,
    end_time         TIME        NOT NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'confirmed'
                     CHECK (status IN ('confirmed', 'cancelled', 'completed', 'no_show')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (doctor_id, appointment_date, start_time),
    CHECK (end_time > start_time)
);

CREATE TABLE case_history (
    id                       SERIAL      PRIMARY KEY,
    appointment_id           INT         NOT NULL UNIQUE REFERENCES appointments(id),
    symptoms                 TEXT,
    diagnosis                TEXT,
    prescription             TEXT,
    follow_up_needed         BOOLEAN     NOT NULL DEFAULT FALSE,
    follow_up_date           DATE,
    follow_up_appointment_id INT         REFERENCES appointments(id),
    notes                    TEXT,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE doctor_leaves (
    id         SERIAL       PRIMARY KEY,
    doctor_id  INT          NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    leave_date DATE         NOT NULL,
    reason     VARCHAR(255),
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (doctor_id, leave_date)
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_doctors_speciality     ON doctors(speciality_id);
CREATE INDEX idx_schedules_doctor       ON doctor_schedules(doctor_id);
CREATE INDEX idx_appts_doctor_date      ON appointments(doctor_id, appointment_date);
CREATE INDEX idx_appts_patient          ON appointments(patient_id);
CREATE INDEX idx_case_history_patient   ON case_history(appointment_id);
CREATE INDEX idx_doctor_leaves_doctor   ON doctor_leaves(doctor_id);
CREATE INDEX idx_doctor_leaves_date     ON doctor_leaves(leave_date);

-- ============================================================
-- SAMPLE DATA — SPECIALITIES
-- ============================================================

INSERT INTO specialities (name) VALUES
    ('Cardiology'),
    ('Orthopedics'),
    ('Dermatology'),
    ('Pediatrics'),
    ('Neurology'),
    ('Gynecology'),
    ('Ophthalmology'),
    ('General Medicine');

-- ============================================================
-- SAMPLE DATA — DOCTORS (10, mix of specialities)
-- ============================================================

INSERT INTO doctors (first_name, last_name, email, phone, registration_number, speciality_id, bio, consultation_fee) VALUES
    ('Rajesh',  'Sharma',   'rajesh.sharma@clinic.in',   '9810001001', 'MCI-DL-10021', 1,
     'Senior cardiologist with 18 years at AIIMS Delhi, specialising in preventive cardiology.', 1200.00),

    ('Priya',   'Nair',     'priya.nair@clinic.in',      '9810001002', 'MCI-KL-20045', 4,
     'Paediatric specialist focused on neonatal care and childhood immunology, trained at CMC Vellore.', 800.00),

... (rest unchanged) ...
