export const ProfessorFields = ({
  formData,
  handleChange,
}: {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  formData: any;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) => (
  <>
    <div className="flex gap-2 items-center">
      <p className="text-lg mr-2">교수아이디</p>
      <input
        name="professor_id"
        value={formData.professor_id}
        onChange={handleChange}
        className="border w-60 h-13 p-4"
      />
    </div>
    <div className="flex gap-2 items-center">
      <p className="text-lg mr-15.5">학과</p>
      <input
        name="department"
        value={formData.department}
        onChange={handleChange}
        className="border w-60 h-13 p-4"
      />
    </div>
    <div className="flex gap-2 items-center">
      <p className="text-lg mr-15.5">직위</p>
      <input
        name="position"
        value={formData.position}
        onChange={handleChange}
        className="border w-60 h-13 p-4"
      />
    </div>
  </>
);
