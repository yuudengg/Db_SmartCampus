export interface Space {
  id: number;
  building: string; // A동, B동
  name: string; // A101
  capacity: number;
  type: "classroom" | "studyroom";
}

export interface SpaceStop {
  id: number;
  spaceName: string;
  startDate: string;
  endDate: string;
}

export interface SpaceInfo {
  no: number;
  room: string;
  capacity: number;
}
