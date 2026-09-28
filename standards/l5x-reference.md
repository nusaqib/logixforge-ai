# L5X reference (what LogixForge emits)

L5X is the XML export of a Logix 5000 project (`RSLogix5000Content` root). Studio 5000 uses it for
full project exchange and for partial import/export of components.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="33.00" TargetName="X" TargetType="Controller"
                    ContainsContext="false" Owner="..." ExportDate="..." ExportOptions="...">
  <Controller Use="Target" Name="X" ProcessorType="1756-L83E" MajorRev="33" MinorRev="11" ...>
    <Description><![CDATA[...]]></Description>
    <RedundancyInfo .../> <Security .../> <SafetyInfo/>
    <DataTypes>      <DataType Name="UDT_x" Family="NoFamily" Class="User"><Members><Member .../></Members></DataType>
    <Modules>        <Module Name="Local" CatalogNumber=... ><EKey/><Ports>...</Ports></Module> ... (I/O modules from Studio export)
    <AddOnInstructionDefinitions> <AddOnInstructionDefinition Name="AOI_x" Revision="1.0" ...>
                        <Parameters><Parameter Name="EnableIn" .../>...</Parameters><LocalTags/><Routines><Routine Name="Logic" Type="RLL"/></Routines>
    <Tags>           <Tag Name="t" TagType="Base|Alias|Produced|Consumed" DataType="DINT" Dimensions="10" Radix="Decimal"
                          Constant="false" ExternalAccess="Read/Write" AliasFor="Local:2:I.Data.0">
                        <Description/> <Data Format="L5K"><![CDATA[0]]></Data> [<Data Format="Decorated">...] </Tag>
    <Programs>       <Program Name="P" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" UseAsFolder="false">
                        <Tags/> <Routines><Routine Name="R" Type="RLL"><RLLContent><Rung Number="0" Type="N">
                        <Comment><![CDATA[...]]></Comment><Text><![CDATA[XIC(A)OTE(B);]]></Text></Rung></RLLContent></Routine>
                        <Routine Name="S" Type="ST"><STContent><Line Number="0"><![CDATA[x := 1;]]></Line></STContent></Routine>
    <Tasks>          <Task Name="MainTask" Type="CONTINUOUS|PERIODIC|EVENT" Rate="10" Priority="10" Watchdog="500"
                          DisableUpdateOutputs="false" InhibitTask="false"><ScheduledPrograms><ScheduledProgram Name="P"/></ScheduledPrograms></Task>
  </Controller>
</RSLogix5000Content>
```

## Partial import files
`TargetType` = `Routine | Program | Tag | DataType | AddOnInstructionDefinition | Module | Rung`,
`ContainsContext="true"`. Enclosing elements carry `Use="Context"`, the imported element `Use="Target"`.
Example: routine import = `Controller[Context] > Programs > Program[Context] > Routines > Routine[Target]`.
Additional `Use="Context"` tags/UDTs may be included so Studio can resolve references; Studio
creates missing tags as needed and shows them in the import dialog.

## Data formats
- `L5K`: text initial values. Atomic `0`, `1.5`; structure `[m1,m2,[nested]]`; array `[a,b,c]`;
  string `'text'` with `$` escapes; BOOL `0/1`. Omitting `<Data>` initialises to zero.
- `Decorated`: verbose XML per member (`<DataValue>`, `<Structure>`, `<Array>`); optional on import.
- Radix: Decimal, Hex, Binary, Octal, ASCII, Float, Exponential, Date/Time. Structured tags (TIMER, UDT, AOI)
  must have **no** Radix attribute; Studio rejects `NullType` on import ("Invalid display style").

## Rung text (neutral text)
Same grammar as Studio's rung editor. `Type="N"` normal rung; `Type="I"`/`"D"` insert/delete
pending edits (online edits export). Rung `Comment` is CDATA, multi-line allowed.

## Things that break import
- Undefined tags in AOI logic; parameter/local name collisions.
- Wrong element order inside `<Controller>` (DataTypes before Tags before Programs before Tasks).
- Alias to non-existent module tag. Module elements missing Communications/Connections.
- A `<Module Name="Local">` for the controller itself (collides with the one Studio creates).
- `ShareUnusedTimeSlice`, `IOMemoryPadPercentage`, `DataTablePadPercentage` on L8x/5069 controllers.
- Descriptions over 128 characters.
- `SoftwareRevision` newer than the installed Studio 5000.
- BOOL arrays not multiple of 32; UDT with AOI member; program scheduled in two tasks.
- Names > 40 chars or reserved words.
