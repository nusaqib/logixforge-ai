
// Maps input modules to tags if not in simulation mode


if NOT System.Simulation_Mode then


 	JSR(R00_Input_Output_Mapping);


end_if;





JSR(R01_Calibration);





JSR(R02_Latch);





JSR(R03_First_Fault);





JSR(R04_PPS);





JSR(R05_Interlocks_Summations);





JSR(R06_Interlock_Logic);





JSR(R07_Local_Remote_Commands);





JSR(R08_Misc);





JSR(R09_PPS_Monitor);





JSR(R10_Module_Status);



