import { ChevronLeft } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router";
import { ClassroomTable } from "../../components/Reservation/ClassroomTable";
import { StudyroomTable } from "../../components/Reservation/StudyroomTable";

export const ReservStaticPage = () => {
  const [select, setSelect] = useState<"classroom" | "studyroom">("classroom");

  return (
    <div className="flex flex-col h-full">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <div className="flex justify-between w-180 mb-8">
          <div className="flex flex-col items-center justify-center">
            <div className="flex rounded-full w-50 h-50 border-4 border-blue-900 mb-2"></div>
            <p className="text-xl text-blue-900 font-bold">실제 사용률</p>
          </div>
          <div className="flex flex-col items-center justify-center">
            <div className="flex rounded-full w-50 h-50 border-4 border-blue-900 mb-2"></div>
            <p className="text-xl text-blue-900 font-bold">예약률</p>
          </div>
        </div>
        <div className="flex justify-start items-start w-200 gap-4 mb-4">
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
      </div>
    </div>
  );
};
