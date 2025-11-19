import { ChevronLeft } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router";
import { ClassroomTable } from "../../components/Reservation/ClassroomTable";
import { StudyroomTable } from "../../components/Reservation/StudyroomTable";

export const ManageSpacePage = () => {
  const [select, setSelect] = useState<"classroom" | "studyroom">("classroom");

  return (
    <div className="flex flex-col h-full">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          장소 관리
        </h1>
        <div className="flex w-200 gap-4 mb-6">
          <button
            className={`border-2 border-blue-900 text-2xl font-bold w-35 py-1 ${
              select === "classroom"
                ? "text-white bg-blue-900"
                : "text-blue-900 bg-white"
            }`}
            onClick={() => setSelect("classroom")}
          >
            강의실
          </button>
          <button
            className={`border-2 border-blue-900 text-2xl font-bold w-35 py-1 ${
              select === "studyroom"
                ? "text-white bg-blue-900"
                : "text-blue-900 bg-white"
            }`}
            onClick={() => setSelect("studyroom")}
          >
            스터디룸
          </button>
        </div>
        {select === "classroom" ? <ClassroomTable /> : <StudyroomTable />}
        <div className="flex w-200 justify-end my-2 gap-2">
          <NavLink
            to="/admin/manage/space/stop"
            className="flex border-2 border-blue-900 px-2 text-blue-900"
          >
            사용중지 리스트
          </NavLink>
          <p className="flex border-2 border-blue-900 px-2 text-blue-900">
            수정 완료
          </p>
        </div>
      </div>
    </div>
  );
};
