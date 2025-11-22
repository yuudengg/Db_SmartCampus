// hooks/useUser.ts
import { useState, useEffect } from "react";

export function useUser() {
  const [user, setUser] = useState<{
    name: string;
    role: string;
    login_id: string;
    user_id: number;
  } | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  return user;
}
