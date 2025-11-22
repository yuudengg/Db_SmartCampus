import type { JSX } from "react";
import { Navigate } from "react-router";

export function PublicOnlyRoute({ children }: { children: JSX.Element }) {
  const role = localStorage.getItem("role");

  if (role === "관리자") {
    return <Navigate to="/admin" replace />;
  }

  if (role === "학생" || role === "교수") {
    return <Navigate to="/user" replace />;
  }

  // ✅ 로그인 안 된 경우만 원래 페이지 보여줌
  return children;
}
