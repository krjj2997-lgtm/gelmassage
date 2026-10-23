import {
  clientIp,
  json,
  randomToken,
  readJson,
  recordAttempt,
  sameOrigin,
  sessionCookie,
  sessionExpiry,
  tooManyAttempts,
  verifyPassword,
} from "../_lib.js";

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!sameOrigin(request)) return json({ error: "이 사이트에서만 로그인할 수 있습니다." }, 403);
  const body = await readJson(request);
  const login = String(body && body.login || "").trim().toLowerCase();
  const password = String(body && body.password || "");
  if (!login || !password) return json({ error: "아이디와 비밀번호를 입력해 주세요." }, 400);

  const ip = clientIp(request);
  if (await tooManyAttempts(env.DB, ip)) {
    return json({ error: "시도가 너무 많습니다. 15분 뒤에 다시 로그인해 주세요." }, 429);
  }

  const admin = await env.DB.prepare(
    "SELECT id, login, email, password_hash FROM admins WHERE login = ? OR email = ?",
  ).bind(login, login).first();
  const stored = admin ? admin.password_hash : "pbkdf2$4000$AAAAAAAAAAAAAAAAAAAAAA==$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
  const matched = await verifyPassword(password, stored);
  if (!admin || !matched) {
    await recordAttempt(env.DB, ip);
    return json({ error: "아이디 또는 비밀번호가 맞지 않습니다." }, 401);
  }

  const token = randomToken();
  const now = Date.now();
  await env.DB.batch([
    env.DB.prepare("DELETE FROM login_attempts WHERE ip = ?").bind(ip),
    env.DB.prepare("DELETE FROM sessions WHERE expires_at <= ?").bind(now),
    env.DB.prepare("INSERT INTO sessions (token, admin_id, expires_at) VALUES (?, ?, ?)").bind(token, admin.id, sessionExpiry()),
  ]);
  return json(
    { login: admin.login, email: admin.email },
    200,
    [sessionCookie(token, request)],
  );
}
