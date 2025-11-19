import { ChevronLeft } from "lucide-react";
import { useState } from "react";
import { NavLink } from "react-router";

export const SpaceReservation = () => {
  const [select, setSelect] = useState<"classroom" | "studyroom">("classroom");

  return (
    <div className="flex flex-col h-full">
      <NavLink to="/user">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>
      <div className="flex flex-col items-center justify-center">
        <h1 className="flex text-5xl font-bold text-blue-900 my-8">
          장소 예약
        </h1>
        <div className="flex w-180 gap-4">
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
      </div>
    </div>
  );
};
