(function () {
  "use strict";

  const $ = (sel, r) => (r || document).querySelector(sel);
  const $$ = (sel, r) => [...(r || document).querySelectorAll(sel)];

  const LS_PROJECTS = "mutiagent_projects_v2";
  const LS_USER = "mutiagent_user_label";
  const LS_DEFAULT_EVAL = "mutiagent_default_run_eval";
  const LS_DEFAULT_AUTO_VENV = "mutiagent_default_auto_venv";
  const LS_DEFAULT_AUTO_INSTALL_PY = "mutiagent_default_auto_install_python";
  const LS_RULES = "mutiagent_rules_draft";
  const LS_HISTORY = "mutiagent_run_history_v2";
  const SS_LAST = "mutiagent_last_workflow_json";
  const SNAP = "mutiagent_snap_";
  const SNAP_ORDER = "mutiagent_snap_order";
  const MAX_SNAPS = 8;
  /** 与 SS_LAST 分离：仅含 evaluation 中「报告分析」所需字段，避免整包过大未写入 sessionStorage 时无表数据 */
  const SS_EVAL_LITE = "mutiagent_eval_lite";

  let lastResult = null;
  let lastSnapshot = null;
  let chartTrend = null;
  let chartPie = null;
  let network = null;
  let strategyOrder = [];
  let selectedCaseIndex = -1;
  let currentProjectDetail = -1;
  let changesReturnTab = "run";

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function uid() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  }

  function loadProjects() {
    try {
      const raw = localStorage.getItem(LS_PROJECTS);
      const arr = JSON.parse(raw || "[]");
      return Array.isArray(arr) ? arr : [];
    } catch {
      return [];
    }
  }

  function saveProjects(list) {
    localStorage.setItem(LS_PROJECTS, JSON.stringify(list));
  }

  function loadHistory() {
    try {
      const h = JSON.parse(localStorage.getItem(LS_HISTORY) || "[]");
      return Array.isArray(h) ? h : [];
    } catch {
      return [];
    }
  }

  function saveHistory(h) {
    const trimmed = h.slice(-50);
    localStorage.setItem(LS_HISTORY, JSON.stringify(trimmed));
    return trimmed;
  }

  function pushSnapOrder(id) {
    try {
      let order = JSON.parse(sessionStorage.getItem(SNAP_ORDER) || "[]");
      if (!Array.isArray(order)) order = [];
      order.push(id);
      while (order.length > MAX_SNAPS) {
        const old = order.shift();
        sessionStorage.removeItem(SNAP + old);
      }
      sessionStorage.setItem(SNAP_ORDER, JSON.stringify(order));
    } catch {
      /* */
    }
  }

  function countHighRisk(data) {
    if (!data) return 0;
    const tr = data.top_risks || [];
    if (tr.length) return tr.length;
    const cat = data.semantic_units_catalog || [];
    return cat.filter((u) => u.test_priority === "P0").length;
  }

  function riskBreakdown(data) {
    const o = { P0: 0, P1: 0, P2: 0, other: 0 };
    if (!data) return o;
    (data.semantic_units_catalog || []).forEach((u) => {
      const p = u.test_priority || "other";
      if (o[p] !== undefined) o[p]++;
      else o.other++;
    });
    return o;
  }

  function switchView(id) {
    $$(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.view === id));
    $$(".view").forEach((v) => v.classList.toggle("view-active", v.id === "view-" + id));
    if (id === "dashboard") refreshDashboard();
    if (id === "projects") renderProjectsGrid();
    if (id === "changes") renderChangesTable();
    if (id === "impact") renderImpactPage();
    if (id === "impact-graph") renderImpactGraphPage();
    if (id === "testing") renderTestingPage();
    if (id === "cases") renderCasesPage();
    if (id === "structured-cases") renderStructuredCasesPage();
    if (id === "execution") renderExecutionPage();
    if (id === "run-analysis") renderRunAnalysisPage();
    if (id === "reports") renderReportsPage();
  }

  function renderImpactGraphInto(networkHost, filterP0, showSyms) {
    if (typeof vis === "undefined" || !vis.Network) return;
    const mainScroll = document.querySelector(".app-main");
    const prevScrollTop = mainScroll ? mainScroll.scrollTop : null;
    const { nodes, edges } = buildVisData(lastResult, filterP0, showSyms);
    if (networkHost && nodes.length === 0) {
      networkHost.innerHTML =
        "<p class='empty impact-empty'>当前筛选条件下无可展示节点。可尝试：<br/>1) 取消「仅高优 P0 相关」；2) 保持「显示符号节点」开启；3) 重新运行一次分析。</p>";
      if (network) {
        network.destroy();
        network = null;
      }
      return;
    }
    const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
    const opts = {
      physics: {
        enabled: true,
        stabilization: { iterations: 200 },
        barnesHut: { gravitationalConstant: -8000 },
      },
      interaction: {
        hover: true,
        zoomView: true,
        // 未按修饰键时滚轮交给页面滚动，避免与 .app-main 抢事件、体感“反向跳”
        zoomKey: "ctrlKey",
      },
    };
    if (network) network.destroy();
    if (networkHost) networkHost.innerHTML = "";
    network = new vis.Network(networkHost, data, opts);
    const stopPhysics = function () {
      try {
        network.setOptions({ physics: false });
      } catch (e) {
        /* destroyed */
      }
    };
    network.once("stabilizationIterationsDone", stopPhysics);
    network.once("afterDrawing", function () {
      if (prevScrollTop != null && mainScroll) {
        mainScroll.scrollTop = prevScrollTop;
      }
    });
    setTimeout(stopPhysics, 5000);
  }

  function refreshTopProjectSelect() {
    const sel = $("#top_project");
    const projects = loadProjects();
    const cur = sel.value;
    sel.innerHTML = '<option value="">— 选择项目 —</option>';
    projects.forEach((p, i) => {
      const o = document.createElement("option");
      o.value = String(i);
      o.textContent = p.name || p.path || "project";
      sel.appendChild(o);
    });
    if (cur !== "" && projects[Number(cur)]) sel.value = cur;
  }

  function applyTopProject() {
    const idx = $("#top_project").value;
    const projects = loadProjects();
    if (idx === "" || !projects[Number(idx)]) return;
    const p = projects[Number(idx)];
    $("#repo_path").value = p.path || "";
    if (p.branch) $("#top_branch").value = p.branch;
  }

  function setStatus(msg, kind) {
    const el = $("#status");
    if (!el) return;
    el.textContent = msg || "";
    el.className = "status-line" + (kind ? " " + kind : "");
  }

  function fmtTs(ts) {
    if (!ts) return "—";
    return String(ts).replace("T", " ").slice(0, 19);
  }

  async function fetchProjectRunsFromDb(repoPath) {
    const u = "/db/project-runs?repo_path=" + encodeURIComponent(repoPath) + "&limit=20";
    const r = await fetch(u);
    if (!r.ok) throw new Error("读取项目历史失败: HTTP " + r.status);
    return await r.json();
  }

  function renderProjectRuns(el, data) {
    if (!el) return;
    const runs = (data && data.runs) || [];
    if (!runs.length) {
      el.innerHTML = "<p class='empty'>数据库中暂无该项目历史记录（先运行一次全流程）。</p>";
      return;
    }
    el.innerHTML = runs
      .map(function (run) {
        const cs = run.case_summary || {};
        const summary =
          "passed " +
          (cs.passed || 0) +
          " / failed " +
          (cs.failed || 0) +
          " / error " +
          (cs.error || 0) +
          " / skipped " +
          (cs.skipped || 0);
        const files = Array.isArray(run.generated_tests) ? run.generated_tests : [];
        const caseDetails = Array.isArray(run.case_details) ? run.case_details : [];
        const caseRowsHtml = caseDetails.length
          ? "<div class='db-cases-wrap'><table class='db-cases-table'><thead><tr><th>状态</th><th>类</th><th>用例</th><th>耗时</th><th>详情</th></tr></thead><tbody>" +
            caseDetails
              .map(function (c) {
                const detail = (c.detail || "").trim();
                const detailHtml = detail
                  ? "<details><summary>展开</summary><pre class='json-out db-case-detail'>" + escapeHtml(detail) + "</pre></details>"
                  : "—";
                return (
                  "<tr><td>" +
                  escapeHtml(String(c.status || "—")) +
                  "</td><td class='mono-inline'>" +
                  escapeHtml(c.classname || "") +
                  "</td><td class='mono-inline'>" +
                  escapeHtml(c.case_name || "") +
                  "</td><td>" +
                  escapeHtml(String(c.case_time || "")) +
                  "</td><td>" +
                  detailHtml +
                  "</td></tr>"
                );
              })
              .join("") +
            "</tbody></table></div>"
          : "<p class='hint'>该 run 没有逐条用例记录（可能未生成 junit）。</p>";
        const filesHtml = files.length
          ? files
              .map(function (f) {
                return (
                  "<details class='db-file-item'><summary>" +
                  escapeHtml(f.file_path || "test.py") +
                  " · " +
                  escapeHtml(String(f.status || "—")) +
                  "</summary><pre class='json-out db-test-content'>" +
                  escapeHtml(f.content || "") +
                  "</pre></details>"
                );
              })
              .join("")
          : "<p class='hint'>该 run 未记录 generated_test_files。</p>";
        return (
          "<details class='db-run-item'><summary><strong>" +
          escapeHtml(fmtTs(run.started_at)) +
          "</strong> · 状态 " +
          escapeHtml(run.status || "—") +
          " · exit_code " +
          escapeHtml(String(run.exit_code == null ? "—" : run.exit_code)) +
          " · 文件 " +
          files.length +
          "</summary><p class='hint'>run_id: <code>" +
          escapeHtml(run.run_id || "") +
          "</code></p><p class='hint'>用例统计: " +
          escapeHtml(summary) +
          "</p>" +
          (run.error_message ? "<p class='hint'>错误: " + escapeHtml(run.error_message) + "</p>" : "") +
          "<h4 class='block-title'>逐条执行情况</h4>" +
          caseRowsHtml +
          "<h4 class='block-title'>生成的测试文件</h4>" +
          "<div class='db-files-wrap'>" +
          filesHtml +
          "</div></details>"
        );
      })
      .join("");
  }

  function setWorkflowProgress(show, ev) {
    const wrap = $("#workflow_progress_wrap");
    const fill = $("#workflow_progress_fill");
    const lab = $("#workflow_progress_label");
    const bar = wrap && wrap.querySelector(".workflow-progress-bar");
    if (!wrap || !fill || !lab) return;
    if (!show) {
      wrap.classList.add("hidden");
      if (bar) bar.removeAttribute("aria-valuenow");
      return;
    }
    wrap.classList.remove("hidden");
    const total = ev && ev.total > 0 ? ev.total : 1;
    const cur = ev && ev.current != null ? ev.current : 0;
    const pct = Math.min(100, Math.round((cur / total) * 100));
    fill.style.width = pct + "%";
    const label = ev && ev.label ? ev.label : "处理中";
    lab.textContent = label + "（" + cur + "/" + total + "）";
    if (bar) bar.setAttribute("aria-valuenow", String(pct));
  }

  async function readNdjsonWorkflow(repo, diff, runEval, autoVenv, autoInstallPython) {
    const r = await fetch("/generate-tests-stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        repo_path: repo,
        diff,
        run_eval: runEval,
        auto_venv: autoVenv,
        auto_install_python: autoInstallPython,
      }),
    });
    if (!r.ok) {
      const text = await r.text();
      let msg = "HTTP " + r.status;
      try {
        const j = JSON.parse(text);
        if (j.detail != null) msg = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
      } catch {
        if (text) msg = text.slice(0, 500);
      }
      throw new Error(msg);
    }
    const reader = r.body.pipeThrough(new TextDecoderStream()).getReader();
    let buffer = "";
    let lastComplete = null;
    let lastError = null;
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      buffer += chunk.value;
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      for (const line of lines) {
        if (!line.trim()) continue;
        let ev;
        try {
          ev = JSON.parse(line);
        } catch {
          continue;
        }
        if (ev.type === "progress") setWorkflowProgress(true, ev);
        else if (ev.type === "error") lastError = ev.message || String(ev);
        else if (ev.type === "complete") lastComplete = ev.result;
      }
    }
    const tail = buffer.trim();
    if (tail) {
      try {
        const ev = JSON.parse(tail);
        if (ev.type === "complete") lastComplete = ev.result;
        if (ev.type === "error") lastError = ev.message;
      } catch {
        /* */
      }
    }
    if (lastError) throw new Error(lastError);
    if (!lastComplete) throw new Error("未收到完整结果");
    return lastComplete;
  }

  async function checkHealth() {
    const badge = $("#health_badge");
    try {
      const r = await fetch("/health");
      const j = await r.json();
      if (j.ok) {
        badge.textContent = "API 正常";
        badge.className = "badge ok";
        const dh = $("#dash_health");
        if (dh) dh.textContent = "正常";
      } else throw new Error();
    } catch {
      badge.textContent = "API 异常";
      badge.className = "badge fail";
      const dh = $("#dash_health");
      if (dh) dh.textContent = "异常";
    }
  }

  function destroyCharts() {
    if (chartTrend) {
      chartTrend.destroy();
      chartTrend = null;
    }
    if (chartPie) {
      chartPie.destroy();
      chartPie = null;
    }
  }

  function updateCharts() {
    if (typeof Chart === "undefined") return;
    const hist = loadHistory();
    const recent = hist.slice(-10);
    const labels = recent.map((h) => h.at.slice(5, 16).replace("T", " "));
    const failData = recent.map((h) => (h.exit_code != null && h.exit_code !== 0 ? 1 : 0));

    const ctx1 = $("#chart_trend");
    if (ctx1) {
      if (chartTrend) chartTrend.destroy();
      chartTrend = new Chart(ctx1, {
        type: "line",
        data: {
          labels: labels.length ? labels : ["暂无"],
          datasets: [
            {
              label: "失败=1 通过=0",
              data: recent.length ? failData : [0],
              borderColor: "#f85149",
              backgroundColor: "rgba(248,81,73,0.15)",
              tension: 0.25,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: "#8b949e" } } },
          scales: {
            x: { ticks: { color: "#8b949e", maxRotation: 45 } },
            y: { min: 0, max: 1, ticks: { color: "#8b949e", stepSize: 1 } },
          },
        },
      });
    }

    const br = lastResult ? riskBreakdown(lastResult) : { P0: 0, P1: 0, P2: 0 };
    const ctx2 = $("#chart_pie");
    if (ctx2) {
      if (chartPie) chartPie.destroy();
      const vals = [br.P0, br.P1, br.P2].some((v) => v > 0) ? [br.P0, br.P1, br.P2] : [1, 0, 0];
      chartPie = new Chart(ctx2, {
        type: "doughnut",
        data: {
          labels: ["P0", "P1", "P2"],
          datasets: [
            {
              data: vals,
              backgroundColor: ["#f85149", "#d29922", "#58a6ff"],
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "bottom", labels: { color: "#8b949e" } } },
        },
      });
    }
  }

  function refreshDashboard() {
    const dm = $("#dash_metric_changes");
    const dr = $("#dash_metric_risk");
    const dc = $("#dash_metric_cov");
    const df = $("#dash_metric_fail");
    if (!dm) return;

    if (lastResult) {
      dm.textContent = String((lastResult.changed_files || []).length);
      dr.textContent = String(countHighRisk(lastResult));
      const cov = lastResult.evaluation && lastResult.evaluation.coverage;
      dc.textContent = cov != null ? (cov * 100).toFixed(1) + "%" : "—";
    } else {
      dm.textContent = "—";
      dr.textContent = "—";
      dc.textContent = "—";
    }

    const hist = loadHistory().slice(-10);
    if (hist.length) {
      const fails = hist.filter((h) => h.exit_code != null && h.exit_code !== 0).length;
      df.textContent = ((fails / hist.length) * 100).toFixed(0) + "%";
    } else {
      df.textContent = "—";
    }

    updateCharts();
  }

  function recordHistory(entry, snapshot) {
    let h = loadHistory();
    h.push(entry);
    h = saveHistory(h);
    try {
      sessionStorage.setItem(SNAP + entry.id, JSON.stringify(snapshot));
      pushSnapOrder(entry.id);
    } catch {
      /* quota */
    }
    renderChangesTable();
  }

  function _shrinkEvalForSessionStorage(ev) {
    if (!ev || typeof ev !== "object") return ev;
    const max = 120000;
    const clip = function (t) {
      if (typeof t !== "string") return t;
      return t.length <= max ? t : t.slice(0, max) + "\n…[已截断；完整文本见 evaluation.report_dir 下 pytest_stdout.txt / pytest_stderr.txt]";
    };
    return Object.assign({}, ev, { stdout: clip(ev.stdout), stderr: clip(ev.stderr) });
  }

  function _persistEvalLite(ev) {
    if (!ev || typeof ev !== "object") return;
    try {
      sessionStorage.setItem(
        SS_EVAL_LITE,
        JSON.stringify({
          ran: !!ev.ran,
          exit_code: ev.exit_code != null ? ev.exit_code : null,
          report_dir: ev.report_dir || null,
          coverage: ev.coverage != null ? ev.coverage : null,
          pytest_summary: ev.pytest_summary && typeof ev.pytest_summary === "object" ? ev.pytest_summary : {},
          pytest_cases: Array.isArray(ev.pytest_cases) ? ev.pytest_cases : [],
        })
      );
    } catch {
      /* quota */
    }
  }

  function saveLastResult(data, clientMeta) {
    lastResult = data;
    lastSnapshot = clientMeta || lastSnapshot;
    const ev = data && data.evaluation;
    _persistEvalLite(ev);
    try {
      const slim = ev ? Object.assign({}, data, { evaluation: _shrinkEvalForSessionStorage(ev) }) : data;
      const s = JSON.stringify(slim);
      if (s.length < 3.5 * 1024 * 1024) sessionStorage.setItem(SS_LAST, s);
    } catch {
      /* */
    }
    $("#fab_raw").disabled = false;
    $("#raw_json").textContent = JSON.stringify(data, null, 2);
    renderChangesSummary(data);
    refreshDashboard();
    renderImpactPage();
    renderTestingPage();
    renderCasesPage();
    renderExecutionPage();
    renderRunAnalysisPage();
    renderReportsPage();
  }

  function loadLastFromSession() {
    try {
      const s = sessionStorage.getItem(SS_LAST);
      const liteS = sessionStorage.getItem(SS_EVAL_LITE);
      if (s) {
        lastResult = JSON.parse(s);
        $("#fab_raw").disabled = false;
        $("#raw_json").textContent = JSON.stringify(lastResult, null, 2);
      } else if (liteS) {
        /* 整包因体积未写入 SS_LAST 时，仍可从精简 evaluation 恢复「报告分析」等依赖 pytest_cases 的视图 */
        lastResult = { changed_files: [], evaluation: JSON.parse(liteS) };
        $("#fab_raw").disabled = false;
        $("#raw_json").textContent = JSON.stringify(lastResult, null, 2);
      }
      if (liteS && lastResult) {
        const lite = JSON.parse(liteS);
        lastResult.evaluation = Object.assign({}, lastResult.evaluation || {}, lite);
      }
    } catch {
      lastResult = null;
    }
  }

  function renderChangesSummary(data) {
    const el = $("#changes_summary");
    if (!el) return;
    if (!data) {
      el.innerHTML = "<p class='empty'>提交后更新</p>";
      return;
    }
    const ev = data.evaluation || {};
    let html = "<p>变更文件：<strong>" + (data.changed_files || []).length + "</strong></p>";
    html += "<p>高风险单元：<strong>" + countHighRisk(data) + "</strong></p>";
    html +=
      "<p>测试计划（结构化用例）：<strong>" +
      (function () {
        const tp = data.test_plan;
        if (!tp) return 0;
        if (Array.isArray(tp)) return tp.length;
        return (tp.test_cases || []).length;
      })() +
      "</strong></p>";
    html += "<p>生成测试：<strong>" + (data.generated_tests || []).length + "</strong></p>";
    if (ev.ran) html += "<p>pytest 退出码：<strong>" + (ev.exit_code ?? "—") + "</strong></p>";
    el.innerHTML = html;
  }

  function buildVisData(data, filterP0, showSyms) {
    const nodes = [];
    const edges = [];
    if (!data || !data.impact_graph) return { nodes, edges };

    const p0ids = new Set();
    (data.semantic_units_catalog || []).forEach((u) => {
      if (u.test_priority === "P0") p0ids.add(u.semantic_unit_id);
    });

    const ig = data.impact_graph || [];
    ig.forEach((file) => {
      const fid = "f:" + file.file;
      const fileRisk = (file.symbols || []).some((s) =>
        (s.semantic_unit_ids || []).some((id) => !filterP0 || p0ids.has(id))
      );
      if (filterP0 && (file.symbols || []).length && !fileRisk) return;

      nodes.push({
        id: fid,
        label: file.file.split("/").pop() || file.file,
        title: file.file,
        shape: "box",
        color: { background: "#21262d", border: "#58a6ff" },
        font: { color: "#e6edf3", size: 13 },
      });

      if (!showSyms) return;
      const seenSymIds = new Set();
      (file.symbols || []).forEach((sym) => {
        const su = sym.semantic_unit_ids || [];
        if (filterP0 && su.length && !su.some((id) => p0ids.has(id))) return;
        const sid = "s:" + file.file + "::" + (sym.symbol_id || sym.name || "");
        if (seenSymIds.has(sid)) return;
        seenSymIds.add(sid);
        nodes.push({
          id: sid,
          label: sym.name || sym.symbol_id,
          title: sym.symbol_id || "",
          shape: "ellipse",
          color: { background: "#1a2332", border: "#388bfd" },
          font: { color: "#8b949e", size: 12 },
        });
        edges.push({ from: fid, to: sid, arrows: "to", color: { color: "#30363d" } });
      });
    });

    return { nodes, edges };
  }

  function renderImpactPage() {
    const left = $("#impact_left");
    const right = $("#impact_right");
    const cat = $("#impact_catalog");
    if (!left) return;

    if (!lastResult) {
      left.innerHTML = "<p class='empty'>请先在「代码变更」运行全流程。</p>";
      right.innerHTML = "";
      if (cat) cat.textContent = "";
      if (network) {
        network.destroy();
        network = null;
      }
      return;
    }

    const files = lastResult.changed_files || [];
    left.innerHTML =
      "<p><strong>变更文件</strong> " +
      files.length +
      " 个</p><ul class='settings-list'>" +
      files.slice(0, 40).map((f) => "<li>" + escapeHtml(f) + "</li>").join("") +
      (files.length > 40 ? "<li>…</li>" : "") +
      "</ul>";

    const tr = lastResult.top_risks || [];
    const impactDebug = (lastResult.debug && lastResult.debug.impact) || {};
    const codeDebug = (lastResult.debug && lastResult.debug.code_change) || {};
    let diag = "";
    if (!lastResult.impact_graph || !lastResult.impact_graph.length) {
      const reasons = [];
      if (impactDebug.fallback_from_diff_hunks) {
        reasons.push("已启用 diff-hunk 降级，但当前仍缺少可视化节点");
      }
      if (impactDebug.semantic_unit_catalog_count === 0) {
        reasons.push("语义单元目录为空（semantic_units_catalog=0）");
      }
      if (codeDebug.analysis_degraded) {
        reasons.push("上游变更解析退化（analysis_degraded=true）");
      }
      if (!reasons.length) reasons.push("当前结果未产出 impact_graph 数据");
      diag =
        "<div class='impact-diagnose'><strong>图谱为空原因：</strong><ul class='settings-list'>" +
        reasons.map((r) => "<li>" + escapeHtml(r) + "</li>").join("") +
        "</ul></div>";
    }
    right.innerHTML =
      "<p><strong>top_risks</strong> " +
      tr.length +
      " 条</p><ul class='settings-list'>" +
      tr
        .slice(0, 12)
        .map((r) => "<li><code>" + escapeHtml(r.semantic_unit_id || "") + "</code> — " + escapeHtml(r.reason || "") + "</li>")
        .join("") +
      "</ul><p class='hint'>筛选：影响图中可隐藏非 P0 符号边</p>" +
      diag;

    const catalog = lastResult.semantic_units_catalog || [];
    if (cat) {
      cat.textContent = JSON.stringify(catalog.slice(0, 60), null, 2);
      if (catalog.length > 60) cat.textContent += "\n/* …共 " + catalog.length + " 条 */\n";
    }

    const filterP0 = $("#impact_filter_p0").checked;
    const showSyms = $("#impact_filter_sym").checked;
    const networkHost = $("#vis_network");
    renderImpactGraphInto(networkHost, filterP0, showSyms);
  }

  function renderImpactGraphPage() {
    const meta = $("#impact_graph_meta");
    const host = $("#vis_network_full");
    if (!meta || !host) return;
    if (!lastResult) {
      meta.innerHTML = "<p class='empty'>请先在「代码变更」运行全流程。</p>";
      host.innerHTML = "";
      if (network) {
        network.destroy();
        network = null;
      }
      return;
    }
    const files = (lastResult.changed_files || []).length;
    const risks = countHighRisk(lastResult);
    const units = (lastResult.semantic_units_catalog || []).length;
    meta.innerHTML =
      "<p>变更文件 <strong>" +
      files +
      "</strong> 个 · 高风险单元 <strong>" +
      risks +
      "</strong> 个 · 语义单元 <strong>" +
      units +
      "</strong> 条</p>";
    const filterP0 = $("#impact_graph_filter_p0").checked;
    const showSyms = $("#impact_graph_filter_sym").checked;
    renderImpactGraphInto(host, filterP0, showSyms);
  }

  function mergeStrategies(data) {
    if (!data) return [];
    const rows = [];
    const seen = new Set();
    (data.impact_test_plan || []).forEach((p) => {
      const k = "i:" + (p.symbol_id || p.target);
      if (seen.has(k)) return;
      seen.add(k);
      rows.push({
        source: "impact",
        target: p.target || "",
        priority: p.priority || "P2",
        reason: p.reason || "",
        types: p.test_types || [],
      });
    });
    const planCases =
      data.test_plan && typeof data.test_plan === "object" && !Array.isArray(data.test_plan) && data.test_plan.test_cases
        ? data.test_plan.test_cases
        : Array.isArray(data.test_plan)
          ? data.test_plan
          : data.test_plan_items || [];
    planCases.forEach((p) => {
      const k =
        "t:" +
        (p.test_case_id || p.target || "") +
        (p.scenario || p.intent || "");
      if (seen.has(k)) return;
      seen.add(k);
      if (p.test_case_id) {
        rows.push({
          source: "plan_case",
          target: p.target || "",
          priority: p.priority || "P2",
          reason: (p.scenario || "") + (p.assertions && p.assertions.length ? " | 断言: " + p.assertions.join("; ") : ""),
          types: p.layer ? [p.layer] : [],
        });
      } else {
        rows.push({
          source: "plan",
          target: p.target || "",
          priority: typeof p.priority === "number" ? (p.priority > 0.7 ? "P0" : p.priority > 0.4 ? "P1" : "P2") : p.priority || "P2",
          reason: p.intent || "",
          types: [],
        });
      }
    });
    const priOrder = { P0: 0, P1: 1, P2: 2 };
    rows.sort((a, b) => (priOrder[a.priority] || 9) - (priOrder[b.priority] || 9));
    return rows;
  }

  function inferTestTypes(row) {
    const tags = [];
    const r = (row.reason || "").toLowerCase();
    if (r.includes("api") || r.includes("http")) tags.push("API 测试");
    if (r.includes("ui") || r.includes("界面")) tags.push("UI 测试");
    if (!tags.length) tags.push("单元测试");
    if (row.types && row.types.length) return row.types.concat(tags).slice(0, 4);
    return tags;
  }

  function renderTestingPage() {
    const box = $("#testing_strategies");
    if (!box) return;
    if (!lastResult) {
      box.innerHTML = "<p class='empty'>暂无策略，请先运行分析。</p>";
      strategyOrder = [];
      return;
    }
    if (!strategyOrder.length) strategyOrder = mergeStrategies(lastResult);
    box.innerHTML = strategyOrder
      .map(function (row, i) {
        const types = inferTestTypes(row);
        return (
          "<div class='strategy-row' data-i='" +
          i +
          "'><div><div class='prio'><span class='prio-badge'>" +
          escapeHtml(String(row.priority)) +
          "</span><strong>" +
          escapeHtml(row.target || "(未命名)") +
          "</strong></div><div class='hint'>" +
          escapeHtml(row.reason || "") +
          "</div><div class='type-tags'>" +
          types.map((t) => "<span class='type-tag'>" + escapeHtml(t) + "</span>").join("") +
          "</div></div><div class='prio'><button type='button' class='btn btn-sm strat-up' data-i='" +
          i +
          "'>↑</button><button type='button' class='btn btn-sm strat-down' data-i='" +
          i +
          "'>↓</button></div></div>"
        );
      })
      .join("");

    box.querySelectorAll(".strat-up").forEach((btn) => {
      btn.addEventListener("click", () => {
        const i = Number(btn.dataset.i);
        if (i > 0) {
          const t = strategyOrder[i - 1];
          strategyOrder[i - 1] = strategyOrder[i];
          strategyOrder[i] = t;
          renderTestingPage();
        }
      });
    });
    box.querySelectorAll(".strat-down").forEach((btn) => {
      btn.addEventListener("click", () => {
        const i = Number(btn.dataset.i);
        if (i < strategyOrder.length - 1) {
          const t = strategyOrder[i + 1];
          strategyOrder[i + 1] = strategyOrder[i];
          strategyOrder[i] = t;
          renderTestingPage();
        }
      });
    });
  }

  function renderCasesPage() {
    const list = $("#case_list");
    const execSummary = $("#case_exec_summary");
    const execWrap = $("#case_exec_table_wrap");
    const tests = (lastResult && lastResult.generated_tests) || [];
    const ev = (lastResult && lastResult.evaluation) || {};
    const pytestCases = Array.isArray(ev.pytest_cases) ? ev.pytest_cases : [];
    if (!list) return;
    if (!tests.length) {
      list.innerHTML = "<div class='case-item'>无生成用例</div>";
      $("#case_detail_body").value = "";
      $("#case_detail_title").textContent = "用例中心";
      if (execSummary) execSummary.innerHTML = "<p class='empty'>暂无执行结果。</p>";
      if (execWrap) execWrap.innerHTML = "";
      return;
    }
    list.innerHTML = tests
      .map(
        (t, i) =>
          "<div class='case-item" +
          (i === selectedCaseIndex ? " active" : "") +
          "' data-i='" +
          i +
          "'>" +
          escapeHtml(t.path || "file " + i) +
          "</div>"
      )
      .join("");

    list.querySelectorAll(".case-item").forEach((el) => {
      el.addEventListener("click", () => {
        selectedCaseIndex = Number(el.dataset.i);
        $$(".case-item", list).forEach((x) => x.classList.remove("active"));
        el.classList.add("active");
        const t = tests[selectedCaseIndex];
        $("#case_detail_title").textContent = t.path || "用例";
        $("#case_detail_body").value = t.content || "";
        $("#case_detail_body").readOnly = false;
      });
    });

    if (selectedCaseIndex < 0 || selectedCaseIndex >= tests.length) selectedCaseIndex = 0;
    const t0 = tests[selectedCaseIndex];
    if (t0) {
      $("#case_detail_title").textContent = t0.path || "用例";
      $("#case_detail_body").value = t0.content || "";
      $("#case_detail_body").readOnly = false;
    }

    if (!execSummary || !execWrap) return;
    if (!ev.ran) {
      execSummary.innerHTML = "<p class='hint'>本次未执行 pytest，无法展示逐条状态。</p>";
      execWrap.innerHTML = "";
      return;
    }
    if (!pytestCases.length) {
      execSummary.innerHTML = "<p class='hint'>未解析到逐条用例结果（evaluation.pytest_cases 为空）。</p>";
      execWrap.innerHTML = "";
      return;
    }
    const passed = pytestCases.filter((c) => String(c.status || "").toLowerCase() === "passed").length;
    const failed = pytestCases.filter((c) => String(c.status || "").toLowerCase() === "failed").length;
    const errored = pytestCases.filter((c) => String(c.status || "").toLowerCase() === "error").length;
    const skipped = pytestCases.filter((c) => String(c.status || "").toLowerCase() === "skipped").length;
    execSummary.innerHTML =
      "<p>共 <strong>" +
      pytestCases.length +
      "</strong> 条：通过 <strong>" +
      passed +
      "</strong> / 失败 <strong>" +
      failed +
      "</strong> / 错误 <strong>" +
      errored +
      "</strong> / 跳过 <strong>" +
      skipped +
      "</strong></p>";
    const rows = pytestCases
      .map(function (c) {
        const st = String(c.status || "").toLowerCase();
        const bc = statusBadgeClass(st);
        const detail = (c.detail || "").trim();
        const detailCell = detail
          ? "<details class='ra-detail'><summary>展开</summary><pre class='ra-detail-pre'>" + escapeHtml(detail) + "</pre></details>"
          : "—";
        const badgeCls = bc ? " badge " + bc : " badge";
        return (
          "<tr class='ra-row ra-" +
          escapeHtml(bc || "na") +
          "'><td><span class='" +
          escapeHtml(badgeCls.trim()) +
          "'>" +
          escapeHtml(statusLabelZh(c.status)) +
          "</span></td><td class='mono ra-mono'>" +
          escapeHtml(c.classname || "") +
          "</td><td class='mono ra-mono'>" +
          escapeHtml(c.name || c.case_name || "") +
          "</td><td>" +
          escapeHtml(String(c.time ?? c.case_time ?? "")) +
          "</td><td>" +
          detailCell +
          "</td></tr>"
        );
      })
      .join("");
    execWrap.innerHTML =
      "<table class='run-analysis-table'><thead><tr><th>状态</th><th>类名</th><th>用例</th><th>耗时(s)</th><th>详情</th></tr></thead><tbody>" +
      rows +
      "</tbody></table>";
  }

  function toChineseScenario(tc) {
    const s = (tc.scenario || "").trim();
    if (s) return s;
    const layerMap = {
      unit: "单元测试",
      integration: "集成测试",
      contract: "契约测试",
      e2e: "端到端测试",
    };
    const layer = layerMap[tc.layer] || "测试";
    const target = tc.target || tc.symbol_id || "目标模块";
    const pri = tc.priority || "P2";
    return "验证「" + target + "」在" + layer + "层的关键行为（优先级 " + pri + "）";
  }

  function toChineseCaseType(layer) {
    const layerMap = {
      unit: "单元测试",
      integration: "集成测试",
      contract: "契约测试",
      e2e: "端到端测试",
    };
    return layerMap[layer] || "功能测试";
  }

  function toChinesePriority(priority) {
    const pri = String(priority || "P2");
    const map = { P0: "高", P1: "中", P2: "低" };
    return pri + "（" + (map[pri] || "一般") + "）";
  }

  function buildPreconditionText(tc) {
    const parts = [];
    const input = tc.input && typeof tc.input === "object" ? tc.input : {};
    const mock = tc.mock && typeof tc.mock === "object" ? tc.mock : {};
    if (Object.keys(input).length) parts.push("输入条件：" + JSON.stringify(input));
    if (Object.keys(mock).length) parts.push("Mock 条件：" + JSON.stringify(mock));
    return parts.length ? parts.join("；") : "无特殊前置条件";
  }

  function buildExpectedText(tc) {
    const assertions = Array.isArray(tc.assertions) ? tc.assertions : [];
    if (!assertions.length) return "结果符合预期，无异常抛出";
    return assertions.join("；");
  }

  function renderPointList(items) {
    if (!Array.isArray(items) || !items.length) return "<p class='hint'>（未提供）</p>";
    return (
      "<ul class='structured-case-list'>" +
      items.map((x) => "<li>" + escapeHtml(String(x || "")) + "</li>").join("") +
      "</ul>"
    );
  }

  function renderStructuredCasesPage() {
    const summaryEl = $("#structured_cases_summary");
    const listEl = $("#structured_cases_list");
    if (!summaryEl || !listEl) return;
    if (!lastResult) {
      summaryEl.innerHTML = "<p class='empty'>请先在「代码变更」运行全流程。</p>";
      listEl.innerHTML = "";
      return;
    }
    const tp = lastResult.test_plan || {};
    const cases = Array.isArray(tp.test_cases) ? tp.test_cases : [];
    if (!cases.length) {
      summaryEl.innerHTML = "<p class='empty'>当前结果中没有结构化用例（test_plan.test_cases 为空）。</p>";
      listEl.innerHTML = "";
      return;
    }
    const p0 = cases.filter((c) => c.priority === "P0").length;
    const p1 = cases.filter((c) => c.priority === "P1").length;
    const p2 = cases.filter((c) => c.priority === "P2").length;
    summaryEl.innerHTML =
      "<p>共 <strong>" +
      cases.length +
      "</strong> 条结构化用例：P0 <strong>" +
      p0 +
      "</strong> / P1 <strong>" +
      p1 +
      "</strong> / P2 <strong>" +
      p2 +
      "</strong></p>";

    listEl.innerHTML = cases
      .map(function (tc, i) {
        const stepsText = toChineseScenario(tc);
        const input = tc.input && typeof tc.input === "object" ? tc.input : {};
        const mock = tc.mock && typeof tc.mock === "object" ? tc.mock : {};
        const preconditionItems = [];
        if (Object.keys(input).length) preconditionItems.push("输入条件：" + JSON.stringify(input));
        if (Object.keys(mock).length) preconditionItems.push("Mock 条件：" + JSON.stringify(mock));
        if (!preconditionItems.length) preconditionItems.push("无特殊前置条件");
        const expectedItems = Array.isArray(tc.assertions) && tc.assertions.length ? tc.assertions : [buildExpectedText(tc)];
        const stepItems = [stepsText];
        return (
          "<article class='card structured-case-card'>" +
          "<div class='structured-case-head'><span class='prio-badge'>" +
          escapeHtml(tc.priority || "P2") +
          "</span><strong>" +
          escapeHtml(tc.test_case_id || "用例 #" + (i + 1)) +
          "</strong></div>" +
          "<div class='structured-case-fields'>" +
          "<div class='structured-case-field'><span class='structured-case-label'>用例类型</span><div class='structured-case-value'>" +
          renderPointList([toChineseCaseType(tc.layer)]) +
          "</div></div>" +
          "<div class='structured-case-field'><span class='structured-case-label'>重要程度</span><div class='structured-case-value'>" +
          renderPointList([toChinesePriority(tc.priority)]) +
          "</div></div>" +
          "<div class='structured-case-field'><span class='structured-case-label'>前置条件</span><div class='structured-case-value'>" +
          renderPointList(preconditionItems) +
          "</div></div>" +
          "<div class='structured-case-field'><span class='structured-case-label'>步骤描述</span><div class='structured-case-value'>" +
          renderPointList(stepItems) +
          "</div></div>" +
          "<div class='structured-case-field'><span class='structured-case-label'>预期结果</span><div class='structured-case-value'>" +
          renderPointList(expectedItems) +
          "</div></div>" +
          "</div>" +
          "<p class='hint'>目标：<code>" +
          escapeHtml(tc.target || tc.symbol_id || "—") +
          "</code></p>" +
          "</article>"
        );
      })
      .join("");
  }

  function renderExecutionPage() {
    const tasks = $("#exec_task_list");
    const detail = $("#execution_content");
    if (!tasks || !detail) return;

    if (!lastResult) {
      tasks.innerHTML = "<p class='empty'>暂无任务</p>";
      detail.innerHTML = "<p class='empty'>无</p>";
      return;
    }

    const ev = lastResult.evaluation || {};
    const done = ev.ran ? 100 : 0;
    const ok = ev.exit_code === 0;
    tasks.innerHTML =
      "<div class='task-row'><div><div><strong>全流程 pytest</strong></div><div class='hint'>" +
      (ev.ran ? "已执行" : "未执行") +
      "</div><div class='bar-wrap'><div class='bar' style='width:" +
      done +
      "%'></div></div></div><div>" +
      (ev.ran ? (ok ? "<span class='badge ok'>成功</span>" : "<span class='badge fail'>失败</span>") : "<span class='badge'>跳过</span>") +
      "</div></div>";

    detail.innerHTML =
      "<pre class='json-out' style='max-height:16rem'>" + escapeHtml(JSON.stringify(ev, null, 2)) + "</pre>";
  }

  function statusBadgeClass(st) {
    const m = { passed: "ok", failed: "fail", error: "err", skipped: "skip" };
    return m[String(st || "").toLowerCase()] || "";
  }

  function statusLabelZh(st) {
    const m = { passed: "通过", failed: "失败", error: "错误", skipped: "跳过" };
    return m[String(st || "").toLowerCase()] || String(st || "—");
  }

  function renderRunAnalysisPage() {
    const meta = $("#run_analysis_meta");
    const summary = $("#run_analysis_summary");
    const wrap = $("#run_analysis_table_wrap");
    if (!meta || !summary || !wrap) return;

    if (!lastResult) {
      meta.innerHTML = "";
      summary.innerHTML = "<p class='empty'>请先在「代码变更」运行全流程。</p>";
      wrap.innerHTML = "";
      return;
    }

    const ev = lastResult.evaluation || {};
    if (!ev.ran) {
      meta.innerHTML = "";
      summary.innerHTML = "<p class='empty'>本次未执行 pytest。请在「代码变更」勾选执行测试后重新运行。</p>";
      wrap.innerHTML = "";
      return;
    }

    const sum = ev.pytest_summary || {};
    const cases = Array.isArray(ev.pytest_cases) ? ev.pytest_cases : [];
    const ok = ev.exit_code === 0;

    meta.innerHTML =
      "<p class='run-analysis-meta-line'><span class='badge " +
      (ok ? "ok" : "fail") +
      "'>" +
      (ok ? "pytest 通过" : "pytest 未通过") +
      "</span> · 退出码 <code>" +
      escapeHtml(String(ev.exit_code ?? "—")) +
      "</code>" +
      (ev.report_dir
        ? " · 本地报告目录 <code class='mono-inline'>" + escapeHtml(ev.report_dir) + "</code>"
        : "") +
      "</p>";

    summary.innerHTML =
      "<div class='ra-stat'><span class='ra-stat-label'>用例数</span><strong>" +
      escapeHtml(String(sum.tests ?? "—")) +
      "</strong></div>" +
      "<div class='ra-stat'><span class='ra-stat-label'>失败</span><strong>" +
      escapeHtml(String(sum.failures ?? "—")) +
      "</strong></div>" +
      "<div class='ra-stat'><span class='ra-stat-label'>错误</span><strong>" +
      escapeHtml(String(sum.errors ?? "—")) +
      "</strong></div>" +
      "<div class='ra-stat'><span class='ra-stat-label'>跳过</span><strong>" +
      escapeHtml(String(sum.skipped ?? "—")) +
      "</strong></div>" +
      "<div class='ra-stat'><span class='ra-stat-label'>耗时(s)</span><strong>" +
      escapeHtml(String(sum.time ?? "—")) +
      "</strong></div>";

    if (!cases.length) {
      wrap.innerHTML =
        "<p class='empty' style='margin:0 0 0.5rem'>未解析到逐条用例（<code>evaluation.pytest_cases</code> 为空）。</p>" +
        "<p class='hint'>常见原因：① 环境变量 <code>MUTIAGENT_DISABLE_TEST_REPORT=1</code> 关闭了 junit 落盘；② pytest 在收集阶段即失败未产出用例；③ 仅刷新了页面且上次完整结果因体积过大未写入浏览器会话存储（可重新跑一次全流程）。</p>" +
        "<p class='hint'>若已生成报告，可在上方「本地报告目录」打开 <code>report.html</code> 或同目录 <code>junit.xml</code> 查看。</p>";
      return;
    }

    const head =
      "<table class='run-analysis-table'><thead><tr>" +
      "<th>状态</th><th>类名</th><th>用例</th><th>耗时(s)</th><th>详情</th>" +
      "</tr></thead><tbody>";
    const rows = cases
      .map(function (c) {
        const st = (c.status || "").toLowerCase();
        const bc = statusBadgeClass(st);
        const detail = (c.detail || "").trim();
        const detailCell = detail
          ? "<details class='ra-detail'><summary>展开</summary><pre class='ra-detail-pre'>" +
            escapeHtml(detail) +
            "</pre></details>"
          : "—";
        const badgeCls = bc ? " badge " + bc : " badge";
        return (
          "<tr class='ra-row ra-" +
          escapeHtml(bc || "na") +
          "'><td><span class='" +
          escapeHtml(badgeCls.trim()) +
          "'>" +
          escapeHtml(statusLabelZh(c.status)) +
          "</span></td><td class='mono ra-mono'>" +
          escapeHtml(c.classname || "") +
          "</td><td class='mono ra-mono'>" +
          escapeHtml(c.name || "") +
          "</td><td>" +
          escapeHtml(String(c.time ?? "")) +
          "</td><td>" +
          detailCell +
          "</td></tr>"
        );
      })
      .join("");
    wrap.innerHTML = head + rows + "</tbody></table>";
  }

  function renderReportsPage() {
    const art = $("#reports_article");
    const extra = $("#reports_extra");
    if (!art) return;
    if (!lastResult) {
      art.innerHTML = "<p class='empty'>暂无报告数据。</p>";
      if (extra) extra.innerHTML = "";
      return;
    }

    const ev = lastResult.evaluation || {};
    const cov = ev.coverage != null ? (ev.coverage * 100).toFixed(1) + "%" : "未解析";
    const rc = countHighRisk(lastResult);
    const fc = (lastResult.changed_files || []).length;

    art.innerHTML =
      "<h3>变更影响总结</h3><p>本次涉及 <strong>" +
      fc +
      "</strong> 个变更文件；语义层面标记的高风险单元约 <strong>" +
      rc +
      "</strong> 个（来自 top_risks / P0 目录）。</p>" +
      "<h3>测试与覆盖</h3><p>pytest 是否执行：<strong>" +
      (ev.ran ? "是" : "否") +
      "</strong>；解析覆盖率：<strong>" +
      cov +
      "</strong>；退出码：<strong>" +
      (ev.exit_code ?? "—") +
      "</strong>。</p>" +
      "<h3>风险评估</h3><ul><li>优先关注 P0 语义单元与 API/异常相关策略</li><li>结合「影响分析」图谱做人工复核</li></ul>";

    if (extra) {
      extra.innerHTML = "";
      if (ev.report_dir) {
        extra.innerHTML =
          "<h2>本地 HTML 报告路径</h2><pre class='json-out'>" + escapeHtml(ev.report_dir) + "</pre>";
      }
    }
  }

  function renderProjectsGrid() {
    $("#project_detail_wrap").classList.add("hidden");
    $("#projects_main").classList.remove("hidden");
    const grid = $("#projects_grid");
    const projects = loadProjects();
    if (!grid) return;
    if (!projects.length) {
      grid.innerHTML = "<p class='empty'>暂无项目，请在上方添加。</p>";
      return;
    }
    grid.innerHTML = projects
      .map(
        (p, i) =>
          "<div class='project-card' data-i='" +
          i +
          "'><h3>" +
          escapeHtml(p.name || "未命名") +
          "</h3><div class='path'>" +
          escapeHtml(p.path || "") +
          "</div><div class='meta'>分支 " +
          escapeHtml(p.branch || "—") +
          " · CI " +
          escapeHtml(p.ci || "未绑定") +
          "</div><div class='project-card-actions'><button type='button' class='btn btn-sm btn-ghost proj-del' data-i='" +
          i +
          "'>删除</button></div></div>"
      )
      .join("");

    grid.querySelectorAll(".project-card").forEach((c) => {
      c.addEventListener("click", () => showProjectDetail(Number(c.dataset.i)));
    });
    grid.querySelectorAll(".proj-del").forEach((btn) => {
      btn.addEventListener("click", (ev) => {
        ev.stopPropagation();
        const i = Number(btn.dataset.i);
        const list = loadProjects();
        const p = list[i];
        if (!p) return;
        if (!window.confirm("确认删除项目「" + (p.name || p.path || "未命名") + "」吗？")) return;
        list.splice(i, 1);
        saveProjects(list);
        refreshTopProjectSelect();
        renderProjectsGrid();
      });
    });
  }

  function showProjectDetail(i) {
    currentProjectDetail = i;
    const p = loadProjects()[i];
    if (!p) return;
    $("#projects_main").classList.add("hidden");
    $("#project_detail_wrap").classList.remove("hidden");
    $("#project_detail_title").textContent = p.name || "项目";
    $("#project_detail_body").innerHTML =
      "<p><strong>路径</strong><br/><code>" +
      escapeHtml(p.path) +
      "</code></p><p><strong>默认分支</strong> " +
      escapeHtml(p.branch || "—") +
      "</p><p><strong>CI/CD</strong> " +
      escapeHtml(p.ci || "（前端备注，未对接流水线）") +
      "</p><div class='row'><button type='button' class='btn btn-primary' id='proj_use'>选用此仓库</button><button type='button' class='btn btn-ghost' id='proj_del_cur'>删除</button></div>" +
      "<hr class='db-sep'/><h3 class='block-title'>历史生成用例（数据库）</h3>" +
      "<div id='proj_db_runs'><p class='hint'>加载中…</p></div>";

    $("#proj_use").onclick = () => {
      $("#top_project").value = String(i);
      applyTopProject();
      switchView("changes");
    };
    $("#proj_del_cur").onclick = () => {
      const list = loadProjects();
      list.splice(i, 1);
      saveProjects(list);
      refreshTopProjectSelect();
      $("#project_detail_back").click();
    };
    fetchProjectRunsFromDb(p.path)
      .then((data) => renderProjectRuns($("#proj_db_runs"), data))
      .catch((err) => {
        const host = $("#proj_db_runs");
        if (host) host.innerHTML = "<p class='empty'>" + escapeHtml(err.message || String(err)) + "</p>";
      });
  }

  function renderChangesTable() {
    const tb = $("#changes_tbody");
    if (!tb) return;
    const hist = loadHistory().slice().reverse();
    if (!hist.length) {
      tb.innerHTML = "<tr><td colspan='7' class='empty'>暂无记录</td></tr>";
      return;
    }
    tb.innerHTML = hist
      .map(
        (h) =>
          "<tr><td>" +
          escapeHtml(h.at.slice(0, 19).replace("T", " ")) +
          "</td><td>" +
          escapeHtml(h.author || "—") +
          "</td><td style='max-width:12rem;word-break:break-all'>" +
          escapeHtml(h.repo_path || "") +
          "</td><td>" +
          h.changed_count +
          "</td><td>" +
          h.high_risk_count +
          "</td><td>" +
          (h.exit_code != null ? h.exit_code : "—") +
          "</td><td><button type='button' class='btn btn-sm btn-ghost ch-detail' data-id='" +
          escapeHtml(h.id) +
          "'>详情</button></td></tr>"
      )
      .join("");

    tb.querySelectorAll(".ch-detail").forEach((btn) => {
      btn.addEventListener("click", () => showChangeDetail(btn.dataset.id));
    });
  }

  function showChangeDetail(id) {
    const activeTab = $(".tab-inline.active");
    changesReturnTab = activeTab && activeTab.dataset.chtab ? activeTab.dataset.chtab : "timeline";
    let snap = null;
    try {
      snap = JSON.parse(sessionStorage.getItem(SNAP + id) || "null");
    } catch {
      snap = null;
    }
    $("#changes_panel_run").classList.add("hidden");
    $("#changes_panel_timeline").classList.add("hidden");
    $("#changes_tabs").classList.add("hidden");
    $("#changes_panel_detail").classList.remove("hidden");

    if (!snap || !snap.response) {
      $("#changes_detail_title").textContent = "记录不可用";
      $("#changes_detail_meta").innerHTML = "<p class='empty'>快照已过期或未保存 diff</p>";
      $("#changes_detail_diff").textContent = "";
      $("#changes_detail_entities").innerHTML = "";
      return;
    }

    const data = snap.response;
    $("#changes_detail_title").textContent = "分析批次 " + id.slice(-6);
    $("#changes_detail_meta").innerHTML =
      "<p>仓库：<code>" +
      escapeHtml(snap.client_repo || "") +
      "</code> · " +
      escapeHtml(snap.at || "") +
      "</p>";

    $("#changes_detail_diff").textContent = snap.client_diff || "（本次未保存 diff 文本）";

    const ents = [];
    (data.change_analysis || []).forEach((f) => {
      (f.changes || []).forEach((c) => {
        ents.push(
          "<span class='entity-chip'>" +
            escapeHtml(c.entity || "") +
            " <span class='muted'>(" +
            escapeHtml(c.type || "") +
            ")</span></span>"
        );
      });
    });
    $("#changes_detail_entities").innerHTML = ents.length
      ? ents.join("")
      : "<p class='empty'>无实体</p>";
  }

  function hideChangeDetail() {
    $("#changes_panel_detail").classList.add("hidden");
    $("#changes_tabs").classList.remove("hidden");
    $$(".tab-inline").forEach((t) => t.classList.toggle("active", t.dataset.chtab === changesReturnTab));
    $("#changes_panel_run").classList.toggle("hidden", changesReturnTab !== "run");
    $("#changes_panel_timeline").classList.toggle("hidden", changesReturnTab !== "timeline");
  }

  /* —— AI 助理 —— */
  const assistantMessages = [];

  function buildAssistantContext() {
    const repoEl = $("#repo_path");
    const repo = repoEl ? repoEl.value.trim() : "";
    const base = {
      repo_path: repo || null,
      user_rules_excerpt: (localStorage.getItem(LS_RULES) || "").slice(0, 600),
    };
    if (!lastResult) {
      return Object.assign({ has_result: false }, base);
    }
    const ev = lastResult.evaluation || {};
    return Object.assign(
      {
        has_result: true,
        changed_files: lastResult.changed_files || [],
        top_risks: (lastResult.top_risks || []).slice(0, 24),
        impact_summary: (lastResult.impact_graph || []).map((f) => ({
          file: f.file,
          symbol_count: (f.symbols || []).length,
        })),
        impact_test_plan_excerpt: (lastResult.impact_test_plan || []).slice(0, 15),
        evaluation: {
          ran: ev.ran,
          exit_code: ev.exit_code,
          report_dir: ev.report_dir || null,
          coverage: ev.coverage,
        },
        generated_test_paths: (lastResult.generated_tests || []).map((t) => t.path),
        generated_preview: (lastResult.generated_tests || []).slice(0, 2).map((t) => ({
          path: t.path,
          excerpt: (t.content || "").slice(0, 1500),
        })),
      },
      base
    );
  }

  function appendAssistantBubble(role, text, isErr) {
    const box = $("#assistant_messages");
    if (!box) return;
    const div = document.createElement("div");
    div.className = "assistant-bubble " + role + (isErr ? " err" : "");
    div.textContent = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }

  async function sendAssistantMessage(text) {
    const q = (text || "").trim();
    if (!q) return;
    assistantMessages.push({ role: "user", content: q });
    appendAssistantBubble("user", q);
    const inp = $("#assistant_input");
    if (inp) inp.value = "";
    const sendBtn = $("#assistant_send");
    const note = $("#assistant_note");
    if (sendBtn) sendBtn.disabled = true;
    if (note) note.textContent = "处理中…";

    try {
      const r = await fetch("/api/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: assistantMessages.slice(-24),
          context: buildAssistantContext(),
        }),
      });
      const raw = await r.text();
      let data;
      try {
        data = JSON.parse(raw);
      } catch {
        appendAssistantBubble("bot", "无法解析响应：" + raw.slice(0, 500), true);
        assistantMessages.pop();
        if (note) note.textContent = "";
        return;
      }
      if (!r.ok) {
        let detail = raw;
        if (data.detail !== undefined) {
          detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
        }
        appendAssistantBubble("bot", detail, true);
        assistantMessages.pop();
        if (note) note.textContent = "HTTP " + r.status;
        return;
      }
      const reply = data.reply || "(空回复)";
      assistantMessages.push({ role: "assistant", content: reply });
      appendAssistantBubble("bot", reply);
      if (note) {
        note.textContent = data.note || (data.used_llm ? "由 LLM 回答" : "规则助理");
      }
    } catch (e) {
      appendAssistantBubble("bot", "网络错误：" + (e.message || String(e)), true);
      assistantMessages.pop();
      if (note) note.textContent = "";
    } finally {
      if (sendBtn) sendBtn.disabled = false;
    }
  }

  function toggleAssistantPanel(force) {
    const p = $("#assistant_panel");
    if (!p) return;
    let show;
    if (force === true) show = true;
    else if (force === false) show = false;
    else show = p.classList.contains("hidden");
    p.classList.toggle("hidden", !show);
    p.setAttribute("aria-hidden", show ? "false" : "true");
    const fab = $("#assistant_fab");
    if (fab) fab.setAttribute("aria-expanded", show ? "true" : "false");
  }

  /* Events */
  $$(".nav-item").forEach((btn) => btn.addEventListener("click", () => switchView(btn.dataset.view)));

  $("#top_project").addEventListener("change", applyTopProject);

  $("#dash_go_changes").addEventListener("click", () => switchView("changes"));
  $("#dash_go_impact").addEventListener("click", () => switchView("impact"));
  $("#dash_go_cases").addEventListener("click", () => switchView("cases"));
  $("#dash_refresh_health").addEventListener("click", checkHealth);

  $("#proj_add").addEventListener("click", () => {
    const name = $("#proj_name").value.trim();
    const path = $("#proj_path").value.trim();
    const branch = $("#proj_branch").value.trim();
    const ci = $("#proj_ci").value.trim();
    if (!path) return alert("填写路径");
    const list = loadProjects();
    list.push({ name: name || path.split("/").filter(Boolean).pop(), path, branch, ci });
    saveProjects(list);
    $("#proj_name").value = "";
    $("#proj_path").value = "";
    $("#proj_branch").value = "";
    $("#proj_ci").value = "";
    refreshTopProjectSelect();
    renderProjectsGrid();
  });

  $("#project_detail_back").addEventListener("click", () => {
    $("#project_detail_wrap").classList.add("hidden");
    $("#projects_main").classList.remove("hidden");
  });

  $$(".tab-inline").forEach((t) => {
    t.addEventListener("click", () => {
      $$(".tab-inline").forEach((x) => x.classList.remove("active"));
      t.classList.add("active");
      const tab = t.dataset.chtab;
      $("#changes_panel_run").classList.toggle("hidden", tab !== "run");
      $("#changes_panel_timeline").classList.toggle("hidden", tab !== "timeline");
      if (tab === "timeline") renderChangesTable();
    });
  });

  $("#changes_detail_back").addEventListener("click", hideChangeDetail);

  $("#form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const repo = $("#repo_path").value.trim();
    const diff = $("#diff").value;
    if (!repo) {
      setStatus("填写仓库路径", "error");
      return;
    }
    if (!diff.trim()) {
      setStatus("粘贴 diff", "error");
      return;
    }
    $("#submit").disabled = true;
    setStatus("运行中，请稍候…", "running");
    setWorkflowProgress(true, { current: 0, total: 11, label: "排队启动" });
    try {
      let data;
      try {
        data = await readNdjsonWorkflow(
          repo,
          diff,
          $("#run_eval").checked,
          $("#auto_venv").checked,
          $("#auto_install_python").checked
        );
      } catch (streamErr) {
        setWorkflowProgress(false);
        setStatus(streamErr.message || String(streamErr), "error");
        return;
      }

      const author = localStorage.getItem(LS_USER) || "本地用户";
      const id = uid();
      const entry = {
        id,
        at: new Date().toISOString(),
        author,
        repo_path: repo,
        branch: $("#top_branch").value.trim(),
        changed_count: (data.changed_files || []).length,
        high_risk_count: countHighRisk(data),
        coverage: data.evaluation && data.evaluation.coverage,
        exit_code: data.evaluation ? data.evaluation.exit_code : null,
        run_eval: $("#run_eval").checked,
        auto_venv: $("#auto_venv").checked,
        auto_install_python: $("#auto_install_python").checked,
      };
      const snapshot = {
        response: data,
        client_diff: diff,
        client_repo: repo,
        at: entry.at,
        branch: entry.branch,
      };
      lastSnapshot = snapshot;
      recordHistory(entry, snapshot);
      saveLastResult(data, snapshot);
      strategyOrder = [];
      setStatus("完成", "");
      setWorkflowProgress(true, { current: 11, total: 11, label: "已完成" });
      setTimeout(function () {
        setWorkflowProgress(false);
      }, 900);
    } catch (err) {
      setWorkflowProgress(false);
      setStatus(err.message || String(err), "error");
    } finally {
      $("#submit").disabled = false;
    }
  });

  $("#load_sample").addEventListener("click", async () => {
    try {
      const r = await fetch("sample.diff");
      $("#diff").value = await r.text();
      setStatus("已加载示例", "");
    } catch (e) {
      setStatus(e.message, "error");
    }
  });

  $("#clear_result").addEventListener("click", () => {
    lastResult = null;
    lastSnapshot = null;
    strategyOrder = [];
    selectedCaseIndex = -1;
    sessionStorage.removeItem(SS_LAST);
    try {
      sessionStorage.removeItem(SS_EVAL_LITE);
    } catch {
      /* */
    }
    $("#fab_raw").disabled = true;
    $("#raw_json").textContent = "";
    renderChangesSummary(null);
    refreshDashboard();
    renderImpactPage();
    renderTestingPage();
    renderCasesPage();
    renderExecutionPage();
    renderRunAnalysisPage();
    renderReportsPage();
    setStatus("已清空会话缓存", "");
  });

  $("#run_eval").addEventListener("change", () => {
    localStorage.setItem(LS_DEFAULT_EVAL, $("#run_eval").checked ? "1" : "0");
  });
  const autoVenvEl = $("#auto_venv");
  const autoInstallPythonEl = $("#auto_install_python");
  if (autoVenvEl) {
    autoVenvEl.addEventListener("change", () => {
      localStorage.setItem(LS_DEFAULT_AUTO_VENV, autoVenvEl.checked ? "1" : "0");
    });
  }
  if (autoInstallPythonEl) {
    autoInstallPythonEl.addEventListener("change", () => {
      localStorage.setItem(LS_DEFAULT_AUTO_INSTALL_PY, autoInstallPythonEl.checked ? "1" : "0");
    });
  }

  $("#set_default_run_eval").addEventListener("change", () => {
    localStorage.setItem(LS_DEFAULT_EVAL, $("#set_default_run_eval").checked ? "1" : "0");
    $("#run_eval").checked = $("#set_default_run_eval").checked;
  });

  $("#set_save_user").addEventListener("click", () => {
    const v = $("#set_user_label").value.trim() || "本地用户";
    localStorage.setItem(LS_USER, v);
    $("#top_user").textContent = v;
  });

  $("#set_rules_save").addEventListener("click", () => {
    localStorage.setItem(LS_RULES, $("#set_rules_draft").value);
    alert("已保存到本地");
  });

  $("#set_clear_cache").addEventListener("click", () => $("#clear_result").click());

  $("#testing_go_changes").addEventListener("click", () => switchView("changes"));
  $("#testing_reset_prio").addEventListener("click", () => {
    strategyOrder = [];
    renderTestingPage();
  });

  $("#impact_filter_p0").addEventListener("change", renderImpactPage);
  $("#impact_filter_sym").addEventListener("change", renderImpactPage);
  $("#impact_graph_filter_p0").addEventListener("change", renderImpactGraphPage);
  $("#impact_graph_filter_sym").addEventListener("change", renderImpactGraphPage);

  $("#case_export_one").addEventListener("click", () => {
    const tests = (lastResult && lastResult.generated_tests) || [];
    const t = tests[selectedCaseIndex];
    if (!t) return alert("先选择用例");
    downloadJson(t.path.replace(/\//g, "_") + ".json", t);
  });

  $("#case_export_all").addEventListener("click", () => {
    if (!lastResult || !lastResult.generated_tests) return;
    downloadJson("generated_tests.json", lastResult.generated_tests);
  });

  function downloadJson(name, obj) {
    const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  $("#report_export_json").addEventListener("click", () => {
    if (!lastResult) return alert("无数据");
    const ev = lastResult.evaluation || {};
    const report = {
      generated_at: new Date().toISOString(),
      summary: {
        changed_files: (lastResult.changed_files || []).length,
        high_risk_count: countHighRisk(lastResult),
        coverage: ev.coverage,
        exit_code: ev.exit_code,
        report_dir: ev.report_dir,
      },
      top_risks: lastResult.top_risks || [],
      change_analysis: lastResult.change_analysis || [],
    };
    downloadJson("mutiagent_report.json", report);
  });

  $("#report_print").addEventListener("click", () => window.print());

  function openDrawer(open) {
    const d = $("#raw_drawer");
    d.classList.toggle("hidden", !open);
    d.setAttribute("aria-hidden", open ? "false" : "true");
  }

  $("#fab_raw").addEventListener("click", () => {
    if (lastResult) $("#raw_json").textContent = JSON.stringify(lastResult, null, 2);
    openDrawer(true);
  });
  $("#raw_drawer_btn").addEventListener("click", () => openDrawer(false));
  $("#raw_drawer_close").addEventListener("click", () => openDrawer(false));

  const afab = $("#assistant_fab");
  if (afab) afab.addEventListener("click", () => toggleAssistantPanel());
  const aclose = $("#assistant_close");
  if (aclose) aclose.addEventListener("click", () => toggleAssistantPanel(false));
  const asend = $("#assistant_send");
  if (asend) asend.addEventListener("click", () => sendAssistantMessage($("#assistant_input").value));
  const ainp = $("#assistant_input");
  if (ainp) {
    ainp.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && !ev.shiftKey) {
        ev.preventDefault();
        sendAssistantMessage(ainp.value);
      }
    });
  }
  const aquick = $("#assistant_quick");
  if (aquick) {
    aquick.addEventListener("click", (ev) => {
      const btn = ev.target.closest(".chip-btn");
      if (!btn || !btn.dataset.q) return;
      sendAssistantMessage(btn.dataset.q);
    });
  }

  /* init */
  try {
    const old = localStorage.getItem("mutiagent_projects_v1");
    if (old && !localStorage.getItem(LS_PROJECTS)) {
      localStorage.setItem(LS_PROJECTS, old);
    }
  } catch {
    /* */
  }

  loadLastFromSession();
  if (lastResult) {
    renderExecutionPage();
    renderRunAnalysisPage();
    renderReportsPage();
  }
  refreshTopProjectSelect();
  const u = localStorage.getItem(LS_USER);
  if (u) {
    $("#set_user_label").value = u;
    $("#top_user").textContent = u;
  }
  const evalOn = localStorage.getItem(LS_DEFAULT_EVAL) !== "0";
  $("#run_eval").checked = evalOn;
  const sde = $("#set_default_run_eval");
  if (sde) sde.checked = evalOn;
  const autoVenvOn = localStorage.getItem(LS_DEFAULT_AUTO_VENV) === "1";
  if (autoVenvEl) autoVenvEl.checked = autoVenvOn;
  const autoInstallPythonOn = localStorage.getItem(LS_DEFAULT_AUTO_INSTALL_PY) === "1";
  if (autoInstallPythonEl) autoInstallPythonEl.checked = autoInstallPythonOn;
  $("#set_rules_draft").value = localStorage.getItem(LS_RULES) || "";

  renderChangesSummary(lastResult);
  renderChangesTable();
  checkHealth();
  $("#fab_raw").disabled = !lastResult;
  switchView("dashboard");

  window.addEventListener("beforeunload", () => {
    try {
      destroyCharts();
    } catch {
      /* */
    }
  });
})();
