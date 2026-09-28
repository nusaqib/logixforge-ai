
volt := RF_Power_Ch.RawVal * RF_Power_Ch.Gain;


PmW := 20 * (volt * volt);


if PmW <= 0 then


	PmW := 0.00000000000000000000000000000000000001;


end_if;


Pdbm := 10 * LOG(PmW) + RF_Power_Ch.Offset;


RF_Power_Ch.Val := 10 ** (0.1 * Pdbm - 6);
