
GSV(Program, THIS, MajorFaultRecord, major_fault_record.Time_Low);


IF (major_fault_record.Type = 1) & (major_fault_record.Code = 1) THEN


major_fault_record.Type := 0;


major_fault_record.Code := 0;


SSV(Program, THIS, MajorFaultRecord, major_fault_record.Time_Low);


END_IF;
