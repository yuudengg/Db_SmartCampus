import { axiosInstance } from "./axiosInstance";

// 🧍‍♀️ 회원가입 API
export const registerUser = async (data: {
  name: string;
  login_id: string;
  password: string;
  role: "학생" | "교수";
  student_id?: string;
  grade?: string;
  major?: string;
  professor_id?: string;
  department?: string;
  position?: string;
}) => {
  const response = await axiosInstance.post("/register", data);
  return response.data;
};

// 🔑 사용자 로그인 API
export const postUserLogin = async (login_id: string, password: string) => {
  const { data } = await axiosInstance.post("/login/user", {
    login_id,
    password,
  });
  return data;
};

// 👨‍💼 관리자 로그인 API
export const adminLogin = async (admin_id: string) => {
  const data = await axiosInstance.post("/login/admin", admin_id);
  return data;
};

// 아이디 중복확인 API
export const postCheckId = async (login_id: string) => {
  const { data } = await axiosInstance.post("/check-id", { login_id });
  return data;
};
