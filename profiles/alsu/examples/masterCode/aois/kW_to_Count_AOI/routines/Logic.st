
Pdbm := 10 * LOG(RF_Power_Ch.Hi_SP) + 60 - RF_Power_Ch.Offset;


PmW := 10 ** (Pdbm / 10);


volt := SQRT(PmW / 20);


RF_Power_Ch.Hi_SP_Raw := TRUNC(volt / RF_Power_Ch.Gain);





Pdbm := 10 * LOG(RF_Power_Ch.Lo_SP) + 60 - RF_Power_Ch.Offset;


PmW := 10 ** (Pdbm / 10);


volt := SQRT(PmW / 20);


RF_Power_Ch.Lo_SP_Raw := TRUNC(volt / RF_Power_Ch.Gain);
