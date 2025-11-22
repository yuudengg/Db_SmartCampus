import { useMemo, useState } from "react";
import { StudentFields } from "../../components/SignupField/StudentField";
import { ProfessorFields } from "../../components/SignupField/ProfessorField";
import { postCheckId, registerUser } from "../../apis/user";
import { useNavigate } from "react-router";

export const SignupPage = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState<"학생" | "교수">("학생");
  const [isChecking, setIsChecking] = useState(false);
  const [idChecked, setIdChecked] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    login_id: "",
    password: "",
    student_id: "",
    grade: "",
    major: "",
    professor_id: "",
    department: "",
    position: "",
  });

  // ✅ 공통 입력 처리 함수
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setIdChecked(false);
  };

  // 중복확인 버튼 함수
  const handleCheckDuplicate = async () => {
    if (!formData.login_id.trim()) {
      alert("아이디를 입력하세요!");
      return;
    }
    setIsChecking(true);
    try {
      const res = await postCheckId(formData.login_id);
      if (res.exists) {
        alert("이미 사용 중인 아이디입니다.");
        setIdChecked(false);
      } else {
        alert("사용 가능한 아이디입니다!");
        setIdChecked(true);
      }
    } catch (err) {
      console.error(err);
      alert("중복확인 중 오류가 발생했습니다.");
      setIdChecked(false);
    } finally {
      setIsChecking(false);
    }
  };

  // 필수 입력 확인 함수
  const isFormValid = useMemo(() => {
    if (!formData.name || !formData.login_id || !formData.password)
      return false;

    if (role === "학생") {
      return (
        formData.student_id.trim() !== "" &&
        formData.grade.trim() !== "" &&
        formData.major.trim() !== "" &&
        idChecked
      );
    } else {
      return (
        formData.professor_id.trim() !== "" &&
        formData.department.trim() !== "" &&
        formData.position.trim() !== "" &&
        idChecked
      );
    }
  }, [formData, role, idChecked]);

  // ✅ 회원가입 버튼 클릭 시
  const handleRegister = async () => {
    if (!isFormValid) {
      alert("모든 정보를 입력하고 아이디 중복확인을 완료하세요!");
      return;
    }

    try {
      const res = await registerUser({
        name: formData.name,
        login_id: formData.login_id,
        password: formData.password,
        role,
        ...(role === "학생"
          ? {
              student_id: formData.student_id,
              grade: formData.grade,
              major: formData.major,
            }
          : {
              professor_id: formData.professor_id,
              department: formData.department,
              position: formData.position,
            }),
      });

      if (res.success) {
        alert(res.message);
        navigate("/login/user");
      } else {
        alert("회원가입 실패: " + res.message);
      }
    } catch (err) {
      console.error(err);
      alert("서버 연결 오류가 발생했습니다.");
    }
  };

  return (
    <div className="flex flex-col">
      <div className="flex flex-col items-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">회원가입</h1>

        <div className="flex flex-col justify-center border w-150 h-150 p-10 gap-4">
          {/* 이름 */}
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-15.5">이름</p>
            <input
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="flex border w-60 h-13 p-4"
              placeholder="이름을 입력하세요."
            />
          </div>

          {/* 아이디 */}
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-11">아이디</p>
            <input
              name="login_id"
              value={formData.login_id}
              onChange={handleChange}
              className="flex border w-60 h-13 p-4"
              placeholder="아이디를 입력하세요."
            />
            <button
              onClick={handleCheckDuplicate}
              disabled={isChecking}
              className={`h-13 p-4 mx-2 ${
                isChecking ? "bg-gray-400" : "bg-blue-900 text-white "
              }`}
            >
              중복 확인
            </button>
          </div>

          {/* 비밀번호 */}
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-6.5">비밀번호</p>
            <input
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className="flex border w-100 h-13 p-4"
              placeholder="비밀번호를 입력하세요."
            />
          </div>

          {/* ROLE 선택 */}
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-14">ROLE</p>
            <select
              className="border text-lg px-4 h-13"
              value={role}
              onChange={(e) => setRole(e.target.value as "학생" | "교수")}
            >
              <option>학생</option>
              <option>교수</option>
            </select>
          </div>

          {/* 역할별 추가 필드 */}
          {role === "학생" && (
            <StudentFields formData={formData} handleChange={handleChange} />
          )}
          {role === "교수" && (
            <ProfessorFields formData={formData} handleChange={handleChange} />
          )}

          {/* 회원가입 버튼 */}
          <button
            onClick={handleRegister}
            disabled={!isFormValid}
            className={`text-3xl font-bold mt-4 py-2 rounded ${
              isFormValid
                ? "text-blue-900 cursor-pointer"
                : "bg-gray-300 text-gray-600 cursor-not-allowed"
            }`}
          >
            회원가입
          </button>
        </div>
      </div>
    </div>
  );
};
