CREATE TABLE IF NOT EXISTS Candidates (
    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    created_at TEXT DEFAULT (DATETIME('now')),
    updated_at TEXT DEFAULT (DATETIME('now'))
);

CREATE TABLE IF NOT EXISTS Notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    next_action TEXT NOT NULL,
    created_at TEXT DEFAULT (DATETIME('now')),
    FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id)
);

CREATE TABLE IF NOT EXISTS WorkExperience (
    experience_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    company TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    created_at TEXT DEFAULT (DATETIME('now')),
    FOREIGN KEY (candidate_id) REFERENCES Candidates(candidate_id)
);
