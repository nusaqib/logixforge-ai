
GSV(Module, ModuleTag, FaultCode, FaultCode);





case FaultCode of


	515,516:


		CommunicationOK.Sts := 0;


	else


		CommunicationOK.Sts [:=] 1;		


end_case;
