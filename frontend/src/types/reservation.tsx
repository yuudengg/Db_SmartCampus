export interface Reservation {
  id: number;
  spaceName: string;
  date: string;
  time: string;
  userId: number;
  status: string;
}

export interface ReservationManage {
  id: number;
  userName: string;
  spaceName: string;
  date: string;
  time: string;
  purpose: string;
  status: "예약됨" | "사용완료" | "예약취소";
}
