import { X } from "lucide-react";
import { useState, useEffect } from "react";
import type { ReservationManage } from "../../types/reservation";

interface EditReservProps {
  reservation: ReservationManage;
  onSave: (updated: ReservationManage) => void;
  onCancel: () => void;
}

export function EditReservModal({
  reservation,
  onSave,
  onCancel,
}: EditReservProps) {
  const parseTimeRange = (range: string) => {
    const timesArray = [
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

    const [start, end] = range.split(" ~ ");

    const startIndex = timesArray.indexOf(start);
    const endIndex = timesArray.indexOf(end);

    if (startIndex === -1 || endIndex === -1) return [];

    return timesArray.slice(startIndex, endIndex);
  };

  const [reserveDate, setReserveDate] = useState(reservation.date);
  const [reservePurpose, setReservePurpose] = useState(reservation.purpose);
  const [selectTimes, setSelectTimes] = useState<string[]>(
    parseTimeRange(reservation.time)
  );

  useEffect(() => {
    setReserveDate(reservation.date);
    setReservePurpose(reservation.purpose);
    setSelectTimes(parseTimeRange(reservation.time));
  }, [reservation]);

  const today = new Date();
  const weekLater = new Date();
  weekLater.setDate(today.getDate() + 7);

  const formatDate = (date: Date) => date.toISOString().split("T")[0];

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
      if (times.indexOf(sorted[i]) !== times.indexOf(sorted[i - 1]) + 1) {
        return false;
      }
    }

    return true;
  };

  const handleSave = () => {
    if (!reserveDate) return alert("예약 날짜를 선택해주세요!");
    if (selectTimes.length === 0) return alert("예약 시간을 선택해주세요!");
    if (!isConsecutive())
      return alert("시간은 반드시 연속된 값만 선택해야 합니다!");
    if (!reservePurpose) return alert("예약 목적을 입력해주세요!");

    const sorted = [...selectTimes].sort(
      (a, b) => times.indexOf(a) - times.indexOf(b)
    );
    const startTime = sorted[0];
    const endTimeIndex = times.indexOf(sorted[sorted.length - 1]) + 1;
    const endTime = endTimeIndex < times.length ? times[endTimeIndex] : "22:00";
    const formattedTime = `${startTime} ~ ${endTime}`;

    onSave({
      ...reservation,
      date: reserveDate,
      time: formattedTime,
      purpose: reservePurpose,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/40 opacity-60"
        onClick={onCancel}
      />
      <div className="relative bg-white p-8 rounded-xl shadow-xl z-10 w-180">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-blue-900">예약 수정</h2>
          <button onClick={onCancel}>
            <X className="text-blue-900" />
          </button>
        </div>
        <div className="flex gap-2 mb-4">
          <h3 className="text-xl text-blue-900">예약날짜 : </h3>
          <input
            type="date"
            min={formatDate(today)}
            max={formatDate(weekLater)}
            value={reserveDate}
            onChange={(e) => setReserveDate(e.target.value)}
          />
        </div>
        <div className="flex gap-2 mb-4">
          <h3 className="text-xl text-blue-900">예약시간 : </h3>
          <div className="grid grid-cols-13 border w-130 h-10">
            {times.map((time) => (
              <button
                key={time}
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
          <h3 className="text-xl text-blue-900">예약목적 : </h3>
          <input
            className="border w-130"
            value={reservePurpose}
            onChange={(e) => setReservePurpose(e.target.value)}
          />
        </div>
        <div className="flex justify-end gap-4">
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-900 text-white rounded-lg"
          >
            저장
          </button>
          <button onClick={onCancel} className="px-4 py-2 border rounded-lg">
            취소
          </button>
        </div>
      </div>
    </div>
  );
}
