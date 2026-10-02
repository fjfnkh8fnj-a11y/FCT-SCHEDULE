from pathlib import Path

src = Path('index.html').read_text(encoding='utf-8')
s = src

# Separate test identity only; production index is never modified.
s = s.replace('<title>FCT 화인세라텍 | 통합 일정</title>', '<title>FCT 화인세라텍 | 통합 일정 · 연동등록 TEST</title>', 1)
s = s.replace("const APP_VERSION='rev.38';", "const APP_VERSION='INTEGRATED TEST rev.1';", 1)
s = s.replace('id="appRevision">rev.38</span>', 'id="appRevision">TEST rev.1</span>', 1)

# Test-only styles.
style_needle = '</style>'
style_add = r'''
.test-banner{margin:0 0 18px;padding:13px 16px;border:1px solid #f0c36b;background:#fff8e8;border-radius:11px;color:#725218;font-size:13px;line-height:1.55}
.test-banner strong{color:#9a5d00}.link-schedule-box{margin:14px 0 4px;border:1px solid #bfd2e5;background:#f4f9ff;border-radius:10px;padding:14px}
.link-schedule-title{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:9px;font-weight:800;color:#173965}.link-schedule-title small{font-size:11px;color:#1766b1;background:#e7f2ff;padding:3px 7px;border-radius:12px}
.link-schedule-options{display:flex;gap:18px;flex-wrap:wrap}.link-schedule-options label{display:inline-flex;align-items:center;gap:7px;font-size:13px;font-weight:700;color:#36516f}.link-schedule-options input{width:auto!important;margin:0!important}
.link-schedule-help{margin:9px 0 0!important;font-size:12px!important;color:#637187!important}
@media(max-width:600px){.link-schedule-options{display:grid;gap:9px}.test-banner{font-size:12px}}
'''
assert style_needle in s
s = s.replace(style_needle, style_add + '\n' + style_needle, 1)

# Visible warning at top.
main_needle = '<main class="main">\n'
banner = '''<main class="main">\n    <div class="test-banner"><strong>연동등록 TEST</strong> · 운영본 rev.38은 변경하지 않습니다. 운영 데이터를 읽어 화면에 보여주지만, 이 TEST 페이지에서 등록·수정·삭제한 내용은 <strong>서버에 저장되지 않으며 새로고침하면 원복</strong>됩니다.</div>\n'''
assert main_needle in s
s = s.replace(main_needle, banner, 1)

# Visit form: one application, multiple calendar views.
visit_needle = '    <label class="vendor-master-option"><input type="checkbox" id="updateVendorMaster" name="updateMaster"> 수정한 대표자·연락처를 업체 기본정보에도 반영</label>'
visit_link = '''    <div class="link-schedule-box">
      <div class="link-schedule-title"><span>일정 연동</span><small>한 번만 등록</small></div>
      <div class="link-schedule-options">
        <label><input type="checkbox" name="showOverall" checked> 전체 일정에 표시</label>
        <label><input type="checkbox" name="showDept" checked> 담당부서 일정에 표시</label>
      </div>
      <p class="link-schedule-help">별도 「일정 등록」을 다시 하지 않습니다. 이 방문신청 1건의 날짜·담당부서·신청사유를 그대로 일정 화면에서 함께 사용합니다.</p>
    </div>
''' + visit_needle
assert visit_needle in s
s = s.replace(visit_needle, visit_link, 1)

# Utility form: same integrated calendar display choice.
utility_needle = '    <div class="actions"><button class="danger" type="button" id="utilityDelete" hidden>삭제</button><span style="flex:1"></span><button class="secondary" type="button" id="utilityCancel">취소</button><button class="primary" id="utilitySubmit">등록</button></div>'
utility_link = '''    <div class="link-schedule-box">
      <div class="link-schedule-title"><span>일정 연동</span><small>한 번만 등록</small></div>
      <div class="link-schedule-options">
        <label><input type="checkbox" name="showOverall" checked> 전체 일정에 표시</label>
        <label><input type="checkbox" name="showDept" checked> 담당부서 일정에 표시</label>
      </div>
      <p class="link-schedule-help">별도 「일정 등록」 없이 이 작업신청의 예정일·담당부서·작업내용을 일정 화면에 그대로 연결합니다.</p>
    </div>
''' + utility_needle
assert utility_needle in s
s = s.replace(utility_needle, utility_link, 1)

# Respect the view selections when rendering visit/utility records.
visit_filter_old = "      if(view!=='전체 일정'&&dept!==view)continue;\n      out.push({id:v.id,kind:'visit'"
visit_filter_new = "      let displayTargets=v.displayTargets||{};\n      if(view==='전체 일정'&&displayTargets.overall===false)continue;\n      if(depts.includes(view)&&(displayTargets.dept===false||dept!==view))continue;\n      out.push({id:v.id,kind:'visit'"
assert visit_filter_old in s
s = s.replace(visit_filter_old, visit_filter_new, 1)

utility_filter_old = "      if(valid(w.workDate)&&w.workDate>=start&&w.workDate<=end&&(view==='전체 일정'||dept===view)){\n        out.push({id:w.id,kind:'utility'"
utility_filter_new = "      let displayTargets=w.displayTargets||{};\n      let visibleInView=view==='전체 일정'?displayTargets.overall!==false:(depts.includes(view)&&displayTargets.dept!==false&&dept===view);\n      if(valid(w.workDate)&&w.workDate>=start&&w.workDate<=end&&visibleInView){\n        out.push({id:w.id,kind:'utility'"
assert utility_filter_old in s
s = s.replace(utility_filter_old, utility_filter_new, 1)

# Populate linked-view options while editing existing items; legacy records default to both views ON.
visit_edit_needle = "    f.elements.reason.value=v.reason||'';\n    document.querySelectorAll('#visitZones input[name=\"zones\"]').forEach(cb=>cb.checked=(v.zones||[]).includes(cb.value));"
visit_edit_new = "    f.elements.reason.value=v.reason||'';\n    f.elements.showOverall.checked=v.displayTargets?.overall!==false;f.elements.showDept.checked=v.displayTargets?.dept!==false;\n    document.querySelectorAll('#visitZones input[name=\"zones\"]').forEach(cb=>cb.checked=(v.zones||[]).includes(cb.value));"
assert visit_edit_needle in s
s = s.replace(visit_edit_needle, visit_edit_new, 1)

utility_edit_needle = "    f.elements.note.value=w.note||'';\n    document.querySelectorAll('#utilityTargets input[name=\"targets\"]').forEach(cb=>cb.checked=(w.targets||[]).includes(cb.value));"
utility_edit_new = "    f.elements.note.value=w.note||'';\n    f.elements.showOverall.checked=w.displayTargets?.overall!==false;f.elements.showDept.checked=w.displayTargets?.dept!==false;\n    document.querySelectorAll('#utilityTargets input[name=\"targets\"]').forEach(cb=>cb.checked=(w.targets||[]).includes(cb.value));"
assert utility_edit_needle in s
s = s.replace(utility_edit_needle, utility_edit_new, 1)

# Save the options into the single visit/utility object (test memory only).
visit_item_old = "let item={id:editingVisitId||newId(),vendorId:master.id,company,startDate,endDate,startTime,endTime,headcount,representative,phone,dept,manager,badgeStatus:String(f.get('badgeStatus')||'미지급'),zones,reason,createdAt:old?.createdAt||new Date().toISOString(),updatedAt:new Date().toISOString()};"
visit_item_new = "let item={id:editingVisitId||newId(),vendorId:master.id,company,startDate,endDate,startTime,endTime,headcount,representative,phone,dept,manager,badgeStatus:String(f.get('badgeStatus')||'미지급'),zones,reason,displayTargets:{overall:f.get('showOverall')==='on',dept:f.get('showDept')==='on'},createdAt:old?.createdAt||new Date().toISOString(),updatedAt:new Date().toISOString()};"
assert visit_item_old in s
s = s.replace(visit_item_old, visit_item_new, 1)

utility_item_old = "let item={id:editingUtilityId||newId(),workName,targets,workDate,startTime,endTime,workContent,location,dept,manager,company,shutdown,departments,note,createdAt:old?.createdAt||new Date().toISOString(),updatedAt:new Date().toISOString()};"
utility_item_new = "let item={id:editingUtilityId||newId(),workName,targets,workDate,startTime,endTime,workContent,location,dept,manager,company,shutdown,departments,note,displayTargets:{overall:f.get('showOverall')==='on',dept:f.get('showDept')==='on'},createdAt:old?.createdAt||new Date().toISOString(),updatedAt:new Date().toISOString()};"
assert utility_item_old in s
s = s.replace(utility_item_old, utility_item_new, 1)

# Make every change local-only. Loading still reads the current production data through the normal PIN flow.
init_needle = "setAdminMode(false);setupForms();setupEventDetail();setupVisits();setupUtilities();setupBulkDelete();setupQr();setupExcel();setupHome();setupLock();setTimeout(()=>$('#lockPin').focus(),0);"
local_save = r'''async function saveCloud(){
  if(!adminUnlocked||!adminPin||!cloudReady)return;
  clearTimeout(saveTimer);saveInFlight=false;savePending=false;
  syncedState=cloneState(localState());
  setCloud('TEST · 서버 저장 안 함','ok');
}
''' + init_needle
assert init_needle in s
s = s.replace(init_needle, local_save, 1)

# Test status should be obvious immediately after loading.
s = s.replace("setCloud('개별 저장 연결됨','ok');render();", "setCloud('TEST · 운영데이터 읽기전용','ok');render();", 1)

# Sanity checks.
checks = [
    '연동등록 TEST',
    'name="showOverall" checked',
    'name="showDept" checked',
    "displayTargets:{overall:f.get('showOverall')==='on',dept:f.get('showDept')==='on'}",
    "setCloud('TEST · 서버 저장 안 함','ok')",
    "const APP_VERSION='INTEGRATED TEST rev.1';",
]
for c in checks:
    assert c in s, c
assert s != src

Path('FCT-SCHEDULE_INTEGRATED-ENTRY_TEST_rev.1.html').write_text(s, encoding='utf-8')
print('built', len(s))
