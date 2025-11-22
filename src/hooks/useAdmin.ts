// hooks/useUser.ts
import { useState, useEffect } from "react";

export function useAdmin() {
  const [admin, setAdmin] = useState<{
    name: string;
    admin_id: string;
    department: string;
  } | null>(null);

  useEffect(() => {
    const saveAdmin = localStorage.getItem("admin");
    if (saveAdmin) setAdmin(JSON.parse(saveAdmin));
  }, []);

  return admin;
}
