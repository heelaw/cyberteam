interface Env {
  DB: D1Database
}

function getSession(request: Request) {
  const cookie = request.headers.get("Cookie") || ""
  const match = cookie.match(/pua_session=([^;]+)/)
  if (!match) return null
  try {
    return JSON.parse(atob(match[1])) as {
      id: string
      login: string
      avatar: string
      token: string
    }
  } catch {
    return null
  }
}

export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  const session = getSession(request)
  if (!session) {
    return Response.json({ logged_in: false }, { status: 401 })
  }

  // Get upload count for this user
  const result = await env.DB.prepare(
    "SELECT COUNT(*) as count FROM uploads WHERE github_id = ?"
  ).bind(session.id).first<{ count: number }>()

  return Response.json({
    logged_in: true,
    id: session.id,
    login: session.login,
    avatar: session.avatar,
    upload_count: result?.count || 0,
  })
}
