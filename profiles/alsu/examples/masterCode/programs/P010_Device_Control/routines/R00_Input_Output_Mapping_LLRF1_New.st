
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


LLRF1_Power[0].RawVal := Local:2:I00.Command00.Data400000;


LLRF1_Power[1].RawVal := Local:2:I00.Command00.Data400001;


LLRF1_Power[2].RawVal := Local:2:I00.Command00.Data400002;


LLRF1_Power[3].RawVal := Local:2:I00.Command00.Data400003;


LLRF1_Power[4].RawVal := Local:2:I00.Command00.Data400004;


LLRF1_Power[5].RawVal := Local:2:I00.Command00.Data400005;


LLRF1_Power[6].RawVal := Local:2:I00.Command00.Data400006;


LLRF1_Power[7].RawVal := Local:2:I00.Command00.Data400007;


LLRF1_Power[8].RawVal := Local:2:I00.Command00.Data400008;


LLRF1_Power[9].RawVal := Local:2:I00.Command00.Data400009;





// MB_ADC0..9_MON_PHS = 10..29 (unchanged, each phase uses 2 registers lo/hi)


LLRF1_Power_Phase[0] := Local:2:I00.Command03.Data400010;


LLRF1_Power_Phase[1] := Local:2:I00.Command03.Data400012;


LLRF1_Power_Phase[2] := Local:2:I00.Command03.Data400014;


LLRF1_Power_Phase[3] := Local:2:I00.Command03.Data400016;


LLRF1_Power_Phase[4] := Local:2:I00.Command03.Data400018;


LLRF1_Power_Phase[5] := Local:2:I00.Command03.Data400020;


LLRF1_Power_Phase[6] := Local:2:I00.Command03.Data400022;


LLRF1_Power_Phase[7] := Local:2:I00.Command03.Data400024;


LLRF1_Power_Phase[8] := Local:2:I00.Command03.Data400026;


LLRF1_Power_Phase[9] := Local:2:I00.Command03.Data400028;





// MB_INLK_FIRST_FAULT_STATUS = 30 (new register - add read if needed)


// LLRF1.DIG.First_Fault_Sts := Local:2:I00.Command00.Data400030;





// MB_INLK_STATUS = 31 (was 30, +1)


LLRF1_Power[0].Sts := Local:2:I00.Command00.Data400031.0;


LLRF1_Power[1].Sts := Local:2:I00.Command00.Data400031.1;


LLRF1_Power[2].Sts := Local:2:I00.Command00.Data400031.2;


LLRF1_Power[3].Sts := Local:2:I00.Command00.Data400031.3;


LLRF1_Power[4].Sts := Local:2:I00.Command00.Data400031.4;


LLRF1_Power[5].Sts := Local:2:I00.Command00.Data400031.5;


LLRF1_Power[6].Sts := Local:2:I00.Command00.Data400031.6;


LLRF1_Power[7].Sts := Local:2:I00.Command00.Data400031.7;


LLRF1_Power[8].Sts := Local:2:I00.Command00.Data400031.8;


LLRF1_Power[9].Sts := Local:2:I00.Command00.Data400031.9;





// MB_INLK_LATCH = 33 (was 32, +1)


LLRF1_Power[0].Ltch := Local:2:I00.Command00.Data400033.0;


LLRF1_Power[1].Ltch := Local:2:I00.Command00.Data400033.1;


LLRF1_Power[2].Ltch := Local:2:I00.Command00.Data400033.2;


LLRF1_Power[3].Ltch := Local:2:I00.Command00.Data400033.3;


LLRF1_Power[4].Ltch := Local:2:I00.Command00.Data400033.4;


LLRF1_Power[5].Ltch := Local:2:I00.Command00.Data400033.5;


LLRF1_Power[6].Ltch := Local:2:I00.Command00.Data400033.6;


LLRF1_Power[7].Ltch := Local:2:I00.Command00.Data400033.7;


LLRF1_Power[8].Ltch := Local:2:I00.Command00.Data400033.8;


LLRF1_Power[9].Ltch := Local:2:I00.Command00.Data400033.9;





// MB_INLK_MODE_ADC0..9 = 65..74 (was 64..73, +1)


Local:2:O00.Command01.Data400065 := LLRF1_Power[0].Intlk_Mode;


Local:2:O00.Command01.Data400066 := LLRF1_Power[1].Intlk_Mode;


Local:2:O00.Command01.Data400067 := LLRF1_Power[2].Intlk_Mode;


Local:2:O00.Command01.Data400068 := LLRF1_Power[3].Intlk_Mode;


Local:2:O00.Command01.Data400069 := LLRF1_Power[4].Intlk_Mode;


Local:2:O00.Command01.Data400070 := LLRF1_Power[5].Intlk_Mode;


Local:2:O00.Command01.Data400071 := LLRF1_Power[6].Intlk_Mode;


Local:2:O00.Command01.Data400072 := LLRF1_Power[7].Intlk_Mode;


Local:2:O00.Command01.Data400073 := LLRF1_Power[8].Intlk_Mode;


Local:2:O00.Command01.Data400074 := LLRF1_Power[9].Intlk_Mode;





// MB_INLK_MASK = 75 (was 74, +1)


Local:2:O00.Command01.Data400075.0 := LLRF1_Power[0].Byp;


Local:2:O00.Command01.Data400075.1 := LLRF1_Power[1].Byp;


Local:2:O00.Command01.Data400075.2 := LLRF1_Power[2].Byp;


Local:2:O00.Command01.Data400075.3 := LLRF1_Power[3].Byp;


Local:2:O00.Command01.Data400075.4 := LLRF1_Power[4].Byp;


Local:2:O00.Command01.Data400075.5 := LLRF1_Power[5].Byp;


Local:2:O00.Command01.Data400075.6 := LLRF1_Power[6].Byp;


Local:2:O00.Command01.Data400075.7 := LLRF1_Power[7].Byp;


Local:2:O00.Command01.Data400075.8 := LLRF1_Power[8].Byp;


Local:2:O00.Command01.Data400075.9 := LLRF1_Power[9].Byp;





// MB_INLK_AMP_LO_ADC0..9 = 45..54 (was 44..53, +1)


Local:2:O00.Command01.Data400045 := LLRF1_Power[0].Lo_SP_Raw;


Local:2:O00.Command01.Data400046 := LLRF1_Power[1].Lo_SP_Raw;


Local:2:O00.Command01.Data400047 := LLRF1_Power[2].Lo_SP_Raw;


Local:2:O00.Command01.Data400048 := LLRF1_Power[3].Lo_SP_Raw;


Local:2:O00.Command01.Data400049 := LLRF1_Power[4].Lo_SP_Raw;


Local:2:O00.Command01.Data400050 := LLRF1_Power[5].Lo_SP_Raw;


Local:2:O00.Command01.Data400051 := LLRF1_Power[6].Lo_SP_Raw;


Local:2:O00.Command01.Data400052 := LLRF1_Power[7].Lo_SP_Raw;


Local:2:O00.Command01.Data400053 := LLRF1_Power[8].Lo_SP_Raw;


Local:2:O00.Command01.Data400054 := LLRF1_Power[9].Lo_SP_Raw;





// MB_INLK_AMP_HI_ADC0..9 = 55..64 (was 54..63, +1)


Local:2:O00.Command01.Data400055 := LLRF1_Power[0].Hi_SP_Raw;


Local:2:O00.Command01.Data400056 := LLRF1_Power[1].Hi_SP_Raw;


Local:2:O00.Command01.Data400057 := LLRF1_Power[2].Hi_SP_Raw;


Local:2:O00.Command01.Data400058 := LLRF1_Power[3].Hi_SP_Raw;


Local:2:O00.Command01.Data400059 := LLRF1_Power[4].Hi_SP_Raw;


Local:2:O00.Command01.Data400060 := LLRF1_Power[5].Hi_SP_Raw;


Local:2:O00.Command01.Data400061 := LLRF1_Power[6].Hi_SP_Raw;


Local:2:O00.Command01.Data400062 := LLRF1_Power[7].Hi_SP_Raw;


Local:2:O00.Command01.Data400063 := LLRF1_Power[8].Hi_SP_Raw;


Local:2:O00.Command01.Data400064 := LLRF1_Power[9].Hi_SP_Raw;





// MB_FPGA_UP..VCCBRAM = 99..103 (was 98..102, +1)


/*LLRF1.DIG.Uptime  := Local:2:I00.Command02.Data400099;


LLRF1.DIG.Temp    := Local:2:I00.Command02.Data400100;


LLRF1.DIG.VCCINT  := Local:2:I00.Command02.Data400101;


LLRF1.DIG.VCCAUX  := Local:2:I00.Command02.Data400102;


LLRF1.DIG.VCCBRAM := Local:2:I00.Command02.Data400103;*/





//Arc Detectors


// MB_ARC_PERMIT_RAW = 37 (was 36, +1)


LLRF1_Arc_Detector[0].Sts := Local:2:I00.Command00.Data400037.0;


LLRF1_Arc_Detector[1].Sts := Local:2:I00.Command00.Data400037.1;


LLRF1_Arc_Detector[2].Sts := Local:2:I00.Command00.Data400037.2;





// MB_ARC_PERMIT_LATCH = 36 (was 35, +1)


LLRF1_Arc_Detector[0].Ltch := Local:2:I00.Command00.Data400036.0;


LLRF1_Arc_Detector[1].Ltch := Local:2:I00.Command00.Data400036.1;


LLRF1_Arc_Detector[2].Ltch := Local:2:I00.Command00.Data400036.2;





LLRF1.DIG.Arc_Sum := Local:2:I00.Command00.Data400038;





// MB_ARC_PERMIT_MASK = 93 (was 92, +1)


Local:2:O00.Command01.Data400093.0 := LLRF1_Arc_Detector[0].Byp;


Local:2:O00.Command01.Data400093.1 := LLRF1_Arc_Detector[1].Byp;


Local:2:O00.Command01.Data400093.2 := LLRF1_Arc_Detector[2].Byp;


/*


// MB_ARC_TEST_MASK = 96 (was 95, +1)


// Note: MB_ARC_TEST_STB = 97 — add strobe write here if required


Local:2:O00.Command01.Data400096.0 := LLRF1_Arc_Detector[0].Test;


Local:2:O00.Command01.Data400096.1 := LLRF1_Arc_Detector[1].Test;


Local:2:O00.Command01.Data400096.2 := LLRF1_Arc_Detector[2].Test;





// MB_ARC_RESET_ARC_DEV = 94 (was 93, +1)


Local:2:O00.Command01.Data400094.0 := LLRF1_Arc_Detector[0].Rst;


Local:2:O00.Command01.Data400094.1 := LLRF1_Arc_Detector[1].Rst;


Local:2:O00.Command01.Data400094.2 := LLRF1_Arc_Detector[2].Rst;*/





// MB_INLK_PERMIT = 32 (was 31, +1)


LLRF1.DIG.RF_Power_Sum := Local:2:I00.Command00.Data400032;


// MB_ARC_PERMIT_SUM = 38 (was 37, +1)


//LLRF1.DIG.Arc_Sum := Local:2:I00.Command00.Data400038;


// MB_INLK_RESET = 76 (was 75, +1)


Local:2:O00.Command01.Data400076 := LLRF1.DIG.Rst_Power;


Local:2:O00.Command01.Data400095 := LLRF1.DIG.Rst_Arc;


//Local:1:O00.Command01.Data400088 := LLRF1.DIG.Arc_Sum;








/* Analog Chassis */


LLRF1.ANLG.PSU_UP := Local:2:I10.Command00.Data400000/6;


LLRF1.ANLG.PSU_TEMP := Local:2:I10.Command00.Data400001/256;


LLRF1.ANLG.PSU_VCCINT := Local:2:I10.Command00.Data400032/1000;


LLRF1.ANLG.PSU_VCCAUX := Local:2:I10.Command00.Data400003/1000;


LLRF1.ANLG.PSU_VCCBRAM := Local:2:I10.Command00.Data400004/1000;


LLRF1.ANLG.PSU_IN_VOLTAGE := Local:2:I10.Command00.Data400005/1000;


LLRF1.ANLG.PSU_IN_CURRENT := Local:2:I10.Command00.Data400006/1000;


LLRF1.ANLG.PSU_A_VOLTAGE := Local:2:I10.Command00.Data400007/1000;


LLRF1.ANLG.PSU_A_CURRENT := Local:2:I10.Command00.Data400008/1000;


LLRF1.ANLG.PSU_B_VOLTAGE := Local:2:I10.Command00.Data400009/1000;


LLRF1.ANLG.PSU_B_CURRENT := Local:2:I10.Command00.Data400010/1000;


LLRF1.ANLG.PSU_C_VOLTAGE := Local:2:I10.Command00.Data400011/1000;


LLRF1.ANLG.PSU_C_CURRENT := Local:2:I10.Command00.Data400012/1000;


LLRF1.ANLG.PSU_D_VOLTAGE := Local:2:I10.Command00.Data400013/1000;


LLRF1.ANLG.PSU_D_CURRENT := Local:2:I10.Command00.Data400014/1000;


LLRF1.ANLG.PSU_E_VOLTAGE := Local:2:I10.Command00.Data400015/1000;


LLRF1.ANLG.PSU_E_CURRENT := Local:2:I10.Command00.Data400016/1000;


LLRF1.ANLG.DC_A_TEMP := Local:2:I10.Command00.Data400017/256;


LLRF1.ANLG.DC_A_VOLTAGE := Local:2:I10.Command00.Data400018/1000;


LLRF1.ANLG.DC_B_TEMP := Local:2:I10.Command00.Data400019/256;


LLRF1.ANLG.DC_B_VOLTAGE := Local:2:I10.Command00.Data400000/1000;


LLRF1.ANLG.INLK_A_Flags := Local:2:I10.Command00.Data400021;


LLRF1.ANLG.INLK_A_VAL := Local:2:I10.Command00.Data400022/256;


LLRF1.ANLG.INLK_A_VAL_MAX := Local:2:I10.Command00.Data400023/256;


LLRF1.ANLG.INLK_A_VAL_MIN := Local:2:I10.Command00.Data400024/256;


LLRF1.ANLG.INLK_B_Flags := Local:2:I10.Command00.Data400025;


LLRF1.ANLG.INLK_B_VAL := Local:2:I10.Command00.Data400026/256;


LLRF1.ANLG.INLK_B_VAL_MAX := Local:2:I10.Command00.Data400027/256;


LLRF1.ANLG.INLK_B_VAL_MIN := Local:2:I10.Command00.Data400028/256;


LLRF1.ANLG.PSU_ERR_FLAGS := Local:2:I10.Command00.Data400029;


LLRF1.ANLG.PSU_SET_PWR_FLAG := Local:2:I10.Command00.Data400030;


LLRF1.ANLG.PSU_SET_FREQ := Local:2:I10.Command00.Data400031;


LLRF1.ANLG.PSU_SET_PHASE_A := Local:2:I10.Command00.Data400032;


LLRF1.ANLG.PSU_SET_PHASE_C := Local:2:I10.Command00.Data400033;


LLRF1.ANLG.PSU_SET_PHASE_C := Local:2:I10.Command00.Data400034;


LLRF1.ANLG.PSU_SET_PHASE_D := Local:2:I10.Command00.Data400035;


LLRF1.ANLG.PSU_SET_PHASE_E := Local:2:I10.Command00.Data400036;


LLRF1.ANLG.INLK_A_RESET_PERMIT := Local:2:I10.Command00.Data400037;


LLRF1.ANLG.INLK_A_RESET_MINMAX := Local:2:I10.Command00.Data400038;


LLRF1.ANLG.INLK_A_MIN_THR := Local:2:I10.Command00.Data400039/256;


LLRF1.ANLG.INLK_A_MAX_THR := Local:2:I10.Command00.Data400040/256;


LLRF1.ANLG.INLK_B_RESET_PERMIT := Local:2:I10.Command00.Data400041;


LLRF1.ANLG.INLK_B_RESET_MINMAX := Local:2:I10.Command00.Data400042;


LLRF1.ANLG.INLK_B_MIN_THR := Local:2:I10.Command00.Data400043/256;


LLRF1.ANLG.INLK_B_MAX_THR := Local:2:I10.Command00.Data400044/256;


LLRF1.ANLG.UP_A_SW := Local:2:I10.Command00.Data400045;


LLRF1.ANLG.UP_B_SW := Local:2:I10.Command00.Data400046;


LLRF1.ANLG.UP_A_ATT := Local:2:I10.Command00.Data400047/2;


LLRF1.ANLG.UP_B_ATT := Local:2:I10.Command00.Data400048/2;


LLRF1.ANLG.PSU_RESET_ERR_FLAGS := Local:2:I10.Command00.Data400049;
