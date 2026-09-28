# Instruction reference (rung-text operand order)

Format `MNEMONIC(operands)`; `?` = let Studio fill. See Rockwell 1756-RM003 for semantics.

## Bit
`XIC(bit)` `XIO(bit)` `OTE(bit)` `OTL(bit)` `OTU(bit)` `ONS(storage_bit)` `OSR(storage,output)` `OSF(storage,output)`

## Timer / counter (ladder)
`TON(timer,?,?)` `TOF(timer,?,?)` `RTO(timer,?,?)` `CTU(counter,?,?)` `CTD(counter,?,?)` `RES(timer|counter)`
Members: `.PRE .ACC .EN .TT .DN` (timer), `.PRE .ACC .CU .CD .DN .OV .UN` (counter). Preset in ms.
ST/FBD versions: `TONR(FBD_TIMER)` `TOFR` `RTOR` `CTUD(FBD_COUNTER)` with `.TimerEnable .Reset .PRE .ACC .DN`.

## Compare
`EQU(a,b)` `NEQ(a,b)` `LES(a,b)` `LEQ(a,b)` `GRT(a,b)` `GEQ(a,b)` `LIM(low,test,high)` `MEQ(source,mask,compare)` `CMP(expression)`

## Math / move
`ADD(a,b,dest)` `SUB` `MUL` `DIV` `MOD` `NEG(src,dest)` `ABS` `SQR` `SQRT` `XPY(a,b,dest)` `CPT(dest,expression)`
`MOV(src,dest)` `MVM(src,mask,dest)` `CLR(dest)` `AND(a,b,dest)` `OR` `XOR` `NOT(src,dest)` `BTD(src,src_bit,dest,dest_bit,len)`
`TRN(src,dest)` `TRUNC` `DEG` `RAD` `SIN` `COS` `TAN` `ASN` `ACS` `ATN` `LN` `LOG`

## Array / file
`COP(src,dest,len)` `CPS(src,dest,len)` `FLL(src,dest,len)` `SIZE(array,dim,dest)`
`FAL(control,len,pos,mode,dest,expr)` `FSC(control,len,pos,mode,expr)` `AVE(array,dest,control,len,pos)`
`SRT(array,control,len,pos)` `STD(array,dest,control,len,pos)` `BSL(array,control,bit,len)` `BSR` `FFL(src,fifo,control,len,pos)` `FFU(fifo,dest,control,len,pos)` `LFL` `LFU`
`SQI(array,mask,src,control,len,pos)` `SQO(array,mask,dest,control,len,pos)` `SQL(array,src,control,len,pos)`

## Program control
`JSR(routine,input_count[,in...,ret...])` `SBR(...)` `RET(...)` `JMP(label)` `LBL(label)` `FOR(routine,index,init,final,step)` `BRK()` `TND()` `MCR()` `UID()` `UIE()` `AFI()` `NOP()` `EVENT(task)` `SFR(sfc,step)` `SFP(sfc,state)`

## System / comms / IO
`GSV(class,instance,attribute,dest)` `SSV(class,instance,attribute,src)` `MSG(message)` `IOT(output_tag)`
Common GSV: `GSV(Task,THIS,MaxScanTime,x)` `GSV(Controller,THIS,...)` `GSV(Module,ModName,EntryStatus,x)` `GSV(Program,THIS,MajorFaultRecord,rec)` `GSV(WallClockTime,,DateTime,arr)`

## Process / alarm
`PID(pid,pv,tieback,cv,master,inhold,invalue)` `PIDE(loop)` `ALMD(alm,in,ack,reset,...)` `ALMA(alm,in,...)`

## String
`CONCAT(a,b,dest)` `MID(src,qty,start,dest)` `FIND(src,search,start,pos)` `INSERT(a,b,start,dest)` `DELETE(src,qty,start,dest)`
`DTOS(src,dest)` `STOD(src,dest)` `RTOS` `STOR` `UPPER(src,dest)` `LOWER(src,dest)`

## AOI call
`AOI_Name(instance, required_params_in_definition_order...)`; InOut parameters are always required.

## Status flags
`S:FS` first scan, `S:MINOR` minor fault. No arithmetic status bits; use `CMP`/`LIM`.
