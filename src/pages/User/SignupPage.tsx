import { useState } from "react";
import { StudentFields } from "../../components/SignupField/StudentField";
import { ProfessorFields } from "../../components/SignupField/ProfessorField";

export const SignupPage = () => {
  const [role, setRole] = useState<"학생" | "교수">("학생");

  return (
    <div className="flex flex-col">
      <div className="flex flex-col items-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">회원가입</h1>
        <div className="flex flex-col justify-center border w-150 h-150 p-10 gap-4">
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-15.5">이름</p>
            <input
              className="flex border w-60 h-13 p-4"
              placeholder="이름을 입력하세요."
            />
          </div>
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-11">아이디</p>
            <input
              className="flex border w-60 h-13 p-4"
              placeholder="아이디를 입력하세요."
            />
            <button className="bg-blue-900 text-white h-13 p-4 mx-2">
              중복 확인
            </button>
          </div>
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-6.5">비밀번호</p>
            <input
              className="flex border w-100 h-13 p-4"
              placeholder="비밀번호를 입력하세요."
            />
          </div>
          <div className="flex gap-2 items-center">
            <p className="text-lg mr-14">ROLE</p>
            <select
              className="border text-lg px-4 h-13"
              onChange={(e) => setRole(e.target.value as "학생" | "교수")}
            >
              <option>학생</option>
              <option>교수</option>
            </select>
          </div>
          {role === "학생" && <StudentFields />}
          {role === "교수" && <ProfessorFields />}
          <button className="text-3xl font-bold text-blue-900 mt-4">
            회원가입
          </button>
        </div>
      </div>
    </div>
  );
};
