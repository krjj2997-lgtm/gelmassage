UPDATE admins SET password_hash = 'pbkdf2$4000$KP3UYQIVPUbxveKQsmWLPA==$Ey6abhn0n/JIw7kmWwIQYQzP2kwzb4uQBBMcG11sbHs=', updated_at = '2026-10-23T04:00:00Z' WHERE login = 'admin';
DELETE FROM sessions;
