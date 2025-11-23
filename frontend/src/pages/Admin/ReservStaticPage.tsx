import { ChevronLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink } from "react-router";
import { StaticClassroomTable } from "../../components/Reservation/StaticClassroomTable";
import { StaticStudyroomTable } from "../../components/Reservation/StaticStudyroomTable";
import { axiosInstance } from "../../apis/axiosInstance";
import { CircleGraph } from "../../components/CircleGraph";

export const ReservStaticPage = () => {
  const [select, setSelect] = useState<"classroom" | "studyroom">("classroom");

  const [usageRate, setUsageRate] = useState(0);
  const [reservRate, setReservRate] = useState(0);

  const fetchStats = async () => {
    try {
      const [cRes, sRes, rRes] = await Promise.all([
        axiosInstance.get("/spaces/classroom"),
        axiosInstance.get("/spaces/studyroom"),
        axiosInstance.get("/admin/reservations"),
      ]);

      const allSpaces = [...cRes.data.data, ...sRes.data.data];
      const reservations = rRes.data.data;

      const totalSpaces = allSpaces.length;

      // 🔹 사용 완료된 공간 수
      const completed = reservations.filter(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (r: any) => r.status === "사용 완료"
      ).length;

      // 🔹 예약된 공간 수 (예약됨 + 사용 완료)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const reserved = reservations.filter((r: any) =>
        ["예약됨", "사용 완료"].includes(r.status)
      ).length;

      setUsageRate(Math.round((completed / totalSpaces) * 100));
      setReservRate(Math.round((reserved / totalSpaces) * 100));
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="flex flex-col h-full">
      <NavLink to="/admin">
        <ChevronLeft className="m-2" size={30} />
      </NavLink>

      <div className="flex flex-col items-center justify-center">
        {/* 🔵 원 그래프 2개 (실사용률 / 예약률) */}
        <div className="flex justify-between w-180 mb-8">
          <div className="flex flex-col items-center justify-center">
            <CircleGraph percentage={usageRate} />
            <p className="text-xl text-blue-900 font-bold mt-2">실제 사용률</p>
          </div>
          <div className="flex flex-col items-center justify-center">
            <CircleGraph percentage={reservRate} />
            <p className="text-xl text-blue-900 font-bold mt-2">예약률</p>
          </div>
        </div>

        {/* 🔵 버튼 */}
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

        {/* 🔵 표 */}
        {select === "classroom" ? (
          <StaticClassroomTable />
        ) : (
          <StaticStudyroomTable />
        )}
      </div>
    </div>
  );
};
