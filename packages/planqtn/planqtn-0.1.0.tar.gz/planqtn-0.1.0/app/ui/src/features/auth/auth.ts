import { userContextSupabase } from "../../config/supabaseClient";

export async function getAccessToken(): Promise<string | null> {
  if (!userContextSupabase) {
    return null;
  }
  const { data, error } = await userContextSupabase.auth.getSession();

  if (error) {
    console.error("Error getting session:", error);
    return null;
  }

  if (data?.session) {
    return data.session.access_token;
  }
  return null;
}
