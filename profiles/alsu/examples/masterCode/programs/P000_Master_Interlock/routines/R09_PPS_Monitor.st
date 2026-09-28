
// Convert PPS RF Power Monitor values to kW


PPS.Cav1_FwdPwr_kW := 10 ** (0.1 * PPS.Cav1_FwdPwr_dbm - 6);


PPS.Cav1_CellPwr_kW := 10 ** (0.1 * PPS.Cav1_CellPwr_dbm - 6);


PPS.Cav2_FwdPwr_kW := 10 ** (0.1 * PPS.Cav2_FwdPwr_dbm - 6);


PPS.Cav2_CellPwr_kW := 10 ** (0.1 * PPS.Cav2_CellPwr_dbm - 6);
