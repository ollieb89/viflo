<!-- Phase {N} - Plan {M} -->
<plan phase="{N}" plan="{M}">
  <overview>
    <phase_name>{Phase Name}</phase_name>
    <plan_focus>{Specific focus of this plan}</plan_focus>
    <goal>{What completing this plan achieves}</goal>
  </overview>
  
  <dependencies>
    <complete>{Completed dependency}</complete>
    <pending>{Pending dependency}</pending>
  </dependencies>
  
  <context>
    <!-- Key decisions from discuss-phase -->
    <decision>{Decision 1}</decision>
    <decision>{Decision 2}</decision>
  </context>
  
  <tasks>
    <task type="auto" priority="1">
      <name>{Task name}</name>
      <files>{files to modify}</files>
      <action>
{Specific instructions for implementation}
      </action>
      <verify>{How to verify this task}</verify>
      <done>{Completion criteria}</done>
    </task>
    
    <task type="manual" priority="1">
      <name>{Manual task name}</name>
      <action>
{What the user needs to do}
      </action>
      <verify>{How to verify completion}</verify>
    </task>
  </tasks>
  
  <verification>
    <check>{Verification item 1}</check>
    <check>{Verification item 2}</check>
  </verification>
</plan>
