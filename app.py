# -*- coding: utf-8 -*-
"""
智控成本 · 数创价值 —— 制造企业全流程成本管理虚拟仿真实训（Streamlit 交互版）
28 步创始人日记体 × 智能成本控制指挥中心 UI  ·  V6.0
V6.0：集成 streamlit-facade 主题化（霓虹绿深色设计系统）+ Design Tokens + 顶栏徽章 + 底部 28 步进度带
依据《智控成本数创价值·设计方案 V5.0》构建；2026 中国仿真创新应用大赛·仿真教学应用赛道
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import facade  # streamlit-facade：shadcn 风格、可主题化组件库（V6.0 引入）

APP_VERSION = "V6.1"  # 版本号：每次升级在此递增，并同步界面与提交信息

st.set_page_config(page_title="智控成本·数创价值", page_icon="◈", layout="wide",
                   initial_sidebar_state="expanded")

# ---------------- V6.0：facade 全局主题（霓虹绿深色指挥中心） ----------------
facade.theme.apply(preset="carbon-dark", base="dark",
                   primary="#00FF9C", primary_foreground="#05070A",
                   background="#05070A", foreground="#E6F2E9",
                   muted="#0A0E12", muted_foreground="#8FB89B",
                   border="#1E3A28", destructive="#FF3B30",
                   chrome_background="#070B0F", chrome_foreground="#E6F2E9",
                   chrome_border="#00FF9C33",
                   radius="md", font_sans="Microsoft YaHei, PingFang SC, sans-serif")

# ---------------- 指挥中心主题 CSS（Design Tokens 单一来源） ----------------
st.markdown("""
<style>
  :root {
    --bg-deep:#05070A; --bg-panel:#0A0E12; --bg-elev:#10161A;
    --neon:#00FF9C; --accent:#38BDF8; --warn:#FFB300; --alert:#FF3B30;
    --text:#E6F2E9; --text-dim:#8FB89B; --line:#00FF9C33; --grid:#00FF9C0A;
    --radius:10px;
  }
  .stApp { background: var(--bg-deep); color: var(--text); }
  /* 指挥中心网格底纹 */
  .stApp { background-image: linear-gradient(var(--grid) 1px, transparent 1px),
                             linear-gradient(90deg, var(--grid) 1px, transparent 1px);
            background-size: 28px 28px; }
  html, body, [class*="css"] { font-family: "Microsoft YaHei", "PingFang SC", sans-serif; }
  .cmd-header { background: linear-gradient(180deg,var(--bg-panel),var(--bg-deep));
                border:1px solid var(--line); border-radius:var(--radius);
                padding:14px 20px; margin-bottom:6px;
                box-shadow:0 0 18px #00FF9C22 inset; }
  .cmd-title { font-size:26px; font-weight:900; color:var(--neon); letter-spacing:2px; }
  .cmd-sub { font-size:13px; color:var(--text-dim); margin-top:2px; }
  .diary-line { border-left:3px solid var(--warn); background:var(--bg-panel); padding:10px 14px;
                border-radius:0 8px 8px 0; margin:8px 0; }
  .diary-line .who { color:var(--warn); font-weight:700; }
  .diary-line .say { color:var(--text); }
  .ok { color:var(--neon); } .warn { color:var(--warn); } .bad { color:var(--alert); }
  /* 底部 28 步进度带 */
  .stepband { display:flex; gap:4px; flex-wrap:wrap; margin:12px 0 4px;
              border:1px solid var(--line); border-radius:8px; background:var(--bg-panel);
              padding:8px 12px; align-items:center; }
  .stepband .seg { width:16px; height:10px; border-radius:2px; background:#1E3A28;
                   border:1px solid #3A5A44; }
  .stepband .seg.done { background:var(--neon); border-color:var(--neon); }
  .stepband .seg.now { background:var(--neon); border-color:var(--neon);
                       animation:pulse 1.2s infinite; }
  .stepband .cap { font-size:11px; color:var(--text-dim); margin-left:6px; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
  /* 表格统一深色 */
  [data-testid="stTable"], [data-testid="stDataFrame"] { background:var(--bg-panel); }
  div[data-testid="stSidebar"] { background:#070B0F; border-right:1px solid var(--line); }
  /* ===== 纯黑指挥中心封面 / 顶栏 HUD ===== */
  .hud-wrap { position:relative; padding:24px 20px; margin:6px 0 10px; border-radius:14px;
              background:radial-gradient(120% 120% at 50% 0%, #0A1210 0%, #05070A 55%, #05070A 100%);
              border:1px solid #00FF9C44; overflow:hidden; }
  .hud-wrap::before { content:""; position:absolute; inset:0;
              background:repeating-linear-gradient(180deg, rgba(0,255,156,0.05) 0 1px, transparent 1px 4px);
              pointer-events:none; }
  .hud-wrap .scan { position:absolute; left:0; right:0; top:-4px; height:2px;
              background:linear-gradient(90deg, transparent, #00FF9C, transparent);
              animation:scanmove 5s linear infinite; opacity:.85; }
  @keyframes scanmove { 0%,60%{transform:translateY(0)} 80%{transform:translateY(150px)} 100%{transform:translateY(0)} }
  .hud-wrap .hud-c { position:absolute; width:16px; height:16px; border:2px solid #00FF9C; }
  .hud-wrap .hud-c.tl { top:9px; left:9px; border-right:none; border-bottom:none; border-top-left-radius:6px; }
  .hud-wrap .hud-c.tr { top:9px; right:9px; border-left:none; border-bottom:none; border-top-right-radius:6px; }
  .hud-wrap .hud-c.bl { bottom:9px; left:9px; border-right:none; border-top:none; border-bottom-left-radius:6px; }
  .hud-wrap .hud-c.br { bottom:9px; right:9px; border-left:none; border-top:none; border-bottom-right-radius:6px; }
  .hud-inner { position:relative; z-index:1; text-align:center; }
  .brand-en { font-size:11px; letter-spacing:5px; color:#4E7A63; text-transform:uppercase; }
  .brand-title { font-size:32px; font-weight:900; color:#00FF9C; letter-spacing:3px;
                 text-shadow:0 0 14px rgba(0,255,156,.6), 0 0 42px rgba(0,255,156,.22);
                 margin:4px 0 6px; line-height:1.3; }
  .brand-title .ver { font-size:12px; letter-spacing:1px; border:1px solid #00FF9C66; border-radius:8px;
                      padding:1px 8px; vertical-align:middle; color:#8FB89B; text-shadow:none; }
  .brand-sub { font-size:13px; color:#8FB89B; letter-spacing:1px; }
  .brand-line { display:inline-flex; align-items:center; gap:10px; margin:10px auto 0;
                color:#4E7A63; font-size:11px; letter-spacing:1px; }
  .brand-line::before, .brand-line::after { content:""; width:60px; height:1px;
                background:linear-gradient(90deg,transparent,#00FF9C55,transparent); }
  .status-dot { display:inline-block; width:8px; height:8px; border-radius:50%;
                background:#FF3B30; margin-right:7px; animation:blink 1.6s infinite; }
  .status-dot.green { background:#00FF9C; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }
  .cover-card { border:1px solid #00FF9C44; border-radius:12px; background:rgba(7,11,15,.85);
                padding:14px 18px; margin-bottom:10px; box-shadow:0 0 24px rgba(0,255,156,.12); }
</style>
""", unsafe_allow_html=True)

# ---------------- 学生登录（学号 / 班级 / 姓名） ----------------
if "student" not in st.session_state:
    st.session_state.student = None

if st.session_state.student is None:
    st.markdown("""
<div class="hud-wrap">
  <span class="scan"></span>
  <span class="hud-c tl"></span><span class="hud-c tr"></span>
  <span class="hud-c bl"></span><span class="hud-c br"></span>
  <div class="hud-inner">
    <div class="brand-en">Smart Cost Command Center</div>
    <div class="brand-title">◈ 智控成本 · 数创价值</div>
    <div class="brand-sub">制造企业全流程成本管理虚拟仿真实训 · 28 步创始人日记体</div>
    <div class="brand-line">身份进阶 · 成本会计 → 车间核算员 → 财务经理 → 管理会计师</div>
  </div>
</div>
<div class="cover-card">
  <span class="status-dot red"></span><span style="color:#8FB89B;font-size:13px;">系统在线 · 请先登录（学号 / 班级 / 姓名）后进入实训</span>
</div>
""", unsafe_allow_html=True)
    with st.form("login_form"):
        _sid = st.text_input("学号")
        _cls = st.text_input("班级")
        _name = st.text_input("姓名")
        _ok = st.form_submit_button("进入实训")
    if _ok:
        if _sid.strip() and _cls.strip() and _name.strip():
            st.session_state.student = {"学号": _sid.strip(), "班级": _cls.strip(), "姓名": _name.strip()}
            st.rerun()
        else:
            st.error("请完整填写学号、班级、姓名。")
    st.stop()

# ---------------- 角色/知识/日记表 ----------------
# 身份进阶（角色层）：成本会计→车间核算员→财务经理→管理会计师（任务驱动声音=创始人/投资人/供应商/质检/客户/监管…）
DIARY = {
    1:  ("投资人", "第 1 天，投资人说：“工厂要起盘了，你先当成本会计，把账算明白，我才追加资金。”"),
    2:  ("供应商", "第 2 天，供应商说：“材料报价就这一张，单价和采购量你定，签了我就发货。”"),
    3:  ("仓管",  "第 3 天，仓管说：“材料到库了，点货入库，账面直接材料成本我按你录的记。”"),
    4:  ("车间主任", "第 4 天，车间主任说：“领料开工。排产怎么配，完工和在产你说了算。”"),
    5:  ("HR",   "第 5 天，HR 说：“车间要排班，工时和单价你拍板，直接人工成本就看你这一手。”"),
    6:  ("财务",  "第 6 天，财务说：“制造费用要拆变动和固定，归集口径错了后面全错。”"),
    7:  ("成本会计", "第 7 天，成本会计说：“费用往各产品/部门分摊，你选分摊动因。”"),
    8:  ("辅助车间", "第 8 天，辅助车间说：“动力/机修费用要交互分配，一次交互还是直接分配？”"),
    9:  ("车间核算员", "第 9 天，车间核算员说：“约当产量怎么算？材料完工程度、加工完工程度都要你定。”"),
    10: ("核算员", "第 10 天，核算员说：“品种法结账，本月成本要算平，勾稽关系不能断。”"),
    11: ("财务经理", "第 11 天，财务经理说：“分批法：按订单归集还是按批次？你设计批次。”"),
    12: ("财务经理", "第 12 天，财务经理说：“分步法：逐步结转还是平行结转？成本还原你来做。”"),
    13: ("财务经理", "第 13 天，财务经理说：“变动成本法与完全成本法，利润差多少？你切换对比。”"),
    14: ("财务经理", "第 14 天，财务经理说：“量本利：售价调多少、保本点在哪，你来测算。”"),
    15: ("销售总监", "第 15 天，销售总监说：“产销情境怎么定？满产满销还是压产累库存？”"),
    16: ("财务经理", "第 16 天，财务经理说：“存货计价：先进先出、加权平均还是移动加权？口径影响成本。”"),
    17: ("管理会计师", "第 17 天，管理会计师说：“设标准成本，作为差异与绩效的基准线。”"),
    18: ("管理会计师", "第 18 天，管理会计师说：“价格差异/数量差异，责任在采购部还是生产部？”"),
    19: ("管理会计师", "第 19 天，管理会计师说：“作业成本法：建成本库、选成本动因，摊出更真实的单位成本。”"),
    20: ("管理会计师", "第 20 天，管理会计师说：“动因博弈：你选动因，成本就向不同产品转移。”"),
    21: ("HR",   "第 21 天，HR 说：“责任考核：差异归责到部门，绩效分怎么扣你定。”"),
    22: ("评审团", "第 22 天，评审团说：“提交降本增效方案，按创新/可操作/成本影响/业财融合四维判分。”"),
    23: ("监控中心", "第 23 天，监控中心说：“成本偏离预警：黄灯还是红灯，你处置。”"),
    24: ("突发现场", "第 24 天，突发现场说：“突发危机！原料涨价/设备故障/订单取消/质量索赔/环保整改，你权衡。”"),
    25: ("监管",  "第 25 天，监管说：“合规红线：成本造假、虚增存货、责任甩锅，触碰即警告或终止。”"),
    26: ("管理会计师", "第 26 天，管理会计师说：“同口径复盘：把关键决策数据逐条回看，找可改进点。”"),
    27: ("能力画像", "第 27 天，能力画像说：“算对成本、解释差异、用成本做决策，三项能力给你画像。”"),
    28: ("董事会", "第 28 天，董事会说：“用成本做经营决策：定价、排产、投融资方案，路演定生死。”"),
}
TOTAL = 28

# ---------------- 算账引擎（V4.0 已验证公式） ----------------
def dev_color(d):
    if d <= 95:   return "蓝·偏低"
    if d <= 105:  return "绿·正常"
    if d <= 115:  return "黄·偏高"
    return "红·失控"

def compute(s):
    mat_total = s["mat_price"] * s["mat_qty"]
    labor_total = s["labor_hours"] * s["labor_rate"]
    proc_total = labor_total + s["mfg_total"]
    mat_eq = s["finished"] + s["wip"] * s["mat_pct"]
    proc_eq = s["finished"] + s["wip"] * s["proc_pct"]
    mat_unit = mat_total / mat_eq if mat_eq else 0
    proc_unit = proc_total / proc_eq if proc_eq else 0
    unit_cost = mat_unit + proc_unit
    finished_cost = unit_cost * s["finished"]
    total_cost = mat_total + proc_total
    wip_cost = total_cost - finished_cost
    revenue = s["price"] * s["finished"]
    profit = revenue - finished_cost
    deviation = unit_cost / s["std_cost"] * 100 if s["std_cost"] else 100
    perf = max(0.0, 95 - abs(deviation - 100) * 2)
    return dict(mat_total=mat_total, labor_total=labor_total, proc_total=proc_total,
                mat_eq=mat_eq, proc_eq=proc_eq, mat_unit=mat_unit, proc_unit=proc_unit,
                unit_cost=unit_cost, finished_cost=finished_cost, wip_cost=wip_cost,
                total_cost=total_cost, revenue=revenue, profit=profit,
                deviation=deviation, perf=perf)

# ---------------- 会话状态初始化 ----------------
def default_state():
    return dict(role="成本会计", company="智控制造厂",
                mat_price=12.0, mat_qty=5000, finished=300, wip=100,
                labor_hours=2000, labor_rate=25.0, mfg_fixed=20000.0, mfg_var=25000.0,
                mfg_total=45000.0, mat_pct=1.0, proc_pct=0.5, price=600.0,
                std_cost=421.0, cost_method="完全成本法", step_method="品种法",
                inv_method="加权平均", sales_mode="满产满销", risk_hits=0, done_redline=False,
                resp_penalty=0.0, log=[])

if "state" not in st.session_state:
    st.session_state.state = default_state()
if "step" not in st.session_state:
    st.session_state.step = 1
if "done" not in st.session_state:
    st.session_state.done = []
if "finished" not in st.session_state:
    st.session_state.finished = False

s = st.session_state.state

def commit(text):
    """存档本步决策并推进到下一步。"""
    cur = st.session_state.step
    if cur not in st.session_state.done:
        st.session_state.done.append(cur)
    s["log"].append({"步": cur, "天": DIARY[cur][0], "决策": text})
    st.session_state.step = min(st.session_state.step + 1, TOTAL + 1)
    st.rerun()

def diary_line(who, say):
    st.markdown(f'<div class="diary-line"><span class="who">[{who}]</span> '
                f'<span class="say">{say}</span></div>', unsafe_allow_html=True)

# ---------------- 顶部指挥中心头部 ----------------
r = compute(s)
_head_name = DIARY.get(st.session_state.step, ("实训完成", ""))[0]
_mode = s.get("mode", "实训中")
_mode_v = "正式" if _mode == "正式" else ("练习" if _mode == "练习" else "实训中")
st.markdown(f"""
<div class="hud-wrap">
  <span class="scan"></span>
  <span class="hud-c tl"></span><span class="hud-c tr"></span>
  <span class="hud-c bl"></span><span class="hud-c br"></span>
  <div class="hud-inner">
    <div class="brand-en">Smart Cost Command Center</div>
    <div class="brand-title">◈ 智能成本控制指挥中心 <span class="ver">V{APP_VERSION}</span></div>
    <div class="brand-sub">创始人日记体 × {TOTAL} 步全流程成本管理虚拟仿真
       ｜ 当前：第 {st.session_state.step} 天 · {_head_name}</div>
    <div class="brand-line">身份进阶 · 成本会计 → 车间核算员 → 财务经理 → 管理会计师</div>
  </div>
</div>
""", unsafe_allow_html=True)

# 顶栏徽章：实训模式 + 学生身份（V6.0 facade.Badge）
_mc = "正式" if _mode == "正式" else ("练习" if _mode == "练习" else "实训中")
_stu = st.session_state.student or {}
hb1, hb2 = st.columns([1, 2])
with hb1:
    if _mode == "正式":
        facade.Badge(f"模式 · {_mc}", bg_color="#00FF9C22", text_color="#00FF9C")
    elif _mode == "练习":
        facade.Badge(f"模式 · {_mc}", bg_color="#FFB30022", text_color="#FFB300")
    else:
        facade.Badge(f"模式 · {_mc}")
with hb2:
    facade.Badge(f"学生 · {_stu.get('姓名','—')}（{_stu.get('学号','—')} · {_stu.get('班级','—')}）")

# 四指标霓虹卡片（V6.0 facade.Metric）
m1, m2, m3, m4 = st.columns(4)
with m1:
    facade.Metric("单位产品成本", f"¥{r['unit_cost']:.2f}")
with m2:
    facade.Metric("经营利润", f"¥{r['profit']:,.0f}")
with m3:
    facade.Metric("成本偏离指数", f"{r['deviation']:.1f}%", delta=dev_color(r["deviation"]))
with m4:
    facade.Metric("责任绩效分", f"{max(0.0, r['perf'] - s['resp_penalty']):.0f} / 100")

cur = st.session_state.step
if not st.session_state.finished and cur <= TOTAL:
    who, say = DIARY[cur]
    diary_line(who, say)

# ---------------- 侧边栏：阶段导航 ----------------
with st.sidebar:
    st.markdown("### 指挥中心导航")
    _prog = len(st.session_state.done) / TOTAL
    facade.Progress(value=int(round(_prog * 100)), label=f"完成 {len(st.session_state.done)} / {TOTAL} 步")
    st.caption("A 情境与参数设定（1-4）· B 自主设计与决策（5-21）· C 风险与博弈（22-25）· D 产出与复盘（26-28）")
    st.markdown("#### A · 情境与参数设定")
    for n in range(1, 5):
        tag = "✔" if n in st.session_state.done else ("▸" if n == cur else "·")
        st.markdown(f"{tag} 第{n}天·{DIARY[n][0]}")
    st.markdown("#### B · 自主设计与决策")
    for n in range(5, 22):
        tag = "✔" if n in st.session_state.done else ("▸" if n == cur else "·")
        st.markdown(f"{tag} 第{n}天·{DIARY[n][0]}")
    st.markdown("#### C · 风险与博弈")
    for n in range(22, 26):
        tag = "✔" if n in st.session_state.done else ("▸" if n == cur else "·")
        st.markdown(f"{tag} 第{n}天·{DIARY[n][0]}")
    st.markdown("#### D · 产出与复盘")
    for n in range(26, 29):
        tag = "✔" if n in st.session_state.done else ("▸" if n == cur else "·")
        st.markdown(f"{tag} 第{n}天·{DIARY[n][0]}")
    if cur > 1 and not st.session_state.finished:
        if facade.Button("⬅ 返回上一步", icon="arrow-left", key="nav_back"):
            st.session_state.step = max(1, cur - 1)
            st.rerun()
    st.caption(f"版本 V{APP_VERSION} · facade 主题")

# ---------------- 步骤分支 ----------------
# ===== A 情境与参数设定（1-4） =====
if cur == 1:
    st.markdown("### 定角色 · 配初始资源 · 认领目标")
    role = st.radio("初始角色（将随流程进阶）", ["成本会计", "车间核算员", "财务经理", "管理会计师"])
    cap = st.slider("初始资金（元）", 50000, 500000, 200000, step=10000)
    target = st.slider("目标经营利润（元）", 20000, 120000, 60000, step=5000)
    if facade.Button("确认 · 拍板签约", icon="save", key="k1"):
        s["role"] = role; s["target_profit"] = target
        commit(f"签约：以{role}身份起步，初始资金 ¥{cap:,.0f}，目标利润 ¥{target:,.0f}。")

elif cur == 2:
    st.markdown("### 材料采购谈判")
    price = st.slider("材料单价（元/kg）", 5.0, 20.0, 12.0, step=0.5, key="d2_price")
    qty = st.slider("采购量（kg）", 1000, 10000, 5000, step=500, key="d2_qty")
    cost = price * qty
    st.caption(f"直接材料预计 ¥{cost:,.0f}。单价 >20 元触发【成本造假】红线。")
    if st.button("确认 · 签订采购合同"):
        if price > 20:
            st.error("触碰红线：材料单价高于市价 20 元，涉嫌成本造假。首次警告（扣 30 分 + 重做）。")
            s["resp_penalty"] += 30; s["done_redline"] = True
            commit(f"红线警告：材料单价 ¥{price} 涉嫌造假，扣 30 分重做。")
        else:
            s["mat_price"] = price; s["mat_qty"] = qty
            commit(f"签约采购：¥{price}/kg × {qty}kg，直接材料 ¥{cost:,.0f}。")

elif cur == 3:
    st.markdown("### 料到入库 · 材料核算")
    actual = st.number_input("实际入库量（kg）", min_value=100, max_value=12000, value=int(s["mat_qty"]), key="d3_in")
    if st.button("确认 · 材料入库"):
        s["mat_qty"] = actual
        after = compute(s)
        commit(f"入库：¥{s['mat_price']}/kg × {actual}kg，直接材料 ¥{after['mat_total']:,.0f}。")

elif cur == 4:
    st.markdown("### 领料开工 · 排产配置")
    fin = st.slider("完工产量（件）", 100, 800, int(s["finished"]), key="d4_fin")
    wip = st.slider("在产品（件）", 0, 400, int(s["wip"]), key="d4_wip")
    if wip > fin * 2:
        st.warning("警示：在产品超过完工 2 倍，涉嫌【虚增存货】红线。")
    if st.button("确认 · 领料开工"):
        if wip > fin * 2:
            st.error("触碰红线：在产品远超完工，虚增存货。首次警告（扣 30 分 + 重做）。")
            s["resp_penalty"] += 30; s["done_redline"] = True
            commit(f"红线警告：在产品 {wip} > 完工 {fin}×2，虚增存货，扣 30 分。")
        else:
            s["finished"] = fin; s["wip"] = wip
            commit(f"领料开工：完工 {fin} 件，在产品 {wip} 件。")

# ===== B 自主设计与决策（5-21） =====
elif cur == 5:
    st.markdown("### 人工排班 · 直接人工")
    h = st.slider("实际工时（h）", 500, 5000, int(s["labor_hours"]), step=50, key="d5_h")
    rate = st.slider("小时工资（元/h）", 15.0, 40.0, s["labor_rate"], step=0.5, key="d5_rate")
    if st.button("确认 · 排班定薪"):
        s["labor_hours"] = h; s["labor_rate"] = rate
        after = compute(s)
        commit(f"直接人工 ¥{after['labor_total']:,.0f}（{h}h × ¥{rate}）。")

elif cur == 6:
    st.markdown("### 制造费用拆解 · 变动/固定")
    fixed = st.slider("固定制造费用（元）", 5000, 50000, int(s["mfg_fixed"]), step=1000, key="d6_fix")
    var = st.slider("变动制造费用（元）", 5000, 50000, int(s["mfg_var"]), step=1000, key="d6_var")
    if st.button("确认 · 归集费用"):
        s["mfg_fixed"] = fixed; s["mfg_var"] = var; s["mfg_total"] = fixed + var
        commit(f"制造费用拆解：固定 ¥{fixed:,.0f} + 变动 ¥{var:,.0f} = ¥{fixed+var:,.0f}。")

elif cur == 7:
    st.markdown("### 费用分摊 · 选择动因")
    basis = st.radio("分摊动因", ["直接人工工时", "机器工时", "直接材料金额"])
    if st.button("确认 · 执行分摊"):
        s["alloc_basis"] = basis
        commit(f"制造费用按「{basis}」分摊。")

elif cur == 8:
    st.markdown("### 辅助车间 · 交互分配")
    m = st.radio("辅助费用分配方法", ["一次交互分配", "直接分配", "计划成本分配"])
    if st.button("确认 · 辅助分配"):
        s["aux_method"] = m
        commit(f"辅助车间费用采用「{m}」。")

elif cur == 9:
    st.markdown("### 完工程度 · 约当产量")
    mp = st.slider("材料完工程度（%）", 0, 100, int(s["mat_pct"] * 100), step=5, key="d9_mp")
    pp = st.slider("加工完工程度（%）", 0, 100, int(s["proc_pct"] * 100), step=5, key="d9_pp")
    before = compute(s)
    if st.button("确认 · 定完工程度"):
        s["mat_pct"] = mp / 100.0; s["proc_pct"] = pp / 100.0
        after = compute(s)
        commit(f"完工程度：材料 {mp}%、加工 {pp}%。约当 材料 {after['mat_eq']:.0f} / 加工 {after['proc_eq']:.0f}。")

elif cur == 10:
    st.markdown("### 品种法结账 · 成本算平")
    before = compute(s)
    rows = [["直接材料", f"¥{r['mat_total']:,.0f}"], ["直接人工", f"¥{r['labor_total']:,.0f}"],
            ["制造费用", f"¥{r['proc_total']-r['labor_total']:,.0f}"],
            ["材料约当", f"{r['mat_eq']:.0f}"], ["加工约当", f"{r['proc_eq']:.0f}"],
            ["材料单位成本", f"¥{r['mat_unit']:.2f}"], ["加工单位成本", f"¥{r['proc_unit']:.2f}"],
            ["单位产品成本", f"¥{r['unit_cost']:.2f}"], ["完工成本", f"¥{r['finished_cost']:,.2f}"],
            ["在产品成本", f"¥{r['wip_cost']:,.2f}"]]
    st.table(pd.DataFrame(rows, columns=["项目", "金额"]))
    ok = abs(r["total_cost"] - (r["mat_total"] + r["proc_total"])) < 0.01
    st.markdown(f"成本合计 ¥{r['total_cost']:,.0f} vs 要素费用 ¥{r['mat_total']+r['proc_total']:,.0f} → {'<span class=ok>勾稽通过 ✓</span>' if ok else '<span class=bad>不平 ✗</span>'}", unsafe_allow_html=True)
    if st.button("确认 · 品种法结账"):
        commit(f"品种法结账：单位成本 ¥{r['unit_cost']:.2f}，完工 ¥{r['finished_cost']:,.0f}，在产品 ¥{r['wip_cost']:,.0f}。")

elif cur == 11:
    st.markdown("### 分批法 · 批次设计")
    m = st.radio("分批归集方式", ["按订单归集", "按批次归集", "按产品归集"])
    if st.button("确认 · 完成分批核算"):
        s["batch_method"] = m
        after = compute(s)
        commit(f"分批法采用「{m}」。单位成本保持 ¥{after['unit_cost']:.2f}。")

elif cur == 12:
    st.markdown("### 分步法 · 结转方式")
    m = st.radio("分步结转方式", ["逐步结转（需成本还原）", "平行结转（只算本步骤份额）"])
    st.caption("逐步结转：半成品成本随实物流转结转（需成本还原）；平行结转：各步骤只算本步骤份额。")
    if st.button("确认 · 完成分步核算"):
        s["step_method"] = m
        after = compute(s)
        commit(f"分步法采用{m}。成本还原已由系统按约当完成，单位成本保持 ¥{after['unit_cost']:.2f}。")

elif cur == 13:
    st.markdown("### 两法切换 · 变动 vs 完全成本法")
    before = compute(s)
    m = st.radio("成本计算方法", ["变动成本法", "完全成本法"])
    fin13 = s["finished"]; mfg13 = s["mfg_total"]
    fixed_unit = mfg13 / fin13 if fin13 else 0
    if m == "变动成本法":
        shown = r["unit_cost"] - fixed_unit
        st.caption(f"变动成本法：单位变动成本 ¥{shown:.2f}（固定制造费用 ¥{mfg13:,.0f} 期间化），存货不吸收固定制造费用。")
    else:
        shown = r["unit_cost"]
        st.caption(f"完全成本法：单位成本 ¥{shown:.2f}，固定制造费用由销货/存货吸收。")
    if st.button("确认 · 完成两法对比"):
        s["cost_method"] = m
        after = compute(s)
        commit(f"两法对比完成：{m}。变动法单位成本 ¥{shown:.2f}，完全法 ¥{after['unit_cost']:.2f}。")

elif cur == 14:
    st.markdown("### 量本利 · 保本点测算")
    before = compute(s)
    price = st.slider("售价（元/件）", 200, 1000, int(s["price"]), key="d14_price")
    vc = r["unit_cost"]
    fixed = r["proc_total"] - r["labor_total"] + s["mfg_fixed"]
    cm = price - vc
    bep = int(np.ceil(fixed / cm)) if cm > 0 else 0
    st.caption(f"单位变动成本 ¥{vc:.2f}，固定成本 ¥{fixed:,.0f}，单位边际贡献 ¥{cm:.2f}，保本销量 ≈ {bep} 件。")
    if st.button("确认 · 完成量本利测算"):
        s["price"] = price
        after = compute(s)
        commit(f"量本利：售价 ¥{price}/件，保本销量 ≈ {bep} 件。经营利润 ¥{after['profit']:,.0f}。")

elif cur == 15:
    st.markdown("### 产销情境选择")
    sc = st.radio("产销情境", ["满产满销", "压产累库存", "提价保毛利", "降本放量"])
    adj = {"满产满销": 0, "压产累库存": -3, "提价保毛利": 5, "降本放量": 2}[sc]
    if st.button("确认 · 确定情境"):
        s["sales_mode"] = sc; s["std_cost"] = 421 * (1 + adj / 100.0)
        after = compute(s)
        commit(f"情境：{sc}。标准基准调整 {adj:+}，偏离指数 {after['deviation']:.1f}%。")

elif cur == 16:
    st.markdown("### 存货计价方法")
    m = st.radio("计价方法", ["先进先出法", "加权平均法", "移动加权平均法"])
    if st.button("确认 · 完成计价"):
        s["inv_method"] = m
        after = compute(s)
        commit(f"存货计价：{m}。单位成本维持 ¥{after['unit_cost']:.2f}（计价口径已记录）。")

elif cur == 17:
    st.markdown("### 标准成本设定")
    before = compute(s)
    std = st.slider("标准单位成本（元/件）", 300, 600, int(s["std_cost"]), step=1, key="d17_std")
    st.caption(f"标准成本作为偏离指数与绩效分基准。当前偏离 {before['deviation']:.1f}%（{dev_color(before['deviation'])}）。")
    if st.button("确认 · 设定标准"):
        s["std_cost"] = std
        after = compute(s)
        commit(f"标准成本 ¥{std}/件。偏离指数 {after['deviation']:.1f}%（{dev_color(after['deviation'])}）。")

elif cur == 18:
    st.markdown("### 差异分析 · 价格差异 / 数量差异")
    std_p = st.slider("标准单价（元/kg）", 5.0, 20.0, 12.0, step=0.5, key="d18_stdp")
    std_q = st.slider("标准用量（kg/件）", 5, 25, int(s["mat_qty"] / max(s["finished"], 1)), key="d18_stdq")
    actual_p = s["mat_price"]; actual_q = s["mat_qty"] / max(s["finished"], 1)
    pq = (actual_p - std_p) * actual_q * s["finished"]
    qq = (actual_q - std_q) * std_p * s["finished"]
    st.caption(f"价格差异 = ({actual_p}-{std_p})×{actual_q:.0f}×{s['finished']} = ¥{pq:,.0f}；数量差异 = ({actual_q:.0f}-{std_q})×{std_p}×{s['finished']} = ¥{qq:,.0f}")
    if st.button("确认 · 归因差异"):
        s["variance_price"] = pq; s["variance_qty"] = qq
        commit(f"差异分析：价格差异 ¥{pq:,.0f}，数量差异 ¥{qq:,.0f}。　采购部/生产部责任定位完成。")

elif cur == 19:
    st.markdown("### 作业成本法 · 成本库与动因")
    pools = st.slider("作业成本库（元）", 10000, 60000, int(r["proc_total"]), step=1000, key="d19_pools")
    drv = st.radio("主要成本动因", ["机器工时", "检验次数", "订单数", "物流次数"])
    if st.button("确认 · 完成作业成本核算"):
        s["act_pools"] = pools; s["act_driver"] = drv
        after = compute(s)
        commit(f"作业成本法：成本库 ¥{pools:,.0f}，动因「{drv}」。单位成本 ¥{after['unit_cost']:.2f}。")

elif cur == 20:
    st.markdown("### 动因博弈 · 成本转移")
    drv = st.radio("动因选择（影响产品间成本分摊）", ["高产产品动因", "低产高复杂度动因", "均衡动因"])
    if st.button("确认 · 提交动因决策"):
        s["driver_game"] = drv
        after = compute(s)
        commit(f"动因博弈：选择「{drv}」。单位成本 ¥{after['unit_cost']:.2f}。")

elif cur == 21:
    st.markdown("### 责任考核 · 差异归责")
    before = compute(s)
    rs = st.radio("差异责任归属", ["采购部（价格差异）", "生产部（数量差异）", "双方共同", "全部推给他人"])
    penalty = 0
    if rs == "采购部（价格差异）":
        penalty = 5 if abs(s.get("variance_price", 0)) > 3000 else 0
    elif rs == "生产部（数量差异）":
        penalty = 5 if abs(s.get("variance_qty", 0)) > 3000 else 0
    elif rs == "全部推给他人":
        st.warning("警示：责任全推他人，涉嫌【责任甩锅】红线。")
    if st.button("确认 · 完成责任考核"):
        if rs == "全部推给他人":
            st.error("触碰红线：责任全推他人，甩锅行为。首次警告（扣 30 分 + 重做）。")
            s["resp_penalty"] += 30; s["done_redline"] = True
            commit(f"红线警告：责任甩锅，扣 30 分。")
        else:
            s["resp_penalty"] += penalty
            commit(f"责任划分：{rs}（绩效扣 {penalty:.0f}）。调整后绩效约 {max(0, r['perf']-s['resp_penalty']):.0f} 分。")

# ===== C 风险与博弈（22-25） =====
elif cur == 22:
    st.markdown("### 方案竞标 · 降本增效（AI 四维判分）")
    idea = st.text_area("提交降本增效方案（创新30·可操作30·成本影响25·业财融合15）",
                        "优化材料采购渠道，推行作业成本精细核算，以标准成本纠偏、动态调价。")
    if st.button("提交并接受判分"):
        # AI 四维判分（规则驱动）
        c_inn = min(30, 30 - 5 if "创新" not in idea and "优化" not in idea else 24)
        c_opt = 30 - (0 if len(idea) >= 15 else 10)
        c_cost = min(25, 25 - 10 if "成本" not in idea else 20)
        c_biz = 15 - (0 if "利润" in idea or "定价" in idea else 6)
        total = c_inn + c_opt + c_cost + c_biz
        s["bid"] = total
        commit(f"方案竞标提交，AI 四维判分：创新{c_inn}/可操作{c_opt}/成本影响{c_cost}/业财融合{c_biz} = {total}。")

elif cur == 23:
    st.markdown("### 监控预警 · 成本偏离处置")
    before = compute(s)
    st.caption(f"当前偏离指数 {before['deviation']:.1f}%（{dev_color(before['deviation'])}）。")
    act = st.radio("预警处置", ["继续监控", "调标准重设基准", "紧急降本专项", "暂停排产核查"])
    if st.button("确认 · 执行预警处置"):
        if act == "调标准重设基准":
            s["std_cost"] = r["unit_cost"] * 1.02
        after = compute(s)
        commit(f"预警处置：{act}。处置后偏离 {after['deviation']:.1f}%。")

elif cur == 24:
    st.markdown("### 突发危机 · 风险博弈")
    import random
    pool = [
        ("原料涨价 15%", "采购成本跳升，可用价格协商/替代料/提价对冲。"),
        ("设备故障停产 2 天", "产量与约当受影响，需重新排产/加班。"),
        ("大客户取消 1/3 订单", "需求骤降，积压库存风险。"),
        ("质量索赔 5000 元", "直接损失，需追溯责任与改进。"),
        ("环保整改 8000 元", "合规支出，短期成本上升。"),
    ]
    ev, note = random.choice(pool)
    st.caption(f"危机事件：{ev}。{note}")
    act = st.radio("应对策略", ["价格协商+替代料", "加班补产", "降价去库存", "追溯整改", "计提损失"])
    if st.button("确认 · 二次确认后提交"):
        impact = {"价格协商+替代料": 3000, "加班补产": 4000, "降价去库存": -2000,
                  "追溯整改": 2000, "计提损失": 5000}[act]
        s["risk_event"] = ev
        s["mfg_total"] += impact
        after = compute(s)
        commit(f"危机「{ev}」应对「{act}」，成本影响 {impact:+}，单位成本 ¥{after['unit_cost']:.2f}。")

elif cur == 25:
    st.markdown("### 合规红线 · 终审确认")
    st.markdown("**三条红线**：① 材料单价 >20 元＝成本造假；② 在产品 > 完工×2＝虚增存货；③ 责任全推他人＝甩锅。")
    st.caption(f"本次实训已触碰红线次数：{s['done_redline']} 次。")
    if st.button("确认 · 提交系统判定"):
        if s["done_redline"]:
            st.error("已触碰红线 ≥1 次，本次实训计入警告记录并降级为【练习模式】。")
            s["mode"] = "练习"
        else:
            s["mode"] = "正式"
            st.success("合规通过：未触碰红线，正式成绩有效。")
        commit(f"合规终审：{'练习模式（有红线记录）' if s['done_redline'] else '正式模式（无红线）'}。")

# ===== D 产出与复盘（26-28） =====
elif cur == 26:
    st.markdown("### 同口径复盘 · 关键决策数据")
    if s["log"]:
        st.table(pd.DataFrame(s["log"]).tail(28))
    improve = st.text_area("复盘改进点（写下要修正的决策）", "优化采购单价、收紧排产、重设标准成本。")
    if st.button("确认 · 完成复盘"):
        after = compute(s)
        commit(f"同口径复盘完成：{improve[:50]}…四指标终态 {r['deviation']:.1f}% / {r['perf']:.0f} 分。")

elif cur == 27:
    st.markdown("### 能力画像 · 三角雷达")
    c = {"算对成本": 0, "解释差异": 0, "用成本决策": 0}
    c["算对成本"] = max(c["算对成本"], int(10 + 40 * (1 - min(1, abs(r["deviation"] - 100) / 100))))
    c["解释差异"] = max(c["解释差异"], int(30 + (10 if r["deviation"] > 95 else 0)))
    c["用成本决策"] = max(c["用成本决策"], int(30 + (20 if r["profit"] > 0 else 0)))
    labels = list(c.keys()); values = list(c.values())
    fig = go.Figure(go.Scatterpolar(r=values, theta=labels, fill="toself",
                                    line_color="#00FF9C", fillcolor="rgba(0,255,156,.25)"))
    fig.update_layout(polar=dict(bgcolor="#0A0E12", radialaxis=dict(visible=True, range=[0, 100],
                       gridcolor="#1E3A28")), showlegend=False, height=380,
                      paper_bgcolor="#05070A", font=dict(color="#E6F2E9"))
    st.plotly_chart(fig, use_container_width=True)
    if st.button("确认 · 生成能力画像"):
        commit(f"能力画像：算对成本 {c['算对成本']} / 解释差异 {c['解释差异']} / 用成本决策 {c['用成本决策']}。")

elif cur == 28:
    st.markdown("### 经营决策 · 定价 / 排产 / 路演")
    price = st.slider("最终定价（元/件）", 200, 1200, int(s["price"]), key="d28_price")
    plan = st.radio("排产方案", ["满产满销", "控制库存", "扩大产能"])
    pitch = st.text_area("路演一句话（投资人视角）", "以标准成本纠偏、作业成本归因，实现降本增效与稳健盈利。")
    s["price"] = price
    after = compute(s)
    st.caption(f"定价 ¥{price}/件，单位成本 ¥{after['unit_cost']:.2f}，毛利 ¥{price-after['unit_cost']:.2f}/件，经营利润 ¥{after['profit']:,.0f}。")
    if facade.Button("完成实训 · 提交路演", icon="send", key="k28"):
        st.session_state.finished = True
        commit(f"经营决策：定价 ¥{price}，{plan}，路演「{pitch[:40]}…」")

# ---------------- 底部 28 步进度带（V6.0；替代已删顶部网格，侧边导航保留） ----------------
if not st.session_state.finished:
    _segs = []
    for _n in range(1, TOTAL + 1):
        _cls = "seg done" if _n in st.session_state.done else ("seg now" if _n == cur else "seg")
        _segs.append(f'<span class="{_cls}" title="第{_n}天"></span>')
    st.markdown(
        f'<div class="stepband">{"".join(_segs)}'
        f'<span class="cap">完成 {len(st.session_state.done)} / {TOTAL} 步 ｜ 实心=完成 · 脉冲=当前 · 空心=未开始</span></div>',
        unsafe_allow_html=True)

# ================= 完成页：个人实验报告 =================
if st.session_state.finished:
    st.markdown("## 🎉 恭喜完成全部 28 步虚拟仿真实训！")
    _stu = st.session_state.student or {}
    st.markdown(f"**学生**：{_stu.get('姓名','—')}（学号 {_stu.get('学号','—')} · {_stu.get('班级','—')}）")
    st.markdown("### 个人实验报告（过程记录存档）")
    if s["log"]:
        st.table(pd.DataFrame(s["log"]))
    final_score = max(0.0, min(100.0, r["perf"] + (10 if s["mode"] == "正式" else 0) - s["resp_penalty"]))
    st.markdown(f"**终态四指标**：单位成本 ¥{r['unit_cost']:.2f} · 经营利润 ¥{r['profit']:,.0f} · "
                f"成本偏离 {r['deviation']:.1f}% · 责任绩效 {r['perf']:.0f}")
    st.markdown(f"**系统终结性评分**（供老师打分参考）：{final_score:.1f} / 100")

    # ---- 三方评价：老师50% + 学生互评20% + 企业专家30% ----
    st.markdown("### 三方评价 · 综合成绩")
    st.caption("权重：老师 50% + 学生互评 20% + 企业专家 30%")
    t_score = st.slider("老师打分（0-100）", 0, 100, int(round(final_score)), key="fin_teacher")
    p_score = st.slider("学生互评（0-100）", 0, 100, 80, key="fin_peer")
    e_score = st.slider("企业专家评分（0-100）", 0, 100, 85, key="fin_expert")
    weighted = 0.5 * t_score + 0.2 * p_score + 0.3 * e_score
    s["eval"] = dict(teacher=t_score, peer=p_score, expert=e_score, weighted=round(weighted, 1))
    ev = pd.DataFrame([
        {"评价方": "老师", "权重": "50%", "得分": t_score},
        {"评价方": "学生互评", "权重": "20%", "得分": p_score},
        {"评价方": "企业专家", "权重": "30%", "得分": e_score},
        {"评价方": "综合成绩", "权重": "100%", "得分": round(weighted, 1)},
    ])
    st.table(ev)
    st.markdown(f"**综合成绩**：**{weighted:.1f} / 100** 　"
                f"（老师 {t_score}×50% + 学生互评 {p_score}×20% + 企业专家 {e_score}×30%）")
    if facade.Button("重做一轮（重置并重新开始）", icon="refresh", key="k_reset"):
        st.session_state.state = default_state()
        st.session_state.step = 1
        st.session_state.done = []
        st.session_state.finished = False
        st.rerun()
