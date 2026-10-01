from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

assert 'rev.37' in s, 'Expected rev.37 source'
assert 'id="usageGuide"' in s, 'Usage guide missing'
assert "function nav(){let views=['전체 일정','연간일정','출입·작업관리',...depts]" in s, 'Nav target missing'
assert "function render(){nav();configurePrimaryAction();if(view==='출입·작업관리')" in s, 'Render target missing'

# Version bump, including visible guide version and Excel filenames.
s = s.replace('rev.37', 'rev.38')

# Move the guide from the bottom of every screen to the main content area, just before the footer.
guide_start = s.index('    <section class="usage-guide card" id="usageGuide"')
main_end = s.index('\n\n  </main>', guide_start)
guide_block = s[guide_start:main_end]
assert guide_block.count('id="usageGuide"') == 1
s = s[:guide_start] + s[main_end:]
guide_block = guide_block.replace('id="usageGuide" aria-labelledby=', 'id="usageGuide" hidden aria-labelledby=', 1)
footer_marker = '    <footer class="utilitybar">'
assert footer_marker in s
s = s.replace(footer_marker, guide_block + '\n\n' + footer_marker, 1)

# Add a dedicated usage tab after the department tabs.
s = s.replace(
    "function nav(){let views=['전체 일정','연간일정','출입·작업관리',...depts];",
    "function nav(){let views=['전체 일정','연간일정','출입·작업관리',...depts,'사용방법'];",
    1
)

# Render the guide only when the Usage tab is selected.
old_render = "function render(){nav();configurePrimaryAction();if(view==='출입·작업관리'){renderManagementView();return}"
new_render = "function render(){nav();configurePrimaryAction();let guide=$('#usageGuide'),content=$('#content'),topcontrols=document.querySelector('.topcontrols');if(guide)guide.hidden=view!=='사용방법';if(content)content.hidden=view==='사용방법';if(view==='사용방법'){if(topcontrols)topcontrols.hidden=true;$('#title').textContent='사용방법';$('#subtitle').textContent='FCT 일정관리 전체 기능 사용 안내';return}else if(topcontrols)topcontrols.hidden=false;if(view==='출입·작업관리'){renderManagementView();return}"
assert old_render in s
s = s.replace(old_render, new_render, 1)

# Ensure the logo/home action returns to the normal calendar view and hides the guide via render().
assert "view='전체 일정';date=new Date(today.getFullYear(),today.getMonth(),1);render();" in s

# Static validation.
assert "...depts,'사용방법'" in s
assert "guide.hidden=view!=='사용방법'" in s
assert "content.hidden=view==='사용방법'" in s
assert "topcontrols.hidden=true" in s
assert 'id="usageGuide" hidden' in s
assert 'rev.38 기준' in s
assert 'rev.37' not in s
assert s.index('id="usageGuide" hidden') < s.index('<footer class="utilitybar">')

p.write_text(s, encoding='utf-8')
Path('FCT_통합일정_rev.38.html').write_text(s, encoding='utf-8')

# Extract inline app script for node --check in CI.
start = s.index("<script>\n(()=>{") + len('<script>\n')
end = s.index('\n</script>', start)
Path('/tmp/fct_schedule_rev38.js').write_text(s[start:end], encoding='utf-8')
