
// When the editing mode is changed on the HMI, load the previous configuration values of that mode once


if RF_Power_Editing_Mode <> RF_Power_Editing_Mode_Prev then


	for Channel_Power := 0 to 9 do


	LLRF1_Power[Channel_Power].Lo_SP_HMI := LLRF1_Power_Lo_SP[RF_Power_Editing_Mode, Channel_Power];


	LLRF1_Power[Channel_Power].Hi_SP_HMI := LLRF1_Power_Hi_SP[RF_Power_Editing_Mode, Channel_Power];


	LLRF1_Power[Channel_Power].Intlk_Mode_HMI := LLRF1_Power_Intlk_Mode[RF_Power_Editing_Mode, Channel_Power];


	LLRF1_Power[Channel_Power].Byp_HMI := LLRF1_Power_Byp[RF_Power_Editing_Mode, Channel_Power].0;


	end_for;


	


	for Channel_Power := 0 to 9 do


	LLRF2_Power[Channel_Power].Lo_SP_HMI := LLRF2_Power_Lo_SP[RF_Power_Editing_Mode, Channel_Power];


	LLRF2_Power[Channel_Power].Hi_SP_HMI := LLRF2_Power_Hi_SP[RF_Power_Editing_Mode, Channel_Power];


	LLRF2_Power[Channel_Power].Intlk_Mode_HMI := LLRF2_Power_Intlk_Mode[RF_Power_Editing_Mode, Channel_Power];


	LLRF2_Power[Channel_Power].Byp_HMI := LLRF2_Power_Byp[RF_Power_Editing_Mode, Channel_Power].0;


	end_for;


	


	for Channel_Arc := 0 to 2 do


	LLRF1_Arc_Detector[Channel_Arc].Byp_Cmd_HMI := LLRF1_Arc_Detector[Channel_Arc].Byp_Modes[RF_Power_Editing_Mode];


	end_for;


	


	for Channel_Arc := 0 to 2 do


	LLRF2_Arc_Detector[Channel_Arc].Byp_Cmd_HMI := LLRF2_Arc_Detector[Channel_Arc].Byp_Modes[RF_Power_Editing_Mode];


	end_for;





// Make the previous mode to the present mode after one cycle


	RF_Power_Editing_Mode_Prev := RF_Power_Editing_Mode;





// Store operator HMI configuration changes to the corresponding mode arrays


else


	for Channel_Power := 0 to 9 do


	LLRF1_Power_Lo_SP[RF_Power_Editing_Mode, Channel_Power] := LLRF1_Power[Channel_Power].Lo_SP_HMI;


	LLRF1_Power_Hi_SP[RF_Power_Editing_Mode, Channel_Power] := LLRF1_Power[Channel_Power].Hi_SP_HMI;


	LLRF1_Power_Intlk_Mode[RF_Power_Editing_Mode, Channel_Power] := LLRF1_Power[Channel_Power].Intlk_Mode_HMI;


	LLRF1_Power_Byp[RF_Power_Editing_Mode, Channel_Power].0 := LLRF1_Power[Channel_Power].Byp_HMI;


	end_for;


	


	for Channel_Power := 0 to 9 do


	LLRF2_Power_Lo_SP[RF_Power_Editing_Mode, Channel_Power] := LLRF2_Power[Channel_Power].Lo_SP_HMI;


	LLRF2_Power_Hi_SP[RF_Power_Editing_Mode, Channel_Power] := LLRF2_Power[Channel_Power].Hi_SP_HMI;


	LLRF2_Power_Intlk_Mode[RF_Power_Editing_Mode, Channel_Power] := LLRF2_Power[Channel_Power].Intlk_Mode_HMI;


	LLRF2_Power_Byp[RF_Power_Editing_Mode, Channel_Power].0 := LLRF2_Power[Channel_Power].Byp_HMI;


	end_for;


	


	for Channel_Arc := 0 to 2 do


	LLRF1_Arc_Detector[Channel_Arc].Byp_Modes[RF_Power_Editing_Mode] := LLRF1_Arc_Detector[Channel_Arc].Byp_Cmd_HMI;


	end_for;


	


	for Channel_Arc := 0 to 2 do


	LLRF2_Arc_Detector[Channel_Arc].Byp_Modes[RF_Power_Editing_Mode] := LLRF2_Arc_Detector[Channel_Arc].Byp_Cmd_HMI;


	end_for;


	


end_if;





// Send corresponding mode configuration values to the LLRF


if PPS.Op_Mode.Sts OR PPS.RF_Test_Mode.Sts OR PPS.RF_TestwAc_Mode.Sts then


	ModeIdx := 0;


elsif PPS.RF_TestLd_Mode.Sts then


		ModeIdx := 1;


end_if;





for Channel_Arc := 0 to 2 do


	LLRF1_Arc_Detector[Channel_Arc].Byp := LLRF1_Arc_Detector[Channel_Arc].Byp_Modes[ModeIdx];


end_for;





for Channel_Arc := 0 to 2 do


	LLRF2_Arc_Detector[Channel_Arc].Byp := LLRF2_Arc_Detector[Channel_Arc].Byp_Modes[ModeIdx];


end_for;





for Channel_Power := 0 to 9 do


	Count_to_kW_AOI(Count_to_kW_1[Channel_Power], LLRF1_Power[Channel_Power]);


	kW_to_Count_AOI(kW_to_Count_1[Channel_Power], LLRF1_Power[Channel_Power]);


	LLRF1_Power[Channel_Power].Hi_SP := LLRF1_Power_Hi_SP[ModeIdx, Channel_Power];


	LLRF1_Power[Channel_Power].Lo_SP := LLRF1_Power_Lo_SP[ModeIdx, Channel_Power];


	LLRF1_Power[Channel_Power].Intlk_Mode := LLRF1_Power_Intlk_Mode[ModeIdx, Channel_Power];


	LLRF1_Power[Channel_Power].Byp := LLRF1_Power_Byp[ModeIdx, Channel_Power].0;


end_for;





for Channel_Power := 0 to 9 do


	Count_to_kW_AOI(Count_to_kW_2[Channel_Power], LLRF2_Power[Channel_Power]);


	kW_to_Count_AOI(kW_to_Count_2[Channel_Power], LLRF2_Power[Channel_Power]);


	LLRF2_Power[Channel_Power].Hi_SP := LLRF2_Power_Hi_SP[ModeIdx, Channel_Power];


	LLRF2_Power[Channel_Power].Lo_SP := LLRF2_Power_Lo_SP[ModeIdx, Channel_Power];


	LLRF2_Power[Channel_Power].Intlk_Mode := LLRF2_Power_Intlk_Mode[ModeIdx, Channel_Power];


	LLRF2_Power[Channel_Power].Byp := LLRF2_Power_Byp[ModeIdx, Channel_Power].0;


end_for;
