import {
  currentAdmin,
  hashPassword,
  json,
  readJson,
  sameOrigin,
  validEmail,
  validLogin,
  validPassword,
  verifyPassword,
} from "../_lib.js";

export async function onRequestGet(context) {
  const admin = await currentAdmin(context.env.DB, context.request);
  if (!admin) return json({ error: "로그인이 필요합니다." }, 401);
  return json({ login: admin.login, email: admin.email });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!sameOrigin(request)) return json({ error: "이 사이트에서만 계정을 수정할 수 있습니다." }, 403);
  const admin = await currentAdmin(env.DB, request);
  if (!admin) return json({ error: "로그인이 필요합니다." }, 401);

  const body = await readJson(request);
  const login = String(body && body.login || "").trim().toLowerCase();
  const email = String(body && body.email || "").trim().toLowerCase();
  const currentPassword = String(body && body.currentPassword || "");
  const newPassword = String(body && body.newPassword || "");
  if (!validLogin(login)) return json({ error: "아이디는 영문 소문자, 숫자, ., _, - 로 2자 이상 입력해 주세요." }, 400);
  if (!validEmail(email)) return json({ error: "이메일 형식을 확인해 주세요." }, 400);
  if (!currentPassword) return json({ error: "현재 비밀번호를 입력해 주세요." }, 400);
  if (newPassword && !validPassword(newPassword)) return json({ error: "새 비밀번호는 8자 이상으로 입력해 주세요." }, 400);

  const row = await env.DB.prepare("SELECT password_hash FROM admins WHERE id = ?").bind(admin.id).first();
  if (!row || !(await verifyPassword(currentPassword, row.password_hash))) {
    return json({ error: "현재 비밀번호가 맞지 않습니다." }, 401);
  }

  const taken = await env.DB.prepare(
    "SELECT id FROM admins WHERE id != ? AND (login = ? OR email = ?)",
  ).bind(admin.id, login, email).first();
  if (taken) return json({ error: "이미 사용 중인 아이디 또는 이메일입니다." }, 409);

  const passwordHash = newPassword ? await hashPassword(newPassword) : row.password_hash;
  await env.DB.prepare(
    "UPDATE admins SET login = ?, email = ?, password_hash = ?, updated_at = ? WHERE id = ?",
  ).bind(login, email, passwordHash, new Date().toISOString(), admin.id).run();
  if (newPassword) {
    await env.DB.prepare("DELETE FROM sessions WHERE admin_id = ? AND token != ?").bind(admin.id, admin.token).run();
  }
  return json({ login, email });
}
