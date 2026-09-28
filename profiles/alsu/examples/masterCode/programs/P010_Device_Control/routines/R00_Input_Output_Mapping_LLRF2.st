//! This routine maps module inputs to PLC tags

/* LLRF 2 Modbus RTU */





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


/*LLRF2_Power[0].RawVal := R01:2:I00.Command00.Data400000;


LLRF2_Power[1].RawVal := R01:2:I00.Command00.Data400001;


LLRF2_Power[2].RawVal := R01:2:I00.Command00.Data400002;


LLRF2_Power[3].RawVal := R01:2:I00.Command00.Data400003;


LLRF2_Power[4].RawVal := R01:2:I00.Command00.Data400004;


LLRF2_Power[5].RawVal := R01:2:I00.Command00.Data400005;


LLRF2_Power[6].RawVal := R01:2:I00.Command00.Data400006;


LLRF2_Power[7].RawVal := R01:2:I00.Command00.Data400007;


LLRF2_Power[8].RawVal := R01:2:I00.Command00.Data400008;


LLRF2_Power[9].RawVal := R01:2:I00.Command00.Data400009;





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





LLRF2_Power[0].Sts := R01:2:I00.Command00.Data400030.0;


LLRF2_Power[1].Sts := R01:2:I00.Command00.Data400030.1;


LLRF2_Power[2].Sts := R01:2:I00.Command00.Data400030.2;


LLRF2_Power[3].Sts := R01:2:I00.Command00.Data400030.3;


LLRF2_Power[4].Sts := R01:2:I00.Command00.Data400030.4;


LLRF2_Power[5].Sts := R01:2:I00.Command00.Data400030.5;


LLRF2_Power[6].Sts := R01:2:I00.Command00.Data400030.6;


LLRF2_Power[7].Sts := R01:2:I00.Command00.Data400030.7;


LLRF2_Power[8].Sts := R01:2:I00.Command00.Data400030.8;


LLRF2_Power[9].Sts := R01:2:I00.Command00.Data400030.9;





LLRF2_Power[0].Ltch := R01:2:I00.Command00.Data400032.0;


LLRF2_Power[1].Ltch := R01:2:I00.Command00.Data400032.1;


LLRF2_Power[2].Ltch := R01:2:I00.Command00.Data400032.2;


LLRF2_Power[3].Ltch := R01:2:I00.Command00.Data400032.3;


LLRF2_Power[4].Ltch := R01:2:I00.Command00.Data400032.4;


LLRF2_Power[5].Ltch := R01:2:I00.Command00.Data400032.5;


LLRF2_Power[6].Ltch := R01:2:I00.Command00.Data400032.6;


LLRF2_Power[7].Ltch := R01:2:I00.Command00.Data400032.7;


LLRF2_Power[8].Ltch := R01:2:I00.Command00.Data400032.8;


LLRF2_Power[9].Ltch := R01:2:I00.Command00.Data400032.9;





R01:2:O00.Command01.Data400058 := LLRF2_Power[0].Intlk_Mode;


R01:2:O00.Command01.Data400059 := LLRF2_Power[1].Intlk_Mode;


R01:2:O00.Command01.Data400060 := LLRF2_Power[2].Intlk_Mode;


R01:2:O00.Command01.Data400061 := LLRF2_Power[3].Intlk_Mode;


R01:2:O00.Command01.Data400062 := LLRF2_Power[4].Intlk_Mode;


R01:2:O00.Command01.Data400063 := LLRF2_Power[5].Intlk_Mode;


R01:2:O00.Command01.Data400064 := LLRF2_Power[6].Intlk_Mode;


R01:2:O00.Command01.Data400065 := LLRF2_Power[7].Intlk_Mode;


R01:2:O00.Command01.Data400066 := LLRF2_Power[8].Intlk_Mode;


R01:2:O00.Command01.Data400067 := LLRF2_Power[9].Intlk_Mode;





R01:2:O00.Command01.Data400068.0 := LLRF2_Power[0].Byp;


R01:2:O00.Command01.Data400068.1 := LLRF2_Power[1].Byp;


R01:2:O00.Command01.Data400068.2 := LLRF2_Power[2].Byp;


R01:2:O00.Command01.Data400068.3 := LLRF2_Power[3].Byp;


R01:2:O00.Command01.Data400068.4 := LLRF2_Power[4].Byp;


R01:2:O00.Command01.Data400068.5 := LLRF2_Power[5].Byp;


R01:2:O00.Command01.Data400068.6 := LLRF2_Power[6].Byp;


R01:2:O00.Command01.Data400068.7 := LLRF2_Power[7].Byp;


R01:2:O00.Command01.Data400068.8 := LLRF2_Power[8].Byp;


R01:2:O00.Command01.Data400068.9 := LLRF2_Power[9].Byp;





R01:2:O00.Command01.Data400038 := LLRF2_Power[0].Lo_SP_Raw;


R01:2:O00.Command01.Data400039 := LLRF2_Power[1].Lo_SP_Raw;


R01:2:O00.Command01.Data400040 := LLRF2_Power[2].Lo_SP_Raw;


R01:2:O00.Command01.Data400041 := LLRF2_Power[3].Lo_SP_Raw;


R01:2:O00.Command01.Data400042 := LLRF2_Power[4].Lo_SP_Raw;


R01:2:O00.Command01.Data400043 := LLRF2_Power[5].Lo_SP_Raw;


R01:2:O00.Command01.Data400044 := LLRF2_Power[6].Lo_SP_Raw;


R01:2:O00.Command01.Data400045 := LLRF2_Power[7].Lo_SP_Raw;


R01:2:O00.Command01.Data400046 := LLRF2_Power[8].Lo_SP_Raw;


R01:2:O00.Command01.Data400047 := LLRF2_Power[9].Lo_SP_Raw;





R01:2:O00.Command01.Data400048 := LLRF2_Power[0].Hi_SP_Raw;


R01:2:O00.Command01.Data400049 := LLRF2_Power[1].Hi_SP_Raw;


R01:2:O00.Command01.Data400050 := LLRF2_Power[2].Hi_SP_Raw;


R01:2:O00.Command01.Data400051 := LLRF2_Power[3].Hi_SP_Raw;


R01:2:O00.Command01.Data400052 := LLRF2_Power[4].Hi_SP_Raw;


R01:2:O00.Command01.Data400053 := LLRF2_Power[5].Hi_SP_Raw;


R01:2:O00.Command01.Data400054 := LLRF2_Power[6].Hi_SP_Raw;


R01:2:O00.Command01.Data400055 := LLRF2_Power[7].Hi_SP_Raw;


R01:2:O00.Command01.Data400056 := LLRF2_Power[8].Hi_SP_Raw;


R01:2:O00.Command01.Data400057 := LLRF2_Power[9].Hi_SP_Raw;





LLRF2.DIG.Uptime := R01:2:I00.Command02.Data400090;


LLRF2.DIG.Temp := R01:2:I00.Command02.Data400091;


LLRF2.DIG.VCCINT := R01:2:I00.Command02.Data400092;


LLRF2.DIG.VCCAUX := R01:2:I00.Command02.Data400093;


LLRF2.DIG.VCCBRAM := R01:2:I00.Command02.Data400094;





//Arc Detectors


LLRF2_Arc_Detector[0].Sts := R01:2:I00.Command00.Data400036.0;


LLRF2_Arc_Detector[1].Sts := R01:2:I00.Command00.Data400036.1;


LLRF2_Arc_Detector[2].Sts := R01:2:I00.Command00.Data400036.2;





LLRF2_Arc_Detector[0].Ltch := R01:2:I00.Command00.Data400035.0;


LLRF2_Arc_Detector[1].Ltch := R01:2:I00.Command00.Data400035.1;


LLRF2_Arc_Detector[2].Ltch := R01:2:I00.Command00.Data400035.2;





R01:2:O00.Command01.Data400086.0 := LLRF2_Arc_Detector[0].Byp;


R01:2:O00.Command01.Data400086.1 := LLRF2_Arc_Detector[1].Byp;


R01:2:O00.Command01.Data400086.2 := LLRF2_Arc_Detector[2].Byp;





R01:2:O00.Command01.Data400089.0 := LLRF2_Arc_Detector[0].Test;


R01:2:O00.Command01.Data400089.1 := LLRF2_Arc_Detector[1].Test;


R01:2:O00.Command01.Data400089.2 := LLRF2_Arc_Detector[2].Test;





R01:2:O00.Command01.Data400087.0 := LLRF2_Arc_Detector[0].Rst;


R01:2:O00.Command01.Data400087.1 := LLRF2_Arc_Detector[1].Rst;


R01:2:O00.Command01.Data400087.2 := LLRF2_Arc_Detector[2].Rst;





LLRF2.DIG.RF_Power_Sum := R01:2:I00.Command00.Data400031;


LLRF2.DIG.Arc_Sum := R01:2:I00.Command00.Data400037;


R01:2:O00.Command01.Data400069 := LLRF2.DIG.Rst_Power;


//Local:1:O00.Command01.Data400088 := LLRF2.DIG.Arc_Sum;*/





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






