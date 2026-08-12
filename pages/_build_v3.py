# -*- coding: utf-8 -*-
import io, os, re

BASE = "E:/CloudStation_T14p/Projects-Agent/iproduct2.0_prototype/iproduct-playbook2/pages"

# small SVG helpers
EYE = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'
ZAP = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
CHK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
DOC = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>'
LINK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>'
EXT = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>'
AVATAR = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-brand-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>'
CHEVRON = '<svg class="agent-chev" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'
STOP = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>'
SPIN = '<span class="spinner-dot"></span>'

NEW_CSS = '''    <style id="agent-components">
      /* ===== Agent run/done — v3.5 WorkBuddy-style streaming turn (concise) ===== */
      #upload-thread { gap: var(--space-6); padding-top: var(--space-8); }

      /* ---- User turn (right-aligned bubble) ---- */
      .user-turn { display: flex; flex-direction: column; align-items: flex-end; gap: var(--space-2); }
      .user-turn-meta { display: flex; align-items: center; gap: var(--space-2); padding-right: var(--space-1);
        font-size: var(--font-size-xs); color: var(--color-text-tertiary); font-family: var(--font-sans); }
      .user-turn-meta .me { color: var(--color-text-secondary); font-weight: var(--font-weight-medium); }
      .user-bubble { max-width: 88%; background: var(--color-bg-tertiary); border: 1px solid var(--color-border-subtle);
        border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4); box-shadow: var(--shadow-sm);
        display: flex; flex-direction: column; gap: var(--space-2); }
      .user-bubble-files { display: flex; flex-wrap: wrap; gap: var(--space-2); }
      .user-bubble-text { font-size: var(--font-size-md); color: var(--color-text-primary); font-family: var(--font-sans);
        line-height: var(--line-height-relaxed); white-space: pre-wrap; }

      /* ---- Agent turn: avatar + name + status/time + chevron (no rail) ---- */
      .agent-turn { margin-bottom: var(--space-5); }
      .agent-head { position: relative; padding-left: 36px; min-height: 28px; display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2); }
      .agent-avatar { position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; border-radius: 50%;
        background: var(--color-brand-primary-muted); color: var(--color-brand-primary); display: flex; align-items: center; justify-content: center; }
      .agent-name { font-size: var(--font-size-sm); font-weight: var(--font-weight-semibold); color: var(--color-text-primary); font-family: var(--font-sans); }
      .agent-status { display: inline-flex; align-items: center; gap: 6px; font-size: var(--font-size-xs); font-family: var(--font-sans);
        padding: 2px 8px; border-radius: var(--radius-full); }
      .agent-status.running { color: var(--color-brand-primary); background: var(--color-brand-primary-soft); }
      .agent-status.done { color: var(--state-success); background: var(--state-success-muted); }
      .agent-time { font-size: var(--font-size-xs); color: var(--color-text-tertiary); font-family: var(--font-sans); }
      .agent-chev { margin-left: auto; color: var(--color-text-tertiary); transition: transform 0.2s var(--ease-smooth); flex-shrink: 0; }
      .agent-body { padding-left: 36px; }

      /* ---- Process fold (details/summary) ---- */
      .process-details { border: none; background: transparent; }
      .process-details > summary { list-style: none; cursor: pointer; }
      .process-details > summary::-webkit-details-marker { display: none; }
      .process-details[open] > summary .agent-chev { transform: rotate(90deg); }

      /* spinner */
      .spinner-dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--color-brand-primary);
        border-top-color: transparent; animation: agent-spin 0.7s linear infinite; flex-shrink: 0; }
      @keyframes agent-spin { to { transform: rotate(360deg); } }

      /* ---- Process log: think -> execute -> check stream ---- */
      .process-log { display: flex; flex-direction: column; gap: var(--space-2); }
      .log-entry { display: flex; gap: var(--space-3); align-items: flex-start; }
      /* watermark-style icon: no background, no container, single muted tone (Linear thin / monochrome) */
      .log-entry-ic { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; color: var(--color-text-tertiary); opacity: 0.6; }
      .log-entry-main { flex: 1; min-width: 0; }
      .log-entry-label { font-size: var(--font-size-xs); font-weight: var(--font-weight-semibold); color: var(--color-text-tertiary); font-family: var(--font-sans); text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 2px; }
      .log-entry-text { font-size: var(--font-size-sm); color: var(--color-text-primary); font-family: var(--font-sans); line-height: var(--line-height-normal); }
      .log-entry-meta { display: flex; align-items: center; gap: var(--space-2); margin-top: var(--space-1); font-size: var(--font-size-xs); color: var(--color-text-tertiary); font-family: var(--font-sans); }
      /* running (active) and done share the same style; only active carries a neutral running cue */
      .log-entry.pending { opacity: 0.4; }
      .process-hint { font-size: var(--font-size-xs); color: var(--color-text-tertiary); font-family: var(--font-sans); margin-top: var(--space-2); display: flex; align-items: center; gap: 6px; }
      .typing-dots { display: inline-flex; gap: 3px; }
      .typing-dots i { width: 4px; height: 4px; border-radius: 50%; background: var(--color-text-tertiary); animation: agent-blink 1.2s infinite; }
      .typing-dots i:nth-child(2) { animation-delay: 0.2s; }
      .typing-dots i:nth-child(3) { animation-delay: 0.4s; }
      @keyframes agent-blink { 0%,100% { opacity: 0.2; } 50% { opacity: 1; } }

      /* ---- Done summary ---- */
      .done-summary { font-size: var(--font-size-sm); color: var(--color-text-primary); font-family: var(--font-sans); line-height: var(--line-height-relaxed); margin-bottom: var(--space-2); }

      /* ---- Artifact row (single line, download only) ---- */
      .artifact-rows { display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-3); }
      .artifact-row { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-2) var(--space-3); border: 1px solid var(--color-border-subtle); border-radius: var(--radius-md); background: var(--color-bg-secondary); }
      .artifact-row-ic { color: var(--color-brand-primary); display: inline-flex; flex-shrink: 0; }
      .artifact-row-info { flex: 1; min-width: 0; }
      .artifact-row-name { font-size: var(--font-size-sm); font-weight: var(--font-weight-medium); color: var(--color-text-primary); font-family: var(--font-sans); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .artifact-row-meta { font-size: var(--font-size-xs); color: var(--color-text-secondary); font-family: var(--font-sans); }
      .artifact-row .btn-primary.btn-sm { padding: 5px 12px; font-size: var(--font-size-xs); border-radius: var(--radius-full); }

      /* ---- Link artifact variant (no button, whole card navigates) ---- */
      .artifact-link { text-decoration: none; color: inherit; cursor: pointer;
        transition: border-color var(--transition-fast), background var(--transition-fast), box-shadow var(--transition-fast); }
      .artifact-link:hover { border-color: var(--color-brand-primary); background: var(--color-brand-primary-soft); }
      .artifact-link:focus-visible { outline: 2px solid var(--color-brand-primary); outline-offset: 2px; }
      .artifact-row-arrow { display: inline-flex; flex-shrink: 0; color: var(--color-text-tertiary);
        transition: transform var(--transition-fast), color var(--transition-fast); }
      .artifact-link:hover .artifact-row-arrow { color: var(--color-brand-primary); transform: translate(2px, -2px); }

      /* ---- Next step: flowing text + inline buttons ---- */
      .next-flow { font-size: var(--font-size-sm); color: var(--color-text-secondary); font-family: var(--font-sans); line-height: var(--line-height-normal); }
      .next-flow .action-chip { display: inline-flex; vertical-align: middle; margin: 0 2px; }

      /* ---- Composer stop state (run page) — on-brand, not alarming ---- */
      .composer-send.stop-state { background: var(--color-brand-primary-soft); color: var(--color-brand-primary); }
      .composer-send.stop-state:hover { background: var(--color-brand-primary); color: var(--color-text-inverse); }

      @media (prefers-reduced-motion: reduce) {
        .spinner-dot { animation: none; }
        .typing-dots i { animation: none; opacity: 0.6; }
      }
    </style>'''

def log_entry(etype, label, text, state="done", meta=""):
    ic = {"think": EYE, "exec": ZAP, "check": CHK}[etype]
    # labels restored (B4 rolled back); only the running (active) step shows a neutral "进行中" cue
    extra = '<div class="log-entry-meta">%s 进行中</div>' % SPIN if state == "active" else ""
    return '''                  <div class="log-entry %s %s">
                    <div class="log-entry-ic">%s</div>
                    <div class="log-entry-main">
                      <div class="log-entry-label">%s</div>
                      <div class="log-entry-text">%s</div>%s
                    </div>
                  </div>''' % (etype, state, ic, label, text, extra)

# ---------- RUN page agent turn ----------
RUN_BLOCK = '''              <!-- ============ AGENT TURN (RUNNING) ============ -->
              <div class="agent-turn animate-in slide-in-from-bottom">
                <div class="agent-body">
                  <details class="process-details" open>
                    <summary>
                      <div class="agent-head">
                        <div class="agent-avatar">%s</div>
                        <span class="agent-name">iProduct</span>
                        <span class="agent-status running">%s 执行中</span>
                        %s
                      </div>
                    </summary>
                    <div class="process-log">
%s
%s
%s
%s
%s
%s
                    </div>
                    <div class="process-hint">Agent 正在继续执行…<span class="typing-dots"><i></i><i></i><i></i></span></div>
                  </details>
                </div>
              </div>
''' % (
    AVATAR, SPIN, CHEVRON,
    log_entry("think", "思考", "识别上传文件为 OD 设计文档（xlsx），解析结构以获取器件清单与位号映射。"),
    log_entry("exec", "执行", "调用 <code>skill-local-cv-doc-generation</code> 解析器件清单与位号映射。"),
    log_entry("check", "检查", "校验 MBG 料号库版本 v2.3，料号映射无冲突。"),
    log_entry("think", "思考", "匹配到最优下一步 skill — <code>super-bom-loadsheet-generation</code>，准备生成 Super BOM。"),
    log_entry("exec", "执行", "调用 <code>skill-super-bom-loadsheet-generation</code> 生成 Tablet Super BOM 物料清单。", state="active"),
    log_entry("check", "检查", "待生成完成后校验位号覆盖率。", state="pending"),
)

# ---------- DONE page agent turn ----------
DONE_BLOCK = '''              <!-- ============ AGENT TURN (DONE) ============ -->
              <div class="agent-turn animate-in slide-in-from-bottom">
                <div class="agent-body">
                  <details class="process-details">
                    <summary>
                      <div class="agent-head">
                        <div class="agent-avatar">%s</div>
                        <span class="agent-name">iProduct</span>
                        <span class="agent-status done">%s 已完成</span>
                        <span class="agent-time">31m59s</span>
                        %s
                      </div>
                    </summary>
                    <div class="process-log">
%s
%s
%s
%s
%s
%s
                    </div>
                  </details>
                  <p class="done-summary">已基于 Sycamore-OD_V2.3.xlsx 生成 Tablet Super BOM，包含 1,284 个器件、3,902 条位号映射，并创建对应的 PLM 文档草稿，请下载核对。</p>
                  <div class="artifact-rows">
                    <div class="artifact-row">
                      <span class="artifact-row-ic">%s</span>
                      <div class="artifact-row-info">
                        <div class="artifact-row-name">Tablet_Super_BOM.xlsx</div>
                        <div class="artifact-row-meta">XLSX · 2.4 MB · 刚刚生成</div>
                      </div>
                      <button class="btn-primary btn-sm" type="button" aria-label="下载 Tablet_Super_BOM.xlsx">下载</button>
                    </div>
                    <div class="artifact-row">
                      <span class="artifact-row-ic">%s</span>
                      <div class="artifact-row-info">
                        <div class="artifact-row-name">MBG_PLM_Draft.docx</div>
                        <div class="artifact-row-meta">DOCX · 1.1 MB · 刚刚生成</div>
                      </div>
                      <button class="btn-primary btn-sm" type="button" aria-label="下载 MBG_PLM_Draft.docx">下载</button>
                    </div>
                    <a class="artifact-row artifact-link" href="https://midhsit.lenovo.com/Windchill/app/#ptc1/tcomp/infoPage?ContainerOid=OR:wt.pdmlink.PDMLinkProduct:6719348244&oid=VR:wt.doc.WTDocument:8658428038&u8=1" target="_blank" rel="noopener noreferrer" aria-label="打开 PLM 文档：0000934077 - Sycamore_Pen_Checklist_V1.0_20260807（新窗口）">
                      <span class="artifact-row-ic">%s</span>
                      <div class="artifact-row-info">
                        <div class="artifact-row-name">0000934077 - Sycamore_Pen_Checklist_V1.0_20260807</div>
                        <div class="artifact-row-meta">外部链接 · Windchill PLM</div>
                      </div>
                      <span class="artifact-row-arrow">%s</span>
                    </a>
                  </div>
                  <div class="next-flow">
                    你可以 <button class="action-chip" type="button">继续生成 PLM 文档</button>、<button class="action-chip" type="button">导出汇总报告</button> 或 <button class="action-chip" type="button">重新运行</button>。
                  </div>
                </div>
              </div>
''' % (
    AVATAR, CHK, CHEVRON,
    log_entry("think", "思考", "识别上传文件为 OD 设计文档（xlsx），解析结构以获取器件清单与位号映射。"),
    log_entry("exec", "执行", "调用 <code>skill-local-cv-doc-generation</code> 解析器件清单与位号映射。"),
    log_entry("check", "检查", "校验 MBG 料号库版本 v2.3，料号映射无冲突。"),
    log_entry("think", "思考", "匹配到最优下一步 skill — <code>super-bom-loadsheet-generation</code>，准备生成 Super BOM。"),
    log_entry("exec", "执行", "调用 <code>skill-super-bom-loadsheet-generation</code> 生成 Tablet Super BOM 物料清单。"),
    log_entry("check", "检查", "生成完成后校验位号覆盖率，全部位号已匹配。"),
    DOC, DOC, LINK, EXT,
)

OLD_SEND_BTN = '''                    <button class="composer-send" type="button" title="发送" aria-label="发送">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                    </button>'''
NEW_STOP_BTN = '''                    <button class="composer-send stop-state" type="button" title="中止" aria-label="中止">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
                    </button>'''

def patch(path, marker, block, replace_send=False):
    c = io.open(path, encoding="utf-8").read()
    # CSS block
    c = re.sub(r'<style id="agent-components">.*?</style>', NEW_CSS, c, flags=re.DOTALL)
    # agent turn block
    pat = re.compile(re.escape(marker) + r'.*?\n              </div>\n', re.DOTALL)
    if not pat.search(c):
        raise SystemExit("MARKER NOT FOUND: " + marker)
    c = pat.sub(block, c, count=1)
    # composer button for run page only (idempotent: skip if already stop-state)
    if replace_send:
        if OLD_SEND_BTN in c:
            c = c.replace(OLD_SEND_BTN, NEW_STOP_BTN)
        elif NEW_STOP_BTN not in c:
            raise SystemExit("SEND BUTTON NOT FOUND in " + path)
    io.open(path, "w", encoding="utf-8").write(c)
    print("patched:", path)

patch(os.path.join(BASE, "playbook-bom-upload-run.html"),
      "<!-- ============ AGENT TURN (RUNNING) ============ -->", RUN_BLOCK, replace_send=True)
patch(os.path.join(BASE, "playbook-bom-upload-done.html"),
      "<!-- ============ AGENT TURN (DONE) ============ -->", DONE_BLOCK, replace_send=False)
print("DONE")
