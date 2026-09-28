//! This routine checks the module/communication status

////////////////////////////////////////////////////////////


//   Copyright (c)  <LBNL>


//------------------------------------------------------------


//   Routine: R10_Module_Status


//   Author: LBL\NUSaqib


//   Created: 8/19/2025


//------------------------------------------------------------


//   Description:


//           This routine checks the module/communication status


////////////////////////////////////////////////////////////





Module_Status_AOI(ModuleStatusAOI[0],R01,Modules.R01.FaultCode,Modules.R01.CommunicationOK);


Module_Status_AOI(ModuleStatusAOI[1],R03,Modules.R03.FaultCode,Modules.R03.CommunicationOK);


Module_Status_AOI(ModuleStatusAOI[2],Cav1_Tuner,Modules.Cav1_Tuner.FaultCode,Modules.Cav1_Tuner.CommunicationOK);


Module_Status_AOI(ModuleStatusAOI[3],Cav2_Tuner,Modules.Cav2_Tuner.FaultCode,Modules.Cav2_Tuner.CommunicationOK);





Modules.LLRF1_DIG.CommunicationOK.Sts := NOT Local:2:I00.Fault;


Modules.LLRF1_ANLG.CommunicationOK.Sts := NOT Local:2:I10.Fault;


Modules.LLRF2_DIG.CommunicationOK.Sts := NOT R01:2:I00.Fault;


Modules.LLRF2_ANLG.CommunicationOK.Sts := NOT R01:2:I10.Fault;



