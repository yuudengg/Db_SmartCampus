import type { JSX } from "react";
import { Navigate, useLocation } from "react-router";

export function PrivateRoute({ children }: { children: JSX.Element }) {
  const role = localStorage.getItem("role");
  const location = useLocation();

  // 🔸 로그인 안 된 경우
  if (!role) {
    alert("로그인이 필요합니다!");
    return <Navigate to="/" replace />;
  }

  // 🔸 관리자 접근 제한
  if (role === "관리자" && location.pathname.startsWith("/user")) {
    alert("관리자는 사용자 페이지에 접근할 수 없습니다.");
    return <Navigate to="/admin" replace />;
  }

  // 🔸 사용자(학생/교수) 접근 제한
  if (
    (role === "학생" || role === "교수") &&
    location.pathname.startsWith("/admin")
  ) {
    alert("사용자는 관리자 페이지에 접근할 수 없습니다.");
    return <Navigate to="/user" replace />;
  }

  // ✅ 접근 허용
  return children;
}
