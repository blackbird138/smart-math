export const API_BASE = "http://localhost:8001";

export async function updateEnv(data: Record<string, string>) {
  await fetch(`${API_BASE}/update_env`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}
