
/* LLRF 1 Modbus RTU */


/* Updated for modbus register map v4 (modbus_registers_(4).h) */





/* Digital Chassis */





/* Channel Mapping


0: MO


1: Cavity Cell


2: Cavity Forward


3: Cavity Reverse


4: Circulator Forward


5: Circulator Reverse


6: Dummy Load Forward


7: Dummy Load Reverse


8: RF Drive 1


9: RF Drive 2


*/





// RF Powers


// MB_ADC0..9_MON_AMP = 0..9 (unchanged)


LLRF2_Power[0].RawVal := R01:2:I00.Command00.Data400000;


LLRF2_Power[1].RawVal := R01:2:I00.Command00.Data400001;


LLRF2_Power[2].RawVal := R01:2:I00.Command00.Data400002;


LLRF2_Power[3].RawVal := R01:2:I00.Command00.Data400003;


LLRF2_Power[4].RawVal := R01:2:I00.Command00.Data400004;


LLRF2_Power[5].RawVal := R01:2:I00.Command00.Data400005;


LLRF2_Power[6].RawVal := R01:2:I00.Command00.Data400006;


LLRF2_Power[7].RawVal := R01:2:I00.Command00.Data400007;


LLRF2_Power[8].RawVal := R01:2:I00.Command00.Data400008;


LLRF2_Power[9].RawVal := R01:2:I00.Command00.Data400009;





// MB_ADC0..9_MON_PHS = 10..29 (unchanged, each phase uses 2 registers lo/hi)


LLRF2_Power_Phase[0] := R01:2:I00.Command03.Data400010;


LLRF2_Power_Phase[1] := R01:2:I00.Command03.Data400012;


LLRF2_Power_Phase[2] := R01:2:I00.Command03.Data400014;


LLRF2_Power_Phase[3] := R01:2:I00.Command03.Data400016;


LLRF2_Power_Phase[4] := R01:2:I00.Command03.Data400018;


LLRF2_Power_Phase[5] := R01:2:I00.Command03.Data400020;


LLRF2_Power_Phase[6] := R01:2:I00.Command03.Data400022;


LLRF2_Power_Phase[7] := R01:2:I00.Command03.Data400024;


LLRF2_Power_Phase[8] := R01:2:I00.Command03.Data400026;


LLRF2_Power_Phase[9] := R01:2:I00.Command03.Data400028;





// MB_INLK_FIRST_FAULT_STATUS = 30 (new register - add read if needed)


// LLRF2.DIG.First_Fault_Sts := R01:2:I00.Command00.Data400030;





// MB_INLK_STATUS = 31 (was 30, +1)


LLRF2_Power[0].Sts := R01:2:I00.Command00.Data400031.0;


LLRF2_Power[1].Sts := R01:2:I00.Command00.Data400031.1;


LLRF2_Power[2].Sts := R01:2:I00.Command00.Data400031.2;


LLRF2_Power[3].Sts := R01:2:I00.Command00.Data400031.3;


LLRF2_Power[4].Sts := R01:2:I00.Command00.Data400031.4;


LLRF2_Power[5].Sts := R01:2:I00.Command00.Data400031.5;


LLRF2_Power[6].Sts := R01:2:I00.Command00.Data400031.6;


LLRF2_Power[7].Sts := R01:2:I00.Command00.Data400031.7;


LLRF2_Power[8].Sts := R01:2:I00.Command00.Data400031.8;


LLRF2_Power[9].Sts := R01:2:I00.Command00.Data400031.9;





// MB_INLK_LATCH = 33 (was 32, +1)


LLRF2_Power[0].Ltch := R01:2:I00.Command00.Data400033.0;


LLRF2_Power[1].Ltch := R01:2:I00.Command00.Data400033.1;


LLRF2_Power[2].Ltch := R01:2:I00.Command00.Data400033.2;


LLRF2_Power[3].Ltch := R01:2:I00.Command00.Data400033.3;


LLRF2_Power[4].Ltch := R01:2:I00.Command00.Data400033.4;


LLRF2_Power[5].Ltch := R01:2:I00.Command00.Data400033.5;


LLRF2_Power[6].Ltch := R01:2:I00.Command00.Data400033.6;


LLRF2_Power[7].Ltch := R01:2:I00.Command00.Data400033.7;


LLRF2_Power[8].Ltch := R01:2:I00.Command00.Data400033.8;


LLRF2_Power[9].Ltch := R01:2:I00.Command00.Data400033.9;





// MB_INLK_MODE_ADC0..9 = 65..74 (was 64..73, +1)


R01:2:O00.Command01.Data400065 := LLRF2_Power[0].Intlk_Mode;


R01:2:O00.Command01.Data400066 := LLRF2_Power[1].Intlk_Mode;


R01:2:O00.Command01.Data400067 := LLRF2_Power[2].Intlk_Mode;


R01:2:O00.Command01.Data400068 := LLRF2_Power[3].Intlk_Mode;


R01:2:O00.Command01.Data400069 := LLRF2_Power[4].Intlk_Mode;


R01:2:O00.Command01.Data400070 := LLRF2_Power[5].Intlk_Mode;


R01:2:O00.Command01.Data400071 := LLRF2_Power[6].Intlk_Mode;


R01:2:O00.Command01.Data400072 := LLRF2_Power[7].Intlk_Mode;


R01:2:O00.Command01.Data400073 := LLRF2_Power[8].Intlk_Mode;


R01:2:O00.Command01.Data400074 := LLRF2_Power[9].Intlk_Mode;





// MB_INLK_MASK = 75 (was 74, +1)


R01:2:O00.Command01.Data400075.0 := LLRF2_Power[0].Byp;


R01:2:O00.Command01.Data400075.1 := LLRF2_Power[1].Byp;


R01:2:O00.Command01.Data400075.2 := LLRF2_Power[2].Byp;


R01:2:O00.Command01.Data400075.3 := LLRF2_Power[3].Byp;


R01:2:O00.Command01.Data400075.4 := LLRF2_Power[4].Byp;


R01:2:O00.Command01.Data400075.5 := LLRF2_Power[5].Byp;


R01:2:O00.Command01.Data400075.6 := LLRF2_Power[6].Byp;


R01:2:O00.Command01.Data400075.7 := LLRF2_Power[7].Byp;


R01:2:O00.Command01.Data400075.8 := LLRF2_Power[8].Byp;


R01:2:O00.Command01.Data400075.9 := LLRF2_Power[9].Byp;





// MB_INLK_AMP_LO_ADC0..9 = 45..54 (was 44..53, +1)


R01:2:O00.Command01.Data400045 := LLRF2_Power[0].Lo_SP_Raw;


R01:2:O00.Command01.Data400046 := LLRF2_Power[1].Lo_SP_Raw;


R01:2:O00.Command01.Data400047 := LLRF2_Power[2].Lo_SP_Raw;


R01:2:O00.Command01.Data400048 := LLRF2_Power[3].Lo_SP_Raw;


R01:2:O00.Command01.Data400049 := LLRF2_Power[4].Lo_SP_Raw;


R01:2:O00.Command01.Data400050 := LLRF2_Power[5].Lo_SP_Raw;


R01:2:O00.Command01.Data400051 := LLRF2_Power[6].Lo_SP_Raw;


R01:2:O00.Command01.Data400052 := LLRF2_Power[7].Lo_SP_Raw;


R01:2:O00.Command01.Data400053 := LLRF2_Power[8].Lo_SP_Raw;


R01:2:O00.Command01.Data400054 := LLRF2_Power[9].Lo_SP_Raw;





// MB_INLK_AMP_HI_ADC0..9 = 55..64 (was 54..63, +1)


R01:2:O00.Command01.Data400055 := LLRF2_Power[0].Hi_SP_Raw;


R01:2:O00.Command01.Data400056 := LLRF2_Power[1].Hi_SP_Raw;


R01:2:O00.Command01.Data400057 := LLRF2_Power[2].Hi_SP_Raw;


R01:2:O00.Command01.Data400058 := LLRF2_Power[3].Hi_SP_Raw;


R01:2:O00.Command01.Data400059 := LLRF2_Power[4].Hi_SP_Raw;


R01:2:O00.Command01.Data400060 := LLRF2_Power[5].Hi_SP_Raw;


R01:2:O00.Command01.Data400061 := LLRF2_Power[6].Hi_SP_Raw;


R01:2:O00.Command01.Data400062 := LLRF2_Power[7].Hi_SP_Raw;


R01:2:O00.Command01.Data400063 := LLRF2_Power[8].Hi_SP_Raw;


R01:2:O00.Command01.Data400064 := LLRF2_Power[9].Hi_SP_Raw;





// MB_FPGA_UP..VCCBRAM = 99..103 (was 98..102, +1)


/*LLRF2.DIG.Uptime  := R01:2:I00.Command02.Data400099;


LLRF2.DIG.Temp    := R01:2:I00.Command02.Data400100;


LLRF2.DIG.VCCINT  := R01:2:I00.Command02.Data400101;


LLRF2.DIG.VCCAUX  := R01:2:I00.Command02.Data400102;


LLRF2.DIG.VCCBRAM := R01:2:I00.Command02.Data400103;*/





//Arc Detectors


// MB_ARC_PERMIT_RAW = 37 (was 36, +1)


LLRF2_Arc_Detector[0].Sts := R01:2:I00.Command00.Data400037.0;


LLRF2_Arc_Detector[1].Sts := R01:2:I00.Command00.Data400037.1;


LLRF2_Arc_Detector[2].Sts := R01:2:I00.Command00.Data400037.2;





// MB_ARC_PERMIT_LATCH = 36 (was 35, +1)


LLRF2_Arc_Detector[0].Ltch := R01:2:I00.Command00.Data400036.0;


LLRF2_Arc_Detector[1].Ltch := R01:2:I00.Command00.Data400036.1;


LLRF2_Arc_Detector[2].Ltch := R01:2:I00.Command00.Data400036.2;





LLRF2.DIG.Arc_Sum := R01:2:I00.Command00.Data400038;





// MB_ARC_PERMIT_MASK = 93 (was 92, +1)


R01:2:O00.Command01.Data400093.0 := LLRF2_Arc_Detector[0].Byp;


R01:2:O00.Command01.Data400093.1 := LLRF2_Arc_Detector[1].Byp;


R01:2:O00.Command01.Data400093.2 := LLRF2_Arc_Detector[2].Byp;


/*


// MB_ARC_TEST_MASK = 96 (was 95, +1)


// Note: MB_ARC_TEST_STB = 97 — add strobe write here if required


R01:2:O00.Command01.Data400096.0 := LLRF2_Arc_Detector[0].Test;


R01:2:O00.Command01.Data400096.1 := LLRF2_Arc_Detector[1].Test;


R01:2:O00.Command01.Data400096.2 := LLRF2_Arc_Detector[2].Test;





// MB_ARC_RESET_ARC_DEV = 94 (was 93, +1)


R01:2:O00.Command01.Data400094.0 := LLRF2_Arc_Detector[0].Rst;


R01:2:O00.Command01.Data400094.1 := LLRF2_Arc_Detector[1].Rst;


R01:2:O00.Command01.Data400094.2 := LLRF2_Arc_Detector[2].Rst;*/





// MB_INLK_PERMIT = 32 (was 31, +1)


LLRF2.DIG.RF_Power_Sum := R01:2:I00.Command00.Data400032;


// MB_ARC_PERMIT_SUM = 38 (was 37, +1)


//LLRF2.DIG.Arc_Sum := R01:2:I00.Command00.Data400038;


// MB_INLK_RESET = 76 (was 75, +1)


R01:2:O00.Command01.Data400076 := LLRF2.DIG.Rst_Power;


R01:2:O00.Command01.Data400095 := LLRF2.DIG.Rst_Arc;


//R01:1:O00.Command01.Data400088 := LLRF2.DIG.Arc_Sum;








/* Analog Chassis */


LLRF2.ANLG.PSU_UP := R01:2:I10.Command00.Data400000/6;


LLRF2.ANLG.PSU_TEMP := R01:2:I10.Command00.Data400001/256;


LLRF2.ANLG.PSU_VCCINT := R01:2:I10.Command00.Data400032/1000;


LLRF2.ANLG.PSU_VCCAUX := R01:2:I10.Command00.Data400003/1000;


LLRF2.ANLG.PSU_VCCBRAM := R01:2:I10.Command00.Data400004/1000;


LLRF2.ANLG.PSU_IN_VOLTAGE := R01:2:I10.Command00.Data400005/1000;


LLRF2.ANLG.PSU_IN_CURRENT := R01:2:I10.Command00.Data400006/1000;


LLRF2.ANLG.PSU_A_VOLTAGE := R01:2:I10.Command00.Data400007/1000;


LLRF2.ANLG.PSU_A_CURRENT := R01:2:I10.Command00.Data400008/1000;


LLRF2.ANLG.PSU_B_VOLTAGE := R01:2:I10.Command00.Data400009/1000;


LLRF2.ANLG.PSU_B_CURRENT := R01:2:I10.Command00.Data400010/1000;


LLRF2.ANLG.PSU_C_VOLTAGE := R01:2:I10.Command00.Data400011/1000;


LLRF2.ANLG.PSU_C_CURRENT := R01:2:I10.Command00.Data400012/1000;


LLRF2.ANLG.PSU_D_VOLTAGE := R01:2:I10.Command00.Data400013/1000;


LLRF2.ANLG.PSU_D_CURRENT := R01:2:I10.Command00.Data400014/1000;


LLRF2.ANLG.PSU_E_VOLTAGE := R01:2:I10.Command00.Data400015/1000;


LLRF2.ANLG.PSU_E_CURRENT := R01:2:I10.Command00.Data400016/1000;


LLRF2.ANLG.DC_A_TEMP := R01:2:I10.Command00.Data400017/256;


LLRF2.ANLG.DC_A_VOLTAGE := R01:2:I10.Command00.Data400018/1000;


LLRF2.ANLG.DC_B_TEMP := R01:2:I10.Command00.Data400019/256;


LLRF2.ANLG.DC_B_VOLTAGE := R01:2:I10.Command00.Data400000/1000;


LLRF2.ANLG.INLK_A_Flags := R01:2:I10.Command00.Data400021;


LLRF2.ANLG.INLK_A_VAL := R01:2:I10.Command00.Data400022/256;


LLRF2.ANLG.INLK_A_VAL_MAX := R01:2:I10.Command00.Data400023/256;


LLRF2.ANLG.INLK_A_VAL_MIN := R01:2:I10.Command00.Data400024/256;


LLRF2.ANLG.INLK_B_Flags := R01:2:I10.Command00.Data400025;


LLRF2.ANLG.INLK_B_VAL := R01:2:I10.Command00.Data400026/256;


LLRF2.ANLG.INLK_B_VAL_MAX := R01:2:I10.Command00.Data400027/256;


LLRF2.ANLG.INLK_B_VAL_MIN := R01:2:I10.Command00.Data400028/256;


LLRF2.ANLG.PSU_ERR_FLAGS := R01:2:I10.Command00.Data400029;


LLRF2.ANLG.PSU_SET_PWR_FLAG := R01:2:I10.Command00.Data400030;


LLRF2.ANLG.PSU_SET_FREQ := R01:2:I10.Command00.Data400031;


LLRF2.ANLG.PSU_SET_PHASE_A := R01:2:I10.Command00.Data400032;


LLRF2.ANLG.PSU_SET_PHASE_C := R01:2:I10.Command00.Data400033;


LLRF2.ANLG.PSU_SET_PHASE_C := R01:2:I10.Command00.Data400034;


LLRF2.ANLG.PSU_SET_PHASE_D := R01:2:I10.Command00.Data400035;


LLRF2.ANLG.PSU_SET_PHASE_E := R01:2:I10.Command00.Data400036;


LLRF2.ANLG.INLK_A_RESET_PERMIT := R01:2:I10.Command00.Data400037;


LLRF2.ANLG.INLK_A_RESET_MINMAX := R01:2:I10.Command00.Data400038;


LLRF2.ANLG.INLK_A_MIN_THR := R01:2:I10.Command00.Data400039/256;


LLRF2.ANLG.INLK_A_MAX_THR := R01:2:I10.Command00.Data400040/256;


LLRF2.ANLG.INLK_B_RESET_PERMIT := R01:2:I10.Command00.Data400041;


LLRF2.ANLG.INLK_B_RESET_MINMAX := R01:2:I10.Command00.Data400042;


LLRF2.ANLG.INLK_B_MIN_THR := R01:2:I10.Command00.Data400043/256;


LLRF2.ANLG.INLK_B_MAX_THR := R01:2:I10.Command00.Data400044/256;


LLRF2.ANLG.UP_A_SW := R01:2:I10.Command00.Data400045;


LLRF2.ANLG.UP_B_SW := R01:2:I10.Command00.Data400046;


LLRF2.ANLG.UP_A_ATT := R01:2:I10.Command00.Data400047/2;


LLRF2.ANLG.UP_B_ATT := R01:2:I10.Command00.Data400048/2;


LLRF2.ANLG.PSU_RESET_ERR_FLAGS := R01:2:I10.Command00.Data400049;
