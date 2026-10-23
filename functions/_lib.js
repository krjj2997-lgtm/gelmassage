const ITERATIONS = 4000;
const COOKIE = "gm_session";
const SESSION_MS = 14 * 24 * 60 * 60 * 1000;
const MAX_ATTEMPTS = 8;
const ATTEMPT_WINDOW_MS = 15 * 60 * 1000;

export function json(data, status, cookies) {
  const headers = new Headers({
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  });
  for (const cookie of cookies || []) headers.append("set-cookie", cookie);
  return new Response(JSON.stringify(data), { status: status || 200, headers });
}

export function sameOrigin(request) {
  const origin = request.headers.get("Origin");
  return Boolean(origin) && origin === new URL(request.url).origin;
}

export async function readJson(request) {
  const length = Number(request.headers.get("content-length") || 0);
  if (length > 4000) return null;
  const text = await request.text();
  if (!text || text.length > 4000) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function encode(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

function decode(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return bytes;
}

function timingEqual(left, right) {
  const a = new TextEncoder().encode(left);
  const b = new TextEncoder().encode(right);
  const length = Math.max(a.length, b.length);
  let diff = a.length ^ b.length;
  for (let index = 0; index < length; index += 1) diff |= (a[index] || 0) ^ (b[index] || 0);
  return diff === 0;
}

export async function hashPassword(password) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const bits = await derive(password, salt, ITERATIONS);
  return `pbkdf2$${ITERATIONS}$${encode(salt)}$${encode(new Uint8Array(bits))}`;
}

async function derive(password, salt, iterations) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveBits"],
  );
  return crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations, hash: "SHA-256" },
    key,
    256,
  );
}

export async function verifyPassword(password, stored) {
  const parts = String(stored || "").split("$");
  if (parts.length !== 4 || parts[0] !== "pbkdf2") return false;
  const iterations = Number(parts[1]);
  if (!Number.isInteger(iterations) || iterations < 1000 || iterations > 20000) return false;
  let salt;
  try {
    salt = decode(parts[2]);
  } catch {
    return false;
  }
  const bits = await derive(password, salt, iterations);
  const actual = `pbkdf2$${iterations}$${parts[2]}$${encode(new Uint8Array(bits))}`;
  return timingEqual(actual, stored);
}

export function randomToken() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function sessionCookie(token, request) {
  const secure = new URL(request.url).protocol === "https:" ? "; Secure" : "";
  const value = token ? `${encodeURIComponent(token)}; Max-Age=${SESSION_MS / 1000}` : "; Max-Age=0";
  return `${COOKIE}=${value}; HttpOnly; Path=/; SameSite=Lax${secure}`;
}

export function readCookie(request) {
  const header = request.headers.get("cookie") || "";
  for (const part of header.split(";")) {
    const item = part.trim();
    const splitAt = item.indexOf("=");
    if (splitAt === -1) continue;
    if (item.slice(0, splitAt) !== COOKIE) continue;
    return decodeURIComponent(item.slice(splitAt + 1));
  }
  return "";
}

export function clientIp(request) {
  return request.headers.get("CF-Connecting-IP") || "local";
}

export async function currentAdmin(db, request) {
  const token = readCookie(request);
  if (!token || token.length > 80) return null;
  return db.prepare(
    `SELECT a.id AS id, a.login AS login, a.email AS email, s.token AS token
     FROM sessions s
     JOIN admins a ON a.id = s.admin_id
     WHERE s.token = ? AND s.expires_at > ?`,
  ).bind(token, Date.now()).first();
}

export async function tooManyAttempts(db, ip) {
  const since = Date.now() - ATTEMPT_WINDOW_MS;
  await db.prepare("DELETE FROM login_attempts WHERE at < ?").bind(since).run();
  const row = await db.prepare("SELECT COUNT(*) AS n FROM login_attempts WHERE ip = ?").bind(ip).first();
  return Number(row && row.n) >= MAX_ATTEMPTS;
}

export async function recordAttempt(db, ip) {
  await db.prepare("INSERT INTO login_attempts (ip, at) VALUES (?, ?)").bind(ip, Date.now()).run();
}

export function sessionExpiry() {
  return Date.now() + SESSION_MS;
}

export function validLogin(value) {
  return /^[a-z0-9._-]{2,40}$/.test(value);
}

export function validEmail(value) {
  return value.length <= 120 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export function validPassword(value) {
  return typeof value === "string" && value.length >= 8 && value.length <= 72;
}
