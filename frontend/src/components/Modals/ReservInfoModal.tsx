import { X } from "lucide-react";
import { useState, useEffect } from "react";
import { axiosInstance } from "../../apis/axiosInstance";
import { useUser } from "../../hooks/useUser";

interface ReserveProps {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  spaceId: number;
}

export function ReservInfoModal({
  open,
  onConfirm,
  onCancel,
  spaceId,
}: ReserveProps) {
  const user = useUser();
  const [reserveDate, setReserveDate] = useState("");
  const [reservePurpose, setReservePurpose] = useState("");
  const [selectTimes, setSelectTimes] = useState<string[]>([]);
  const [disabledDates, setDisabledDates] = useState<string[]>([]); // ✅ 사용중지 날짜들

  // 오늘 ~ 일주일 뒤까지
  const today = new Date();
  const onWeekLater = new Date();
  onWeekLater.setDate(today.getDate() + 7);
  const formatDate = (date: Date) => date.toISOString().split("T")[0];

  // ✅ Space_Stop 사용중지 날짜 불러오기
  useEffect(() => {
    const fetchDisabledDates = async () => {
      try {
        const res = await axiosInstance.get("/spaces/stop-periods");
        if (res.data.success) {
          const stops = res.data.data.filter(
            (s: any) => s.space_id === spaceId
          );

          const all: string[] = [];
          stops.forEach((stop: any) => {
            const start = new Date(stop.start_date);
            const end = new Date(stop.end_date);
            for (
              let d = new Date(start);
              d <= end;
              d.setDate(d.getDate() + 1)
            ) {
              all.push(d.toISOString().split("T")[0]);
            }
          });
          setDisabledDates(all);
        }
      } catch (err) {
        console.error("🚨 사용중지 기간 불러오기 실패:", err);
      }
    };

    if (open && spaceId) fetchDisabledDates();
  }, [open, spaceId]);

  // ✅ 예약 가능 시간대
  const times = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
    "19:00",
    "20:00",
    "21:00",
  ];
  const MAX_COUNT = 3;

  const toggleTime = (time: string) => {
    if (selectTimes.includes(time)) {
      setSelectTimes(selectTimes.filter((t) => t !== time));
      return;
    }
    if (selectTimes.length >= MAX_COUNT) {
      alert(`최대 ${MAX_COUNT}개까지 선택할 수 있습니다.`);
      return;
    }
    setSelectTimes([...selectTimes, time]);
  };

  const isConsecutive = () => {
    if (selectTimes.length <= 1) return true;
    const sorted = [...selectTimes].sort(
      (a, b) => times.indexOf(a) - times.indexOf(b)
    );
    for (let i = 1; i < sorted.length; i++) {
      if (times.indexOf(sorted[i]) !== times.indexOf(sorted[i - 1]) + 1)
        return false;
    }
    return true;
  };

  // ✅ 날짜 선택 시 사용중지 확인
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (disabledDates.includes(value)) {
      alert("이 날짜는 사용중지된 공간입니다!");
      return;
    }
    setReserveDate(value);
  };

  const handleReserve = async () => {
    if (!user) {
      alert("로그인이 필요합니다!");
      return;
    }
    if (!reserveDate) {
      alert("예약 날짜를 선택해주세요!");
      return;
    }
    if (disabledDates.includes(reserveDate)) {
      alert("❌ 이 날짜는 사용중지된 공간이에요!");
      return;
    }
    if (selectTimes.length === 0) {
      alert("예약 시간을 선택해주세요!");
      return;
    }
    if (!isConsecutive()) {
      alert("시간은 반드시 연속된 값만 선택할 수 있습니다!");
      return;
    }
    if (!reservePurpose) {
      alert("예약 목적을 적어주세요!");
      return;
    }

    const sorted = [...selectTimes].sort(
      (a, b) => times.indexOf(a) - times.indexOf(b)
    );
    const startTime = sorted[0];
    const endTimeIndex = times.indexOf(sorted[sorted.length - 1]);
    const endTime = `${parseInt(times[endTimeIndex].split(":")[0]) + 1}:00`;

    try {
      const res = await axiosInstance.post("/reservation", {
        user_id: user.user_id,
        space_id: spaceId,
        reservation_date: reserveDate,
        start_time: startTime,
        end_time: endTime,
        purpose: reservePurpose,
      });

      if (res.data.success) {
        alert("예약이 완료되었습니다!");
        setReserveDate("");
        setReservePurpose("");
        setSelectTimes([]);
        onConfirm();
      } else {
        alert("예약 실패: " + res.data.message);
      }
    } catch (err) {
      console.error(err);
      alert("서버 연결 오류가 발생했습니다.");
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/40 opacity-60"
        onClick={onCancel}
      />
      <div className="relative bg-white p-8 rounded-xl shadow-xl z-10 w-180">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-blue-900">예약 상세</h2>
          <button onClick={onCancel}>
            <X />
          </button>
        </div>

        <div className="flex gap-2 mb-4">
          <h3 className="text-xl text-blue-900">예약날짜 :</h3>
          <input
            type="date"
            min={formatDate(today)}
            max={formatDate(onWeekLater)}
            value={reserveDate}
            onChange={handleDateChange}
            className={`border px-2 py-1 ${
              disabledDates.includes(reserveDate)
                ? "bg-gray-300 cursor-not-allowed"
                : ""
            }`}
          />
        </div>

        <div className="flex gap-2 mb-4">
          <h3 className="text-xl text-blue-900">예약시간 :</h3>
          <div className="grid grid-cols-13 border w-130 h-10">
            {times.map((time, idx) => (
              <button
                key={idx}
                className={`flex items-center justify-center border-r ${
                  selectTimes.includes(time)
                    ? "bg-blue-900 text-white"
                    : "text-blue-900"
                }`}
                onClick={() => toggleTime(time)}
              >
                {time}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-2 mb-4">
          <h3 className="text-xl text-blue-900">예약목적 :</h3>
          <input
            className="border w-130"
            value={reservePurpose}
            onChange={(e) => setReservePurpose(e.target.value)}
          />
        </div>

        <div className="flex justify-end gap-4">
          <button
            onClick={handleReserve}
            className="px-4 py-2 bg-blue-900 text-white rounded-lg"
          >
            예약완료
          </button>
        </div>
      </div>
    </div>
  );
}
