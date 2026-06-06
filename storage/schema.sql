CREATE TABLE IF NOT EXISTS leagues (
    league_id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    fetched_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS rosters (
    league_id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    fetched_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data TEXT NOT NULL,
    fetched_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS matchups (
    league_id TEXT NOT NULL,
    week INTEGER NOT NULL,
    data TEXT NOT NULL,
    fetched_at REAL NOT NULL,
    PRIMARY KEY (league_id, week)
);

CREATE TABLE IF NOT EXISTS transactions (
    league_id TEXT NOT NULL,
    week INTEGER NOT NULL,
    data TEXT NOT NULL,
    fetched_at REAL NOT NULL,
    PRIMARY KEY (league_id, week)
);
