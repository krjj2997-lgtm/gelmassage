CREATE TABLE IF NOT EXISTS admins (
  id INTEGER PRIMARY KEY,
  login TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  admin_id INTEGER NOT NULL,
  expires_at INTEGER NOT NULL,
  FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_admin ON sessions(admin_id);

CREATE TABLE IF NOT EXISTS login_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ip TEXT NOT NULL,
  at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip, at);

INSERT OR IGNORE INTO admins (id, login, email, password_hash, updated_at)
VALUES (
  1,
  'admin',
  'krjj2997@gmail.com',
  'pbkdf2$4000$FWMP8HFbu5DW8+CjVwMfMA==$Pb4tI5GzJJm02/Ea++tLQcgUPfxLKjYY5jGPXdbyY0I=',
  '2026-10-23T00:00:00Z'
);
