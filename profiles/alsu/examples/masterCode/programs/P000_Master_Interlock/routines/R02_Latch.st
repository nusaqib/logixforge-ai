//! Latches all the fault signals

////////////////////////////////////////////////////////////


//   Copyright (c)  <LBNL>


//------------------------------------------------------------


//   Routine: tripStatusLatch


//   Author: LBL\NUSaqib


//   Created: 2/11/2022


//------------------------------------------------------------


//   Description:


//           This routine latches all the trip fault signals


//           


//


//   History:


//


////////////////////////////////////////////////////////////





// System


Latch_ai_AOI(Latch_ai_System[0], Main_LCWS_Temp, System.Rst);


Latch_ai_AOI(Latch_ai_System[1], Main_LCWR_Temp, System.Rst);


Latch_ai_AOI(Latch_ai_System[2], Main_LCWS_Pressure, System.Rst);


Latch_ai_AOI(Latch_ai_System[3], Main_LCWR_Pressure, System.Rst);


Latch_bi_AOI(Latch_bi_System[0], System.MainSensors_DC_24V, System.Rst);


Latch_bi_AOI(Latch_bi_System[1], System.ARRF1_Sensors_DC_24V, System.Rst);


Latch_bi_AOI(Latch_bi_System[2], System.ARRF2_Sensors_DC_24V, System.Rst);


Latch_bi_AOI(Latch_bi_System[3], System.PLC_SA_DC_24V, System.Rst);


Latch_bi_AOI(Latch_bi_System[4], System.PLC_LA_DC_24V, System.Rst);


Latch_bi_AOI(Latch_bi_System[5], System.Ext_Intlks_DC_24V, System.Rst);


Latch_bi_AOI(Latch_bi_System[6], TunerPot_PS, System.Rst);


Latch_bi_AOI(Latch_bi_System[7], System.CAE_Sensors_DC_24V, System.Rst);





// PPS


Latch_bi_AOI(Latch_bi_PPS[0], PPS.ARRF_Test_En_ChA, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[1], PPS.ARRF_Test_En_ChB, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[2], PPS.SR_Ops_En_ChA, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[3], PPS.SR_Ops_En_ChB, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[4], PPS.KeyChA_Op, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[5], PPS.KeyChB_Op, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[6], PPS.KeyChA_RF_Test, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[7], PPS.KeyChB_RF_Test, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[8], PPS.KeyChA_RF_TestwAc, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[9], PPS.KeyChB_RF_TestwAc, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[10], PPS.KeyChA_RF_TestLd, System.Rst);


Latch_bi_AOI(Latch_bi_PPS[11], PPS.KeyChB_RF_TestLd, System.Rst);


//Latch_bi_AOI(Latch_bi_PPS[12], PPS.Cav1_RF_Pwr_Ltch, System.Rst);  Latched in hardware in PPS Power Monitor Chassis


//Latch_bi_AOI(Latch_bi_PPS[13], PPS.Cav2_RF_Pwr_Ltch, System.Rst);  Latched in hardware in PPS Power Monitor Chassis


Latch_bi_AOI(Latch_bi_PPS[14], PPS.DC_24V, System.Rst);





// MPS


Latch_bi_AOI(Latch_bi_MPS[0], MPS.PermitA, System.Rst);


Latch_bi_AOI(Latch_bi_MPS[1], MPS.PermitB, System.Rst);





// Drive Control 1


//Latch_bi_AOI(Latch_bi_DrvCtrl1[0], DrvCtrl1.CoaxSwNO_Sts, System.Rst);


Latch_bi_AOI(Latch_bi_DrvCtrl1[1], DrvCtrl1.DC_24V, System.Rst);





// Drive Control 2


//Latch_bi_AOI(Latch_bi_DrvCtrl2[0], DrvCtrl2.CoaxSwNO_Sts, System.Rst);


Latch_bi_AOI(Latch_bi_DrvCtrl2[1], DrvCtrl2.DC_24V, System.Rst);





// HP Coax Switch 1


Latch_bi_AOI(Latch_bi_HP_Coax_SW1[0], HP_Cx_Sw1.AC_120V, System.Rst);


Latch_bi_AOI(Latch_bi_HP_Coax_SW1[1], HP_Cx_Sw1.PPS_Match, System.Rst);





// HP Coax Switch 2


Latch_bi_AOI(Latch_bi_HP_Coax_SW2[0], HP_Cx_Sw2.AC_120V, System.Rst);


Latch_bi_AOI(Latch_bi_HP_Coax_SW2[1], HP_Cx_Sw2.PPS_Match, System.Rst);





// TCU 1


Latch_bi_AOI(Latch_bi_TCU1[0], Feeder1.TCU.OperationOK, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU1[1], Feeder1.TCU.CoilCurr, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU1[2], Feeder1.TCU.TempInHi, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU1[3], Feeder1.TCU.DeltaTHi, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU1[4], Feeder1.TCU.TempInLo, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU1[5], Feeder1.TCU.TempAmbientLo, System.Rst);





// TCU 2


Latch_bi_AOI(Latch_bi_TCU2[0], Feeder2.TCU.OperationOK, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU2[1], Feeder2.TCU.CoilCurr, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU2[2], Feeder2.TCU.TempInHi, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU2[3], Feeder2.TCU.DeltaTHi, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU2[4], Feeder2.TCU.TempInLo, System.Rst);


//Latch_bi_AOI(Latch_bi_TCU2[5], Feeder2.TCU.TempAmbientLo, System.Rst);





// HPA 1


Latch_bi_AOI(Latch_bi_HPA1[0], HPA1.Fault, System.Rst);


Latch_bi_AOI(Latch_bi_HPA1[1], HPA1.State, System.Rst);





// HPA 2


Latch_bi_AOI(Latch_bi_HPA2[0], HPA2.Fault, System.Rst);


Latch_bi_AOI(Latch_bi_HPA2[1], HPA2.State, System.Rst);





// LLRF 1


Latch_bi_AOI(Latch_bi_LLRF1[0], LLRF1.FastPermit, System.Rst);


Latch_bi_AOI(Latch_bi_LLRF1[1], LLRF1.LO_Fault, System.Rst);





// LLRF 2


Latch_bi_AOI(Latch_bi_LLRF2[0], LLRF2.FastPermit, System.Rst);


Latch_bi_AOI(Latch_bi_LLRF2[1], LLRF2.LO_Fault, System.Rst);





// Feeder 1


Latch_ai_AOI(Latch_ai_Feeder1[0], Feeder1.Circ_LCWR_Flow, System.Rst);


//Latch_ai_AOI(Latch_ai_Feeder1[1], Feeder1.Circ_LCWR_Temp, System.Reset);


Latch_ai_AOI(Latch_ai_Feeder1[2], Feeder1.CircLoad_LCWR_Flow, System.Rst);


//Latch_ai_AOI(Latch_ai_Feeder1[3], Feeder1.CircLoad_LCWR_Temp, System.Reset);


Latch_ai_AOI(Latch_ai_Feeder1[4], Feeder1.DummyLoad_LCWR_Flow, System.Rst);


//Latch_ai_AOI(Latch_ai_Feeder1[5], Feeder1.DummyLoad_LCWR_Temp, System.Reset);


Latch_bi_AOI(Latch_bi_Feeder1[0], Feeder1.TxLineSw, System.Rst);





// Feeder 2


Latch_ai_AOI(Latch_ai_Feeder2[0], Feeder2.Circ_LCWR_Flow, System.Rst);


//Latch_ai_AOI(Latch_ai_Feeder2[1], Feeder2.Circ_LCWR_Temp, System.Reset);


Latch_ai_AOI(Latch_ai_Feeder2[2], Feeder2.CircLoad_LCWR_Flow, System.Rst);


//Latch_ai_AOI(Latch_ai_Feeder2[3], Feeder2.CircLoad_LCWR_Temp, System.Reset);


Latch_ai_AOI(Latch_ai_Feeder2[4], Feeder2.DummyLoad_LCWR_Flow, System.Rst);


//Latch_ai_AOI(Latch_ai_Feeder2[5], Feeder2.DummyLoad_LCWR_Temp, System.Reset);


Latch_bi_AOI(Latch_bi_Feeder2[0], Feeder2.TxLineSw, System.Rst);





// Cavity 1


Latch_ai_AOI(Latch_ai_Cav1[0], Cav1.LCWR_Temp[0], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[1], Cav1.LCWR_Temp[1], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[2], Cav1.LCWR_Temp[2], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[3], Cav1.LCWR_Temp[3], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[4], Cav1.LCWR_Temp[4], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[5], Cav1.LCWR_Temp[5], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[6], Cav1.LCWR_Temp[6], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[7], Cav1.LCWR_Temp[7], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[8], Cav1.LCWR_Temp[8], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[9], Cav1.LCWR_Temp[9], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[10], Cav1.LCWR_Temp[10], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[11], Cav1.LCWR_Temp[11], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[12], Cav1.LCWR_Temp[12], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[13], Cav1.LCWR_Temp[13], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[14], Cav1.LCWR_Temp[14], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[15], Cav1.LCWR_Flow[0], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[16], Cav1.LCWR_Flow[1], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[17], Cav1.LCWR_Flow[2], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[18], Cav1.LCWR_Flow[3], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[19], Cav1.LCWR_Flow[4], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[20], Cav1.LCWR_Flow[5], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[21], Cav1.LCWR_Flow[6], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[22], Cav1.LCWR_Flow[7], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[23], Cav1.LCWR_Flow[8], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[24], Cav1.LCWR_Flow[9], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[25], Cav1.LCWR_Flow[10], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[26], Cav1.LCWR_Flow[11], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[27], Cav1.LCWR_Flow[12], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[28], Cav1.LCWR_Flow[13], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[29], Cav1.LCWR_Flow[14], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[30], Cav1.Surf_Temp[0], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[31], Cav1.Surf_Temp[1], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[32], Cav1.Surf_Temp[2], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[33], Cav1.Surf_Temp[3], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[34], Cav1.Surf_Temp[4], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[35], Cav1.Surf_Temp[5], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[36], Cav1.Surf_Temp[6], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[37], Cav1.Surf_Temp[7], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[38], Cav1.Surf_Temp[8], System.Rst);


Latch_ai_AOI(Latch_ai_Cav1[39], Cav1.CouplerTemp, System.Rst);


Latch_bi_AOI(Latch_bi_Cav1[0], Cav1.CouplerBlower.Flow_Sw, System.Rst);


Latch_bi_AOI(Latch_bi_Cav1[1], Vacuum.Cav1_CCG_Relay, System.Rst);


Latch_bi_AOI(Latch_bi_Cav1[2], Vacuum.Cav1_PiraniRelay, System.Rst);





// Cavity 2


Latch_ai_AOI(Latch_ai_Cav2[0], Cav2.LCWR_Temp[0], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[1], Cav2.LCWR_Temp[1], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[2], Cav2.LCWR_Temp[2], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[3], Cav2.LCWR_Temp[3], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[4], Cav2.LCWR_Temp[4], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[5], Cav2.LCWR_Temp[5], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[6], Cav2.LCWR_Temp[6], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[7], Cav2.LCWR_Temp[7], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[8], Cav2.LCWR_Temp[8], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[9], Cav2.LCWR_Temp[9], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[10], Cav2.LCWR_Temp[10], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[11], Cav2.LCWR_Temp[11], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[12], Cav2.LCWR_Temp[12], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[13], Cav2.LCWR_Temp[13], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[14], Cav2.LCWR_Temp[14], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[15], Cav2.LCWR_Flow[0], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[16], Cav2.LCWR_Flow[1], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[17], Cav2.LCWR_Flow[2], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[18], Cav2.LCWR_Flow[3], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[19], Cav2.LCWR_Flow[4], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[20], Cav2.LCWR_Flow[5], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[21], Cav2.LCWR_Flow[6], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[22], Cav2.LCWR_Flow[7], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[23], Cav2.LCWR_Flow[8], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[24], Cav2.LCWR_Flow[9], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[25], Cav2.LCWR_Flow[10], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[26], Cav2.LCWR_Flow[11], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[27], Cav2.LCWR_Flow[12], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[28], Cav2.LCWR_Flow[13], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[29], Cav2.LCWR_Flow[14], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[30], Cav2.Surf_Temp[0], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[31], Cav2.Surf_Temp[1], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[32], Cav2.Surf_Temp[2], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[33], Cav2.Surf_Temp[3], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[34], Cav2.Surf_Temp[4], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[35], Cav2.Surf_Temp[5], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[36], Cav2.Surf_Temp[6], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[37], Cav2.Surf_Temp[7], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[38], Cav2.Surf_Temp[8], System.Rst);


Latch_ai_AOI(Latch_ai_Cav2[39], Cav2.CouplerTemp, System.Rst);


Latch_bi_AOI(Latch_bi_Cav2[0], Cav2.CouplerBlower.Flow_Sw, System.Rst);


Latch_bi_AOI(Latch_bi_Cav2[1], Vacuum.Cav2_CCG_Relay, System.Rst);


Latch_bi_AOI(Latch_bi_Cav2[2], Vacuum.Cav2_PiraniRelay, System.Rst);





// Misc


Latch_bi_AOI(Latch_bi_Misc[0], Local_RF_OFF, System.Rst);


Latch_bi_AOI(Latch_bi_Misc[1], Modules.R01.CommunicationOK, System.Rst);


Latch_bi_AOI(Latch_bi_Misc[2], Modules.R03.CommunicationOK, System.Rst);


Latch_bi_AOI(Latch_bi_Misc[3], Modules.Cav1_Tuner.CommunicationOK, System.Rst);


Latch_bi_AOI(Latch_bi_Misc[4], Modules.Cav2_Tuner.CommunicationOK, System.Rst);


Latch_bi_AOI(Latch_bi_Misc[5], Modules.LLRF1_DIG.CommunicationOK, System.Rst);


Latch_bi_AOI(Latch_bi_Misc[6], Modules.LLRF1_ANLG.CommunicationOK, System.Rst);


Latch_bi_AOI(Latch_bi_Misc[7], Modules.LLRF2_DIG.CommunicationOK, System.Rst);


Latch_bi_AOI(Latch_bi_Misc[8], Modules.LLRF2_ANLG.CommunicationOK, System.Rst);





// Tuner 1


Latch_bi_AOI(Latch_bi_Tuner1[0], Tuner1.PS, System.Rst);


Latch_bi_AOI(Latch_bi_Tuner1[1], Tuner1.Error, System.Rst);


Latch_bi_AOI(Latch_bi_Tuner1[2], Tuner1.Position_Invalid, System.Rst);


Latch_bi_AOI(Latch_bi_Tuner1[3], Tuner1.ConnectionFaulted, System.Rst);


Latch_bi_AOI(Latch_bi_Tuner1[4], Tuner1.InRange, System.Rst);





// Tuner 2


Latch_bi_AOI(Latch_bi_Tuner2[0], Tuner2.PS, System.Rst);


Latch_bi_AOI(Latch_bi_Tuner2[1], Tuner2.Error, System.Rst);


Latch_bi_AOI(Latch_bi_Tuner2[2], Tuner2.Position_Invalid, System.Rst);


Latch_bi_AOI(Latch_bi_Tuner2[3], Tuner2.ConnectionFaulted, System.Rst);


Latch_bi_AOI(Latch_bi_Tuner2[4], Tuner2.InRange, System.Rst);















