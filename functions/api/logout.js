import { currentAdmin, json, readCookie, sameOrigin, sessionCookie } from "../_lib.js";

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!sameOrigin(request)) return json({ error: "이 사이트에서만 로그아웃할 수 있습니다." }, 403);
  const admin = await currentAdmin(env.DB, request);
  const token = readCookie(request);
  if (admin && token) {
    await env.DB.prepare("DELETE FROM sessions WHERE token = ?").bind(token).run();
  }
  return json({ ok: true }, 200, [sessionCookie("", request)]);
}
