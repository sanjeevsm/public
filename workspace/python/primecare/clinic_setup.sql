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

    ('Arjun',   'Mehta',    'arjun.mehta@clinic.in',     '9810001003', 'MCI-MH-30078', 2,
     'Orthopaedic surgeon specialising in sports injuries and minimally invasive joint replacements.', 1000.00),

    ('Sunita',  'Reddy',    'sunita.reddy@clinic.in',    '9810001004', 'MCI-AP-40099', 6,
     'Gynaecologist and obstetrician with 12 years of clinical practice in high-risk pregnancies.', 900.00),

    ('Vikram',  'Iyer',     'vikram.iyer@clinic.in',     '9810001005', 'MCI-TN-50112', 5,
     'Neurologist specialising in epilepsy, migraine, and movement disorders.', 1100.00),

    ('Ananya',  'Krishnan', 'ananya.krishnan@clinic.in', '9810001006', 'MCI-KL-60134', 3,
     'Dermatologist with expertise in cosmetic dermatology, acne management, and hair loss treatment.', 700.00),

    ('Suresh',  'Patel',    'suresh.patel@clinic.in',    '9810001007', 'MCI-GJ-70156', 8,
     'General physician with 20 years in primary care and chronic disease management.', 500.00),

    ('Meera',   'Bose',     'meera.bose@clinic.in',      '9810001008', 'MCI-WB-80178', 7,
     'Ophthalmologist trained at Sankara Nethralaya, Chennai, with expertise in retinal disorders.', 850.00),

    ('Rahul',   'Gupta',    'rahul.gupta@clinic.in',     '9810001009', 'MCI-UP-90200', 8,
     'Family medicine physician focusing on preventive healthcare and lifestyle disease management.', 500.00),

    ('Kavitha', 'Menon',    'kavitha.menon@clinic.in',   '9810001010', 'MCI-KL-10022', 1,
     'Interventional cardiologist with expertise in angioplasty, cardiac imaging, and heart failure.', 1500.00);

-- ============================================================
-- SAMPLE DATA — DOCTOR SCHEDULES
-- day_of_week: 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
-- ============================================================

INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes) VALUES
    -- Dr. Rajesh Sharma (Cardiology): Mon, Wed, Fri mornings
    (1, 1, '09:00', '13:00', 30),
    (1, 3, '09:00', '13:00', 30),
    (1, 5, '14:00', '18:00', 30),

    -- Dr. Priya Nair (Paediatrics): Tue, Thu, Sat
    (2, 2, '10:00', '14:00', 20),
    (2, 4, '10:00', '14:00', 20),
    (2, 6, '09:00', '12:00', 20),

    -- Dr. Arjun Mehta (Orthopaedics): Mon, Tue, Thu
    (3, 1, '08:00', '12:00', 30),
    (3, 2, '14:00', '18:00', 30),
    (3, 4, '08:00', '12:00', 30),

    -- Dr. Sunita Reddy (Gynaecology): Mon, Wed, Fri, Sat
    (4, 1, '10:00', '14:00', 30),
    (4, 3, '10:00', '14:00', 30),
    (4, 5, '10:00', '13:00', 30),
    (4, 6, '09:00', '12:00', 30),

    -- Dr. Vikram Iyer (Neurology): Tue, Thu (longer slots)
    (5, 2, '09:00', '13:00', 45),
    (5, 4, '15:00', '19:00', 45),

    -- Dr. Ananya Krishnan (Dermatology): Wed, Thu, Sat
    (6, 3, '11:00', '15:00', 20),
    (6, 4, '11:00', '15:00', 20),
    (6, 6, '10:00', '13:00', 20),

    -- Dr. Suresh Patel (General Medicine): Mon–Sat
    (7, 1, '08:00', '12:00', 15),
    (7, 2, '08:00', '12:00', 15),
    (7, 3, '08:00', '12:00', 15),
    (7, 4, '08:00', '12:00', 15),
    (7, 5, '08:00', '12:00', 15),
    (7, 6, '08:00', '11:00', 15),

    -- Dr. Meera Bose (Ophthalmology): Mon, Wed, Fri
    (8, 1, '10:00', '14:00', 30),
    (8, 3, '10:00', '14:00', 30),
    (8, 5, '10:00', '13:00', 30),

    -- Dr. Rahul Gupta (General Medicine): Tue, Thu, Sat
    (9, 2, '09:00', '13:00', 15),
    (9, 4, '09:00', '13:00', 15),
    (9, 6, '09:00', '12:00', 15),

    -- Dr. Kavitha Menon (Cardiology): Mon, Wed, Fri afternoons
    (10, 1, '14:00', '18:00', 30),
    (10, 3, '14:00', '18:00', 30),
    (10, 5, '09:00', '13:00', 30);

-- ============================================================
-- SAMPLE DATA — PATIENTS (10, Indian names)
-- ============================================================

INSERT INTO patients (first_name, last_name, email, phone, date_of_birth, gender) VALUES
    ('Arun',    'Kumar',        'arun.kumar@gmail.com',       '9900001001', '1985-03-15', 'Male'),
    ('Lakshmi', 'Devi',         'lakshmi.devi@gmail.com',     '9900001002', '1972-07-22', 'Female'),
    ('Rohit',   'Sharma',       'rohit.sharma@gmail.com',     '9900001003', '1990-11-08', 'Male'),
    ('Anjali',  'Singh',        'anjali.singh@gmail.com',     '9900001004', '1988-05-30', 'Female'),
    ('Mohan',   'Rao',          'mohan.rao@gmail.com',        '9900001005', '1965-01-12', 'Male'),
    ('Preethi', 'Nair',         'preethi.nair@gmail.com',     '9900001006', '1995-09-18', 'Female'),
    ('Sanjay',  'Verma',        'sanjay.verma@gmail.com',     '9900001007', '1978-04-25', 'Male'),
    ('Deepa',   'Patel',        'deepa.patel@gmail.com',      '9900001008', '1982-12-03', 'Female'),
    ('Karthik', 'Subramaniam',  'karthik.s@gmail.com',        '9900001009', '1992-06-14', 'Male'),
    ('Nandita', 'Ghosh',        'nandita.ghosh@gmail.com',    '9900001010', '1968-02-28', 'Female');

-- ============================================================
-- SAMPLE DATA — APPOINTMENTS
-- Dates chosen to match each doctor's scheduled day_of_week.
-- Appointments 1–12 : completed (past)
-- Appointments 13–16: confirmed follow-ups (upcoming)
-- Appointments 17–21: confirmed new bookings (upcoming)
-- ============================================================

INSERT INTO appointments (doctor_id, patient_id, appointment_date, start_time, end_time, status) VALUES
    -- Past completed
    (1,  5,  '2026-04-06', '09:00', '09:30', 'completed'),  -- 1:  Mohan Rao       → Rajesh Sharma   (Cardiology)
    (4,  6,  '2026-04-06', '10:00', '10:30', 'completed'),  -- 2:  Preethi Nair     → Sunita Reddy    (Gynecology)
    (3,  3,  '2026-04-06', '08:00', '08:30', 'completed'),  -- 3:  Rohit Sharma     → Arjun Mehta     (Orthopedics)
    (7,  1,  '2026-04-07', '08:00', '08:15', 'completed'),  -- 4:  Arun Kumar       → Suresh Patel    (General Medicine)
    (5,  7,  '2026-04-07', '09:00', '09:45', 'completed'),  -- 5:  Sanjay Verma     → Vikram Iyer     (Neurology)
    (6,  8,  '2026-04-08', '11:00', '11:20', 'completed'),  -- 6:  Deepa Patel      → Ananya Krishnan (Dermatology)
    (8,  2,  '2026-04-08', '10:00', '10:30', 'completed'),  -- 7:  Lakshmi Devi     → Meera Bose      (Ophthalmology)
    (3,  9,  '2026-04-09', '08:00', '08:30', 'completed'),  -- 8:  Karthik Subra.   → Arjun Mehta     (Orthopedics)
    (7,  10, '2026-04-09', '08:00', '08:15', 'completed'),  -- 9:  Nandita Ghosh    → Suresh Patel    (General Medicine)
    (1,  4,  '2026-04-13', '09:00', '09:30', 'completed'),  -- 10: Anjali Singh      → Rajesh Sharma   (Cardiology)
    (10, 5,  '2026-04-27', '14:00', '14:30', 'completed'),  -- 11: Mohan Rao        → Kavitha Menon   (Cardiology)
    (7,  2,  '2026-05-04', '08:00', '08:15', 'completed'),  -- 12: Lakshmi Devi     → Suresh Patel    (General Medicine)

    -- Follow-up appointments (confirmed, upcoming)
    (1,  5,  '2026-05-18', '09:00', '09:30', 'confirmed'),  -- 13: Follow-up for #1  (Mohan Rao, Cardiology)
    (5,  7,  '2026-05-19', '09:00', '09:45', 'confirmed'),  -- 14: Follow-up for #5  (Sanjay Verma, Neurology)
    (3,  3,  '2026-05-21', '08:00', '08:30', 'confirmed'),  -- 15: Follow-up for #3  (Rohit Sharma, Orthopedics)
    (3,  9,  '2026-05-21', '08:30', '09:00', 'confirmed'),  -- 16: Follow-up for #8  (Karthik, Orthopedics)

    -- New upcoming bookings (confirmed)
    (2,  6,  '2026-05-19', '10:00', '10:20', 'confirmed'),  -- 17: Preethi Nair  → Priya Nair      (Pediatrics)
    (4,  8,  '2026-05-20', '10:00', '10:30', 'confirmed'),  -- 18: Deepa Patel   → Sunita Reddy    (Gynecology)
    (6,  1,  '2026-05-21', '11:00', '11:20', 'confirmed'),  -- 19: Arun Kumar    → Ananya Krishnan (Dermatology)
    (8,  10, '2026-05-22', '10:00', '10:30', 'confirmed'),  -- 20: Nandita Ghosh → Meera Bose      (Ophthalmology)
    (10, 4,  '2026-05-25', '14:00', '14:30', 'confirmed');  -- 21: Anjali Singh   → Kavitha Menon  (Cardiology)

-- ============================================================
-- SAMPLE DATA — CASE HISTORY (for all 12 completed appointments)
-- follow_up_needed = TRUE for appointments 1, 5, 3, 8
-- ============================================================

INSERT INTO case_history (appointment_id, symptoms, diagnosis, prescription, follow_up_needed, follow_up_date, follow_up_appointment_id, notes) VALUES

    -- Appt #1: Mohan Rao — Cardiology (Rajesh Sharma) → follow-up booked as #13
    (1,
     'Chest tightness and mild shortness of breath on exertion for 2 weeks',
     'Stable angina pectoris — Grade II (CCS classification)',
     'Tab. Aspirin 75 mg OD; Tab. Atorvastatin 40 mg HS; Tab. Metoprolol 25 mg BD; Tab. Isosorbide mononitrate 10 mg BD SOS',
     TRUE, '2026-05-18', 13,
     'ECG normal at rest. Stress echo ordered. Holter report due — review at follow-up.'),

    -- Appt #2: Preethi Nair — Gynecology (Sunita Reddy)
    (2,
     'Irregular menstrual cycles for 6 months, lower abdominal cramps, mild hirsutism',
     'Polycystic ovarian syndrome (PCOS)',
     'Tab. Metformin 500 mg BD with meals; Tab. Folic acid 5 mg OD; Lifestyle counselling — low GI diet and exercise',
     FALSE, NULL, NULL,
     'USG pelvis confirms polycystic ovaries. Hormone panel (LH, FSH, testosterone) ordered. Review when reports arrive.'),

    -- Appt #3: Rohit Sharma — Orthopedics (Arjun Mehta) → follow-up booked as #15
    (3,
     'Right knee pain and swelling after a football match, restricted flexion beyond 90°',
     'Medial meniscus tear — Grade II (MRI confirmed)',
     'Tab. Diclofenac 50 mg BD x 7 days; Tab. Pantoprazole 40 mg OD; Knee brace (hinged); Physiotherapy 3× per week',
     TRUE, '2026-05-21', 15,
     'MRI right knee shows Grade II medial meniscus tear. No ligament rupture. Surgical decision deferred pending physio response. No high-impact activity until follow-up.'),

    -- Appt #4: Arun Kumar — General Medicine (Suresh Patel)
    (4,
     'Fatigue, mild headache, low-grade fever (99–100 °F) for 4 days, body ache',
     'Acute viral fever',
     'Tab. Paracetamol 650 mg TDS × 5 days; Tab. Cetirizine 10 mg HS; ORS sachets; Adequate hydration advised',
     FALSE, NULL, NULL,
     'CBC ordered — mild lymphocytosis, no alarming findings. Review if fever persists beyond 5 days or spikes above 102 °F.'),

    -- Appt #5: Sanjay Verma — Neurology (Vikram Iyer) → follow-up booked as #14
    (5,
     'Recurrent pulsatile headaches 2–3 episodes/week, photophobia, nausea, visual aura preceding attacks',
     'Chronic migraine with aura',
     'Tab. Topiramate 25 mg BD (titrate to 50 mg BD over 4 weeks); Tab. Sumatriptan 50 mg SOS (max 2/day); Tab. Metoclopramide 10 mg SOS for nausea',
     TRUE, '2026-05-19', 14,
     'MRI brain unremarkable. Migraine diary to be maintained. Follow-up in 6 weeks to assess Topiramate tolerability and response. Avoid known triggers — poor sleep, skipped meals, screen glare.'),

    -- Appt #6: Deepa Patel — Dermatology (Ananya Krishnan)
    (6,
     'Pruritic erythematous patches on forearms and neck, worsening in summer, dry skin',
     'Atopic dermatitis — mild to moderate',
     'Betamethasone valerate 0.1% cream BD × 2 weeks; Tab. Cetirizine 10 mg HS; Cetaphil moisturising lotion QID; Avoid synthetic fabrics and harsh detergents',
     FALSE, NULL, NULL,
     'Patch test recommended to identify contact allergens. Return if no improvement in 3 weeks or lesions spread.'),

    -- Appt #7: Lakshmi Devi — Ophthalmology (Meera Bose)
    (7,
     'Progressive blurring of near vision for 1 year, difficulty reading fine print, eye strain by evening',
     'Presbyopia with bilateral dry eye syndrome',
     'Reading glasses +1.75 D (both eyes) prescribed; Systane Ultra lubricating eye drops QID; Omega-3 supplement 1000 mg OD',
     FALSE, NULL, NULL,
     'Fundoscopy normal. IOP within normal limits. Annual eye review advised. Screen time reduction and 20-20-20 rule counselled.'),

    -- Appt #8: Karthik Subramaniam — Orthopedics (Arjun Mehta) → follow-up booked as #16
    (8,
     'Left ankle pain and swelling after a road run, unable to bear full weight, bruising noted',
     'Lateral ankle sprain — Grade II (anterior talofibular ligament)',
     'Tab. Ibuprofen 400 mg TDS × 5 days; Tab. Pantoprazole 40 mg OD; RICE protocol; Ankle brace for 3 weeks; Physiotherapy for proprioception training',
     TRUE, '2026-05-21', 16,
     'X-ray ankle: no fracture. MRI ordered to rule out peroneal tendon injury. No running for 4 weeks. Review with MRI report.'),

    -- Appt #9: Nandita Ghosh — General Medicine (Suresh Patel)
    (9,
     'Persistent dry cough for 3 weeks, mild wheeze, breathlessness on climbing stairs',
     'Allergic bronchitis — possible early asthma',
     'Inhaler: Budesonide 200 mcg BD × 4 weeks; Tab. Montelukast 10 mg HS; Tab. Cetirizine 10 mg OD; Avoid dust and cold air',
     FALSE, NULL, NULL,
     'Spirometry shows mild obstruction with reversibility. Chest X-ray clear. Allergen panel ordered. Review in 4 weeks with spirometry repeat.'),

    -- Appt #10: Anjali Singh — Cardiology (Rajesh Sharma)
    (10,
     'Fatigue, occasional palpitations, mild ankle swelling for 3 months',
     'Mild mitral valve regurgitation with preserved ejection fraction',
     'Tab. Ramipril 2.5 mg OD; Tab. Furosemide 20 mg OD; Sodium restriction (<2 g/day); Annual 2D Echo advised',
     FALSE, NULL, NULL,
     '2D Echo: EF 58%, mild MR, no LV dilatation. BP well controlled. Antibiotic prophylaxis not indicated per current guidelines. Annual cardiac follow-up.'),

    -- Appt #11: Mohan Rao — Cardiology (Kavitha Menon)
    (11,
     'Palpitations, intermittent dizziness, exertional breathlessness — second opinion sought',
     'Paroxysmal atrial fibrillation — confirmed on Holter',
     'Tab. Apixaban 5 mg BD; Tab. Metoprolol succinate 50 mg OD; Tab. Amiodarone 200 mg OD (loading phase); Rate and rhythm control plan initiated',
     FALSE, NULL, NULL,
     '24-hour Holter: 3 episodes of PAF, longest 47 minutes. CHADS-VASc score 3. EP team review recommended for ablation candidacy assessment.'),

    -- Appt #12: Lakshmi Devi — General Medicine (Suresh Patel)
    (12,
     'Swelling and pain in finger joints and wrists, morning stiffness lasting >1 hour for 2 months',
     'Early rheumatoid arthritis — under evaluation',
     'Tab. Hydroxychloroquine 200 mg OD; Tab. Folic acid 5 mg OD; Tab. Paracetamol 500 mg SOS; Hand physiotherapy advised',
     FALSE, NULL, NULL,
     'RA factor positive (1:160). Anti-CCP sent. ESR and CRP elevated. Rheumatology referral placed. Avoid NSAIDs long-term until rheumatologist review.');
