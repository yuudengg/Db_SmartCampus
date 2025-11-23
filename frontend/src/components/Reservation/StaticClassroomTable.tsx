import { useState, useEffect } from "react";
import { axiosInstance } from "../../apis/axiosInstance";
import type { SpaceInfo } from "../../types/space";

export const StaticClassroomTable = () => {
  const [classrooms, setClassrooms] = useState<SpaceInfo[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [reservations, setReservations] = useState<any[]>([]);
  const [selectBuilding, setSelectBuilding] = useState("A동");

  // 🔹 강의실 목록 불러오기
  useEffect(() => {
    const fetchClassrooms = async () => {
      try {
        const res = await axiosInstance.get("/spaces/classroom");
        if (res.data.success) setClassrooms(res.data.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchClassrooms();
  }, []);

  // 🔹 전체 예약 데이터 불러오기 (사용 현황 계산용)
  useEffect(() => {
    const fetchReservations = async () => {
      try {
        const res = await axiosInstance.get("/admin/reservations");
        if (res.data.success) setReservations(res.data.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchReservations();
  }, []);

  // 🔹 특정 강의실의 사용률 계산
  const getUsageRate = (spaceName: string) => {
    const roomReserv = reservations.filter((r) => r.spaceName === spaceName);
    if (roomReserv.length === 0) return 0;

    const completed = roomReserv.filter((r) => r.status === "사용 완료").length;
    return Math.round((completed / roomReserv.length) * 100);
  };

  // 🔹 선택 건물 필터
  const filteredRooms = classrooms.filter(
    (room) => room.location === selectBuilding
  );

  const buildings = ["A동", "B동", "C동", "D동", "E동", "G동", "P동", "산융"];

  return (
    <div className="flex flex-col items-center">
      {/* 건물 버튼 */}
      <div className="flex w-200">
        {buildings.map((b) => (
          <button
            key={b}
            onClick={() => setSelectBuilding(b)}
            className={`px-4 w-1/7 rounded-t-sm border-2 border-blue-900 text-2xl ${
              selectBuilding === b
                ? "bg-blue-900 text-white"
                : "bg-white text-blue-900"
            }`}
          >
            {b}
          </button>
        ))}
      </div>

      {/* 테이블 */}
      <div className="flex flex-col w-200 h-100 border-2 border-blue-900 gap-2 p-6 overflow-auto">
        <div className="grid grid-cols-4 text-2xl text-blue-900 font-bold gap-4 pb-2">
          <div className="flex justify-center"></div>
          <div className="flex justify-center">강의실</div>
          <div className="flex justify-center">수용 인원</div>
          <div className="flex justify-center">사용 현황</div>
        </div>

        {filteredRooms.map((room, index) => {
          const usage = getUsageRate(room.space_name);

          return (
            <div
              key={room.space_id}
              className="grid grid-cols-4 text-xl text-blue-900 border-b py-3 items-center"
            >
              <div className="text-center">{index + 1}</div>
              <div className="text-center">{room.space_name}</div>
              <div className="text-center">{room.capacity}</div>

              {/* 🔵 사용 현황 그래프 */}
              <div className="flex flex-col items-center w-full px-4">
                <div className="w-full bg-gray-200 h-4 rounded">
                  <div
                    className="h-full bg-blue-900 rounded"
                    style={{ width: `${usage}%` }}
                  />
                </div>
                <p className="text-sm mt-1">{usage}%</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
