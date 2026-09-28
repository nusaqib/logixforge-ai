//! This routine maps module inputs to PLC tags

// Reference: Master Interlock PLC I/O List





/***** Rack 00 *****/





/*** R00_S01 ***/


// Spare := Local:1:I.Ch00.Data;												// R00_S01.0


Feeder1.Circ_LCWR_Flow.RawVal := Local:1:I.Ch01.Data;							// R00_S01.1


// Feeder1.Circ_LCWR_Temp.RawVal := Local:1:I.Ch02.Data;						// R00_S01.2


Feeder1.CircLoad_LCWR_Flow.RawVal := Local:1:I.Ch03.Data;						// R00_S01.3


// Feeder1.CircLoad_LCWR_Temp.RawVal := Local:1:I.Ch04.Data;					// R00_S01.4


Feeder1.DummyLoad_LCWR_Flow.RawVal := Local:1:I.Ch05.Data;						// R00_S01.5


// Feeder1.DummyLoad_LCWR_Temp.RawVal := Local:1:I.Ch06.Data;					// R00_S01.6


// Spare := Local:1:I.Ch07.Data; 												// R00_S01.7





/*** R00_S02 --> 5069-SERIAL ***/





/*** R00_S03 ***/


HPA1.Fault.Sts := Local:3:I.Pt00.Data;											// R00_S03.0


HPA1.State.Sts := Local:3:I.Pt01.Data;											// R00_S03.1


// Spare := Local:3:I.Pt02.Data;												// R00_S03.2


// Spare := Local:3:I.Pt03.Data;												// R00_S03.3


// Spare := Local:3:I.Pt04.Data;												// R00_S03.4


LLRF1.LO_Fault.Sts := Local:3:I.Pt05.Data;										// R00_S03.5


LLRF1.FastPermit.Sts := Local:3:I.Pt06.Data;									// R00_S03.6


// Spare := Local:3:I.Pt07.Data;												// R00_S03.7


HP_Cx_Sw1.S2_Sts := Local:3:I.Pt08.Data;										// R00_S03.8


HP_Cx_Sw1.S6_Sts := Local:3:I.Pt09.Data;										// R00_S03.9


HP_Cx_Sw1.S8_Sts := Local:3:I.Pt10.Data;										// R00_S03.10


HP_Cx_Sw1.S10_Sts := Local:3:I.Pt11.Data;										// R00_S03.11


Feeder1.TxLineSw.Sts := Local:3:I.Pt12.Data;									// R00_S03.12


// Spare := Local:3:I.Pt13.Data;												// R00_S03.13


// Spare := Local:3:I.Pt14.Data;												// R00_S03.14


// Spare := Local:3:I.Pt15.Data;												// R00_S03.15





/*** R00_S04 ***/


DrvCtrl1.CoaxSwNC_Sts := Local:4:I.Pt00.Data;									// R00_S04.0


DrvCtrl1.CoaxSwNO_Sts := Local:4:I.Pt01.Data;									// R00_S04.1


DrvCtrl1.LLRF_FastPermit_Sts := Local:4:I.Pt02.Data;							// R00_S04.2


DrvCtrl1.MPS_PermitA_Sts := Local:4:I.Pt03.Data;								// R00_S04.3


DrvCtrl1.MPS_PermitB_Sts := Local:4:I.Pt04.Data;								// R00_S04.4


DrvCtrl1.Permit_Sum := Local:4:I.Pt05.Data;								// R00_S04.5


DrvCtrl1.PPS_TestModeActive_Sts := Local:4:I.Pt06.Data;							// R00_S04.6


// Spare := Local:4:I.Pt07.Data;												// R00_S04.7


// Spare := Local:4:I.Pt08.Data;												// R00_S04.8


Feeder1.TCU.Booting := Local:4:I.Pt09.Data;										// R00_S04.9


Feeder1.TCU.OperationOK.Sts := Local:4:I.Pt10.Data;								// R00_S04.10


Feeder1.TCU.CoilCurr_Sts := Local:4:I.Pt11.Data;								// R00_S04.11


Feeder1.TCU.TempInLo_Sts := Local:4:I.Pt12.Data;								// R00_S04.12


Feeder1.TCU.TempInHi_Sts := Local:4:I.Pt13.Data;								// R00_S04.13


Feeder1.TCU.DeltaTHi_Sts := Local:4:I.Pt14.Data;								// R00_S04.14


Feeder1.TCU.TempAmbientLo_Sts := Local:4:I.Pt15.Data;							// R00_S04.15





/*** R00_S05 ***/


Local:5:O.Pt00.Data := DrvCtrl1.Transmit_Out;									// R00_S05.0


Local:5:O.Pt01.Data := DrvCtrl1.PPS_TestModeActive_Out;							// R00_S05.1


// Local:5:O.Pt02.Data := Spare;												// R00_S05.2


// Local:5:O.Pt03.Data := Spare;												// R00_S05.3


Local:5:O.Pt04.Data := HP_Cx_Sw1.Pos_Cav_Out;									// R00_S05.4


//Local:5:O.Pt05.Data := Spare;													// R00_S05.5


// Local:5:O.Pt06.Data := Spare;												// R00_S05.6


// Local:5:O.Pt07.Data := Spare;												// R00_S05.7


Local:5:O.Pt08.Data := HPA1.Permit_Out;											// R00_S05.8


// Local:5:O.Pt09.Data := Spare;												// R00_S05.9


// Local:5:O.Pt10.Data := Spare;												// R00_S05.10


// Local:5:O.Pt11.Data := Spare;												// R00_S05.11


// Local:5:O.Pt12.Data := Spare;												// R00_S05.12


Local:5:O.Pt13.Data := LLRF1.Permit_Out;										// R00_S05.13


// Local:5:O.Pt14.Data := Spare;												// R00_S05.14


// Local:5:O.Pt15.Data := Spare;												// R00_S05.15





/*** R00_S06 ***/


// Spare := Local:6:I.Pt00.Data;												// R00_S06.0


// Spare := Local:6:I.Pt01.Data;												// R00_S06.1


DrvCtrl1.DC_24V.Sts := Local:6:I.Pt02.Data;										// R00_S06.2


DrvCtrl2.DC_24V.Sts := Local:6:I.Pt03.Data;										// R00_S06.3


// Spare := Local:6:I.Pt04.Data;												// R00_S06.4


// Spare := Local:6:I.Pt05.Data;												// R00_S06.5


System.MainSensors_DC_24V.Sts := Local:6:I.Pt06.Data;							// R00_S06.6


System.ARRF1_Sensors_DC_24V.Sts := Local:6:I.Pt07.Data;							// R00_S06.7


System.ARRF2_Sensors_DC_24V.Sts := Local:6:I.Pt08.Data;							// R00_S06.8


HP_Cx_Sw1.AC_120V.Sts := Local:6:I.Pt09.Data;									// R00_S06.9


HP_Cx_Sw2.AC_120V.Sts := Local:6:I.Pt10.Data;									// R00_S06.10


// Spare := Local:6:I.Pt11.Data;												// R00_S06.11


// Spare := Local:6:I.Pt12.Data;												// R00_S06.12


// Spare := Local:6:I.Pt13.Data;												// R00_S06.13


// Spare := Local:6:I.Pt14.Data;												// R00_S06.14


// Spare := Local:6:I.Pt15.Data;												// R00_S06.15





/*** R00_S07 ***/


Vacuum.Cav1_CCG_Relay.Sts := Local:7:I.Pt00.Data;								// R00_S07.0


Vacuum.Cav2_CCG_Relay.Sts := Local:7:I.Pt01.Data;								// R00_S07.1


Vacuum.Cav1_PiraniRelay.Sts := Local:7:I.Pt02.Data;								// R00_S07.2


Vacuum.Cav2_PiraniRelay.Sts := Local:7:I.Pt03.Data;								// R00_S07.3


// Spare := Local:7:I.Pt04.Data;												// R00_S07.4


// Spare := Local:7:I.Pt05.Data;												// R00_S07.5


// Spare := Local:7:I.Pt06.Data;												// R00_S07.6


System.PLC_SA_DC_24V.Sts := Local:7:I.Pt07.Data;								// R00_S07.7


System.PLC_LA_DC_24V.Sts := Local:7:I.Pt08.Data;								// R00_S07.8


System.Ext_Intlks_DC_24V.Sts := Local:7:I.Pt09.Data;							// R00_S07.9


Local_RF_OFF.Sts := Local:7:I.Pt10.Data;										// R00_S07.10


// Spare := Local:7:I.Pt11.Data;												// R00_S07.11


MPS.PermitA.Sts := Local:7:I.Pt12.Data;											// R00_S07.12


MPS.PermitB.Sts := Local:7:I.Pt13.Data;											// R00_S07.13


MPS.HeartBeat := Local:7:I.Pt14.Data;											// R00_S07.14


// Spare := Local:7:I.Pt15.Data;												// R00_S07.15





/*** R00_S08 ***/


Local:8:O.Pt00.Data := PPS.HP_Cx_Sw1_PosDummyLd_Out;							// R00_S08.0


Local:8:O.Pt01.Data := PPS.HP_Cx_Sw2_PosDummyLd_Out;							// R00_S08.1


// Local:8:O.Pt02.Data := ;														// R00_S08.2


// Local:8:O.Pt03.Data := ;														// R00_S08.3


// Local:8:O.Pt04.Data := ;														// R00_S08.4


// Local:8:O.Pt05.Data := ;														// R00_S08.5


// Local:8:O.Pt06.Data := ;														// R00_S08.6


// Local:8:O.Pt07.Data := ;														// R00_S08.7


// Local:8:O.Pt08.Data := ;														// R00_S08.8


// Local:8:O.Pt09.Data := ;														// R00_S08.9


// Local:8:O.Pt10.Data := ;														// R00_S08.10


// Local:8:O.Pt11.Data := ;														// R00_S08.11


Local:8:O.Pt12.Data := MPS.BeamStsA_Out;										// R00_S08.12


Local:8:O.Pt13.Data := MPS.BeamStsB_Out;										// R00_S08.13


// Local:8:O.Pt14.Data := ;														// R00_S08.14


// Local:8:O.Pt15.Data := ;														// R00_S08.15





/*** R00_S09 ***/


PPS.HPA1_ChA_CxSw_Sts := Local:9:I.Pt00.Data;									// R00_S09.0


PPS.HPA1_ChB_CxSw_Sts := Local:9:I.Pt01.Data;									// R00_S09.1


PPS.HPA2_ChA_CxSw_Sts := Local:9:I.Pt02.Data;									// R00_S09.2


PPS.HPA2_ChB_CxSw_Sts := Local:9:I.Pt03.Data;									// R00_S09.3


PPS.KeyChA_Op.Sts := Local:9:I.Pt04.Data;										// R00_S09.4


PPS.KeyChB_Op.Sts := Local:9:I.Pt05.Data;										// R00_S09.5


PPS.KeyChA_RF_Test.Sts := Local:9:I.Pt06.Data;									// R00_S09.6


PPS.KeyChB_RF_Test.Sts := Local:9:I.Pt07.Data;									// R00_S09.7


PPS.KeyChA_RF_TestwAc.Sts := Local:9:I.Pt08.Data;								// R00_S09.8


PPS.KeyChB_RF_TestwAc.Sts := Local:9:I.Pt09.Data;								// R00_S09.9


PPS.KeyChA_RF_TestLd.Sts := Local:9:I.Pt10.Data;								// R00_S09.10


PPS.KeyChB_RF_TestLd.Sts := Local:9:I.Pt11.Data;								// R00_S09.11


PPS.ARRF_Test_En_ChA.Sts := Local:9:I.Pt12.Data;								// R00_S09.12


PPS.ARRF_Test_En_ChB.Sts := Local:9:I.Pt13.Data;								// R00_S09.13


PPS.SR_Ops_En_ChA.Sts := Local:9:I.Pt14.Data;									// R00_S09.14


PPS.SR_Ops_En_ChB.Sts := Local:9:I.Pt15.Data;									// R00_S09.15





/*** R00_S10 ***/


PPS.Cav1_RF_Pwr_Ltch := Local:10:I.Pt00.Data;									// R00_S10.0


PPS.Cav2_RF_Pwr_Ltch := Local:10:I.Pt01.Data;									// R00_S10.1


PPS.DC_24V.Sts := Local:10:I.Pt02.Data;											// R00_S10.2


// Spare := Local:10:I.Pt03.Data;												// R00_S10.3


// Spare := Local:10:I.Pt04.Data;												// R00_S10.4


// Spare := Local:10:I.Pt05.Data;												// R00_S10.5


// Spare := Local:10:I.Pt06.Data;												// R00_S10.6


// Spare := Local:4:I.Pt07.Data;												// R00_S10.7


// Spare := Local:10:I.Pt08.Data;												// R00_S10.8


// Spare := Local:10:I.Pt09.Data;												// R00_S10.9


// Spare := Local:10:I.Pt10.Data;												// R00_S10.10


// Spare := Local:10:I.Pt11.Data;												// R00_S10.11


// Spare := Local:10:I.Pt12.Data;												// R00_S10.12


// Spare := Local:10:I.Pt13.Data;												// R00_S10.13


// Spare := Local:10:I.Pt14.Data;												// R00_S10.14


// Spare := Local:10:I.Pt15.Data;												// R00_S10.15








/***** Rack 01 *****/





/*** R01_S01 ***/


// Spare := R01:1:I.Ch00.Data;													// R01_S01.0


Feeder2.Circ_LCWR_Flow.RawVal := R01:1:I.Ch01.Data;								// R00_S01.1


// Feeder2.Circ_LCWR_Temp.RawVal := R01:1:I.Ch02.Data;							// R00_S01.2


Feeder2.CircLoad_LCWR_Flow.RawVal := R01:1:I.Ch03.Data;							// R00_S01.3


// Feeder2.CircLoad_LCWR_Temp.RawVal := R01:1:I.Ch04.Data;						// R00_S01.4


Feeder2.DummyLoad_LCWR_Flow.RawVal := R01:1:I.Ch05.Data;						// R00_S01.5


// Feeder2.DummyLoad_LCWR_Temp.RawVal := R01:1:I.Ch06.Data;						// R00_S01.6


// Spare := R01:1:I.Ch07.Data													// R01_S01.7





/*** R01_S02 --> 5069-SERIAL ***/





/*** R01_S03 ***/


HPA2.Fault.Sts := R01:3:I.Pt00.Data;											// R01_S03.0


HPA2.State.Sts := R01:3:I.Pt01.Data;											// R01_S03.1


// Spare := R01:3:I.Pt02.Data;													// R01_S03.2


// Spare := R01:3:I.Pt03.Data;													// R01_S03.3


// Spare := R01:3:I.Pt04.Data;													// R01_S03.4


LLRF2.LO_Fault.Sts := R01:3:I.Pt05.Data;										// R01_S03.5


LLRF2.FastPermit.Sts := R01:3:I.Pt06.Data;										// R01_S03.6


//Spare := R01:3:I.Pt07.Data;													// R01_S03.7


HP_Cx_Sw2.S2_Sts := R01:3:I.Pt08.Data;											// R01_S03.8


HP_Cx_Sw2.S6_Sts := R01:3:I.Pt09.Data;											// R01_S03.9


HP_Cx_Sw2.S8_Sts := R01:3:I.Pt10.Data;											// R01_S03.10


HP_Cx_Sw2.S10_Sts := R01:3:I.Pt11.Data;											// R01_S03.11


Feeder2.TxLineSw.Sts := R01:3:I.Pt12.Data;										// R01_S03.12


// Spare := R01:3:I.Pt13.Data;													// R01_S03.13


// Spare := R01:3:I.Pt14.Data;													// R01_S03.14


// Spare := R01:3:I.Pt15.Data;													// R01_S03.15





/*** R01_S04 ***/


DrvCtrl2.CoaxSwNC_Sts := R01:4:I.Pt00.Data;										// R01_S04.0


DrvCtrl2.CoaxSwNO_Sts := R01:4:I.Pt01.Data;										// R01_S04.1


DrvCtrl2.LLRF_FastPermit_Sts := R01:4:I.Pt02.Data;								// R01_S04.2


DrvCtrl2.MPS_PermitA_Sts := R01:4:I.Pt03.Data;									// R01_S04.3


DrvCtrl2.MPS_PermitB_Sts := R01:4:I.Pt04.Data;									// R01_S04.4


DrvCtrl2.Permit_Sum := R01:4:I.Pt05.Data;									// R01_S04.5


DrvCtrl2.PPS_TestModeActive_Sts := R01:4:I.Pt06.Data;							// R01_S04.6


// Spare := R01:4:I.Pt07.Data;													// R01_S04.7


// Spare := R01:4:I.Pt08.Data;													// R01_S04.8


Feeder2.TCU.Booting := R01:4:I.Pt09.Data;										// R01_S04.9


Feeder2.TCU.OperationOK.Sts := R01:4:I.Pt10.Data;								// R01_S04.10


Feeder2.TCU.CoilCurr_Sts := R01:4:I.Pt11.Data;									// R01_S04.11


Feeder2.TCU.TempInLo_Sts := R01:4:I.Pt12.Data;									// R01_S04.12


Feeder2.TCU.TempInHi_Sts := R01:4:I.Pt13.Data;									// R01_S04.13


Feeder2.TCU.DeltaTHi_Sts := R01:4:I.Pt14.Data;									// R01_S04.14


Feeder2.TCU.TempAmbientLo_Sts := R01:4:I.Pt15.Data;								// R01_S04.15





/*** R01_S05 ***/


R01:5:O.Pt00.Data := DrvCtrl2.Transmit_Out;										// R01_S05.0


R01:5:O.Pt01.Data := DrvCtrl2.PPS_TestModeActive_Out;							// R01_S05.1


// R01:5:O.Pt02.Data := Spare;													// R01_S05.2


// R01:5:O.Pt03.Data := Spare;													// R01_S05.3


R01:5:O.Pt04.Data := HP_Cx_Sw2.Pos_Cav_Out;										// R01_S05.4


// R01:5:O.Pt05.Data := Spare;													// R01_S05.5


// R01:5:O.Pt06.Data := Spare;													// R01_S05.6


// R01:5:O.Pt07.Data := Spare;													// R01_S05.7


R01:5:O.Pt08.Data := HPA2.Permit_Out;											// R01_S05.8


// R01:5:O.Pt09.Data := Spare;													// R01_S05.9


// R01:5:O.Pt10.Data := Spare;													// R01_S05.10


// R01:5:O.Pt11.Data := Spare;													// R01_S05.11


// R01:5:O.Pt12.Data := Spare;													// R01_S05.12


R01:5:O.Pt13.Data := LLRF2.Permit_Out;											// R01_S05.13


// R01:5:O.Pt14.Data := Spare;													// R01_S05.14


// R01:5:O.Pt15.Data := Spare;													// R01_S05.15





/*** R01_S06 ***/


Main_LCWR_Temp.RawVal := R01:6:I.Ch00.Data;										// R01_S06.0


Main_LCWS_Temp.RawVal := R01:6:I.Ch01.Data;										// R01_S06.1


// Spare := R01:6:I.Ch02.Data;													// R01_S06.2


// Spare := R01:6:I.Ch03.Data;													// R01_S06.3





/*** R01_S07 ***/


Main_LCWS_Pressure.RawVal := R01:7:I.Ch00.Data;									// R01_S07.0


Main_LCWR_Pressure.RawVal := R01:7:I.Ch01.Data;									// R01_S07.1


// Spare := R01:7:I.Ch02.Data;													// R01_S07.2


// Spare := R01:7:I.Ch03.Data;													// R01_S07.3


// Spare := R01:7:I.Ch04.Data;													// R01_S07.4


// Spare := R01:7:I.Ch05.Data;													// R01_S07.5


Vacuum.Cav1_Pressure_Raw := R01:7:I.Ch06.Data;										// R01_S07.6


Vacuum.Cav2_Pressure_Raw := R01:7:I.Ch07.Data; 										// R01_S07.7





/*** R01_S08 ***/


PPS.Cav1_FwdPwr_dbm := R01:8:I.Ch00.Data;										// R01_S08.0


PPS.Cav1_CellPwr_dbm := R01:8:I.Ch01.Data;										// R01_S08.1


// Spare := R01:8:I.Ch02.Data;													// R01_S08.2


// Spare := R01:8:I.Ch03.Data;													// R01_S08.3


PPS.Cav2_FwdPwr_dbm := R01:8:I.Ch04.Data;										// R01_S08.4


PPS.Cav2_CellPwr_dbm := R01:8:I.Ch05.Data;										// R01_S08.5


// Spare := R01:8:I.Ch06.Data;													// R01_S08.6


// Spare := Not Used 															// R01_S08.7








/***** Rack 03 - CAE *****/


/*** There is no Rack 02 PLC/RIO, this is because of CAE schematic nomenclature ***/





/*** R03_S01 ***/


Cav1.CouplerBlower.Flow_Sw.Sts := R03:1:I.Pt00.Data;							// R03_S01.0


Tuner1.PS.Sts := R03:1:I.Pt01.Data;												// R03_S01.1


Tuner2.PS.Sts := R03:1:I.Pt02.Data;												// R03_S01.2


// Spare := R03_S00:1:I.Pt03.Data;												// R03_S01.3


TunerPot_PS.Sts := R03:1:I.Pt04.Data;											// R03_S01.4


System.CAE_Sensors_DC_24V.Sts := R03:1:I.Pt05.Data;								// R03_S01.5


// Spare := R03:1:I.Pt06.Data;													// R03_S01.6


// Spare := R03:1:I.Pt07.Data;													// R03_S01.7


Cav2.CouplerBlower.Flow_Sw.Sts := R03:1:I.Pt08.Data;							// R03_S01.8


// Spare := R03:1:I.Pt09.Data;													// R03_S01.9


// Spare := R03:1:I.Pt10.Data;													// R03_S01.10


// Spare := R03:1:I.Pt11.Data;													// R03_S01.11


// Spare := R03:1:I.Pt12.Data;													// R03_S01.12


// Spare := R03:1:I.Pt13.Data;													// R03_S01.13


// Spare := R03:1:I.Pt14.Data;													// R03_S01.14


// Spare := R03:1:I.Pt15.Data;													// R03_S01.15





/*** R03_S02 ***/


R03:2:O.Pt00.Data := Cav1.CouplerBlower.PS_Cmd.On_Out;							// R03_S02.0


R03:2:O.Pt01.Data := Tuner1.PS_Cmd.On_Out;										// R03_S02.1


// R03:2:O.Pt02.Data := ;														// R03_S02.2


// R03:2:O.Pt03.Data := ;														// R03_S02.3


R03:2:O.Pt04.Data := System.CAE_Sensors_DC_24V_Cmd.On_Out;						// R03_S02.4


// R03:2:O.Pt05.Data := ;														// R03_S02.5


// R03:2:O.Pt06.Data := ;														// R03_S02.6


// R03:2:O.Pt07.Data := ;														// R03_S02.7


R03:2:O.Pt08.Data := Cav2.CouplerBlower.PS_Cmd.On_Out;								// R03_S02.8


R03:2:O.Pt09.Data := Tuner2.PS_Cmd.On_Out;											// R03_S02.9


// R03:2:O.Pt10.Data := ;														// R03_S02.10


// R03:2:O.Pt11.Data := ;														// R03_S02.11


// R03:2:O.Pt12.Data := ;														// R03_S02.12


// R03:2:O.Pt13.Data := ;														// R03_S02.13


// R03:2:O.Pt14.Data := ;														// R03_S02.14


// R03:2:O.Pt15.Data := ;														// R03_S02.15





/*** R03_S03 ***/


Cav1.LCWR_Flow[0].RawVal := R03:3:I.Ch00.Data;									// R03_S03.0


Cav1.LCWR_Flow[1].RawVal := R03:3:I.Ch01.Data;									// R03_S03.1


Cav1.LCWR_Flow[2].RawVal := R03:3:I.Ch02.Data;									// R03_S03.2


Cav1.LCWR_Flow[3].RawVal := R03:3:I.Ch03.Data;									// R03_S03.3


Cav1.LCWR_Flow[4].RawVal := R03:3:I.Ch04.Data;									// R03_S03.4


Cav1.LCWR_Flow[5].RawVal := R03:3:I.Ch05.Data;									// R03_S03.5


Cav1.LCWR_Flow[6].RawVal := R03:3:I.Ch06.Data;									// R03_S03.6


Cav1.LCWR_Flow[7].RawVal := R03:3:I.Ch07.Data; 									// R03_S03.7





/*** R03_S04 ***/


Cav1.LCWR_Flow[8].RawVal := R03:4:I.Ch00.Data;									// R03_S04.0


Cav1.LCWR_Flow[9].RawVal := R03:4:I.Ch01.Data;									// R03_S04.1


Cav1.LCWR_Flow[10].RawVal := R03:4:I.Ch02.Data;									// R03_S04.2


Cav1.LCWR_Flow[11].RawVal := R03:4:I.Ch03.Data;									// R03_S04.3


Cav1.LCWR_Flow[12].RawVal := R03:4:I.Ch04.Data;									// R03_S04.4


Cav1.LCWR_Flow[13].RawVal := R03:4:I.Ch05.Data;									// R03_S04.5


Cav1.LCWR_Flow[14].RawVal := R03:4:I.Ch06.Data;									// R03_S04.6


// Spare := R03:4:I.Ch07.Data; 													// R03_S04.7





/*** R03_S05 ***/


Cav1.LCWR_Temp[0].RawVal := R03:5:I.Ch00.Data;									// R03_S05.0


Cav1.LCWR_Temp[1].RawVal := R03:5:I.Ch01.Data;									// R03_S05.1


Cav1.LCWR_Temp[2].RawVal := R03:5:I.Ch02.Data;									// R03_S05.2


Cav1.LCWR_Temp[3].RawVal := R03:5:I.Ch03.Data;									// R03_S05.3





/*** R03_S06 ***/


Cav1.LCWR_Temp[4].RawVal := R03:6:I.Ch00.Data;									// R03_S06.0


Cav1.LCWR_Temp[5].RawVal := R03:6:I.Ch01.Data;									// R03_S06.1


Cav1.LCWR_Temp[6].RawVal := R03:6:I.Ch02.Data;									// R03_S06.2


Cav1.LCWR_Temp[7].RawVal := R03:6:I.Ch03.Data; 									// R03_S06.3





/*** R03_S07 ***/


Cav1.LCWR_Temp[8].RawVal := R03:7:I.Ch00.Data;									// R03_S07.0


Cav1.LCWR_Temp[9].RawVal := R03:7:I.Ch01.Data;									// R03_S07.1


Cav1.LCWR_Temp[10].RawVal := R03:7:I.Ch02.Data;									// R03_S07.2


Cav1.LCWR_Temp[11].RawVal := R03:7:I.Ch03.Data;									// R03_S07.3





/*** R03_S08 ***/


Cav1.LCWR_Temp[12].RawVal := R03:8:I.Ch00.Data;									// R03_S08.0


Cav1.LCWR_Temp[13].RawVal := R03:8:I.Ch01.Data;									// R03_S08.1


Cav1.LCWR_Temp[14].RawVal := R03:8:I.Ch02.Data;									// R03_S08.2


Cav1.Surf_Temp[0].RawVal := R03:8:I.Ch03.Data; 									// R03_S08.3





/*** R03_S09 ***/


Cav1.Surf_Temp[1].RawVal := R03:9:I.Ch00.Data;									// R03_S09.0


Cav1.Surf_Temp[2].RawVal := R03:9:I.Ch01.Data;									// R03_S09.1


Cav1.Surf_Temp[3].RawVal := R03:9:I.Ch02.Data;									// R03_S09.2


Cav1.Surf_Temp[4].RawVal := R03:9:I.Ch03.Data; 									// R03_S09.3





/*** R03_S10 ***/


Cav1.Surf_Temp[5].RawVal := R03:10:I.Ch00.Data;									// R03_S10.0


Cav1.Surf_Temp[6].RawVal := R03:10:I.Ch01.Data;									// R03_S10.1


Cav1.Surf_Temp[7].RawVal := R03:10:I.Ch02.Data;									// R03_S10.2


Cav1.Surf_Temp[8].RawVal := R03:10:I.Ch03.Data; 								// R03_S10.3





/*** R03_S11 ***/


Cav1.CouplerTemp.RawVal := R03:11:I.Ch00.Data;								// R03_S11.0


// Spare := R03:11:I.Ch01.Data;													// R03_S11.1


// Spare := R03:11:I.Ch02.Data;													// R03_S11.2


Tuner1.Position_Pot := R03:11:I.Ch03.Data;										// R03_S11.3





/*** R03_S12 ***/


Cav2.LCWR_Flow[0].RawVal := R03:12:I.Ch00.Data;									// R03_S12.0


Cav2.LCWR_Flow[1].RawVal := R03:12:I.Ch01.Data;									// R03_S12.1


Cav2.LCWR_Flow[2].RawVal := R03:12:I.Ch02.Data;									// R03_S12.2


Cav2.LCWR_Flow[3].RawVal := R03:12:I.Ch03.Data;									// R03_S12.3


Cav2.LCWR_Flow[4].RawVal := R03:12:I.Ch04.Data;									// R03_S12.4


Cav2.LCWR_Flow[5].RawVal := R03:12:I.Ch05.Data;									// R03_S12.5


Cav2.LCWR_Flow[6].RawVal := R03:12:I.Ch06.Data;									// R03_S12.6


Cav2.LCWR_Flow[7].RawVal := R03:12:I.Ch07.Data; 								// R03_S12.7





/*** R03_S13 ***/


Cav2.LCWR_Flow[8].RawVal := R03:13:I.Ch00.Data;									// R03_S13.0


Cav2.LCWR_Flow[9].RawVal := R03:13:I.Ch01.Data;									// R03_S13.1


Cav2.LCWR_Flow[10].RawVal := R03:13:I.Ch02.Data;								// R03_S13.2


Cav2.LCWR_Flow[11].RawVal := R03:13:I.Ch03.Data;								// R03_S13.3


Cav2.LCWR_Flow[12].RawVal := R03:13:I.Ch04.Data;								// R03_S13.4


Cav2.LCWR_Flow[13].RawVal := R03:13:I.Ch05.Data;								// R03_S13.5


Cav2.LCWR_Flow[14].RawVal := R03:13:I.Ch06.Data;								// R03_S13.6


// Spare := R03:13:I.Ch07.Data; 												// R03_S13.7





/*** R03_S14 ***/


Cav2.LCWR_Temp[0].RawVal := R03:14:I.Ch00.Data;									// R03_S14.0


Cav2.LCWR_Temp[1].RawVal := R03:14:I.Ch01.Data;									// R03_S14.1


Cav2.LCWR_Temp[2].RawVal := R03:14:I.Ch02.Data;									// R03_S14.2


Cav2.LCWR_Temp[3].RawVal := R03:14:I.Ch03.Data;									// R03_S14.3





/*** R03_S15 ***/


Cav2.LCWR_Temp[4].RawVal := R03:15:I.Ch00.Data;									// R03_S15.0


Cav2.LCWR_Temp[5].RawVal := R03:15:I.Ch01.Data;									// R03_S15.1


Cav2.LCWR_Temp[6].RawVal := R03:15:I.Ch02.Data;									// R03_S15.2


Cav2.LCWR_Temp[7].RawVal := R03:15:I.Ch03.Data; 								// R03_S15.3





/*** R03_S16 ***/


Cav2.LCWR_Temp[8].RawVal := R03:16:I.Ch00.Data;									// R03_S16.0


Cav2.LCWR_Temp[9].RawVal := R03:16:I.Ch01.Data;									// R03_S16.1


Cav2.LCWR_Temp[10].RawVal := R03:16:I.Ch02.Data;								// R03_S16.2


Cav2.LCWR_Temp[11].RawVal := R03:16:I.Ch03.Data;								// R03_S16.3





/*** R03_S17 ***/


Cav2.LCWR_Temp[12].RawVal := R03:17:I.Ch00.Data;								// R03_S17.0


Cav2.LCWR_Temp[13].RawVal := R03:17:I.Ch01.Data;								// R03_S17.1


Cav2.LCWR_Temp[14].RawVal := R03:17:I.Ch02.Data;								// R03_S17.2


Cav2.Surf_Temp[0].RawVal := R03:17:I.Ch03.Data; 								// R03_S17.3





/*** R03_S18 ***/


Cav2.Surf_Temp[1].RawVal := R03:18:I.Ch00.Data;									// R03_S18.0


Cav2.Surf_Temp[2].RawVal := R03:18:I.Ch01.Data;									// R03_S18.1


Cav2.Surf_Temp[3].RawVal := R03:18:I.Ch02.Data;									// R03_S18.2


Cav2.Surf_Temp[4].RawVal := R03:18:I.Ch03.Data; 								// R03_S18.3





/*** R03_S19 ***/


Cav2.Surf_Temp[5].RawVal := R03:19:I.Ch00.Data;									// R03_S19.0


Cav2.Surf_Temp[6].RawVal := R03:19:I.Ch01.Data;									// R03_S19.1


Cav2.Surf_Temp[7].RawVal := R03:19:I.Ch02.Data;									// R03_S19.2


Cav2.Surf_Temp[8].RawVal := R03:19:I.Ch03.Data; 								// R03_S19.3





/*** R03_S20 ***/


Cav2.CouplerTemp.RawVal := R03:20:I.Ch00.Data;								// R03_S20.0


// Spare := R03:20:I.Ch01.Data;													// R03_S20.1


// Spare := R03:20:I.Ch02.Data;													// R03_S20.2


Tuner2.Position_Pot := R03:20:I.Ch03.Data;										// R03_S20.3





//Tuner1


Tuner1.LimitSw_CW := Cav1_Tuner:I.IN1_Active;


Tuner1.LimitSw_CCW := Cav1_Tuner:I.IN2_Active;


Tuner1.Position := Cav1_Tuner:I.MOTOR_POSITION;


Tuner1.Input_Error := NOT Cav1_Tuner:I.Input_Error;


Tuner1.Command_Error := NOT Cav1_Tuner:I.Command_Error;


Tuner1.Configuration_Error := NOT Cav1_Tuner:I.Configuration_Error;


Tuner1.Position_Invalid.Sts := NOT Cav1_Tuner:I.Position_Invalid;


Tuner1.ConnectionFaulted.Sts := NOT Cav1_Tuner:I.ConnectionFaulted;


Tuner1.ResetErrors_Cmd := System.Rst;


Tuner1.Moving_CW := Cav1_Tuner:I.Moving_CW;


Tuner1.Moving_CCW := Cav1_Tuner:I.Moving_CCW;


Tuner1.Move_Complete := Cav1_Tuner:I.Move_Complete;





//Tuner2


Tuner2.LimitSw_CW := Cav2_Tuner:I.IN1_Active;


Tuner2.LimitSw_CCW := Cav2_Tuner:I.IN2_Active;


Tuner2.Position := Cav2_Tuner:I.MOTOR_POSITION;


Tuner2.Input_Error := NOT Cav2_Tuner:I.Input_Error;


Tuner2.Command_Error := NOT Cav2_Tuner:I.Command_Error;


Tuner2.Configuration_Error := NOT Cav2_Tuner:I.Configuration_Error;


Tuner2.Position_Invalid.Sts := NOT Cav2_Tuner:I.Position_Invalid;


Tuner2.ConnectionFaulted.Sts := NOT Cav2_Tuner:I.ConnectionFaulted;


Tuner2.ResetErrors_Cmd := System.Rst;


Tuner2.Moving_CW := Cav2_Tuner:I.Moving_CW;


Tuner2.Moving_CCW := Cav2_Tuner:I.Moving_CCW;


Tuner2.Move_Complete := Cav2_Tuner:I.Move_Complete;
