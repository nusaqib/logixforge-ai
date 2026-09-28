
if NOT System.Simulation_Mode then


 	JSR(R00_Input_Output_Mapping_LLRF1_New);


	JSR(R00_Input_Output_Mapping_LLRF2_New);


end_if;





JSR(R01_RF_Power_Arcs);





JSR(R02_HP_Cx_Sw);





// Tuner position/resonance control


JSR(R04_Tuner1_Control);





JSR(R05_Tuner2_Control);



