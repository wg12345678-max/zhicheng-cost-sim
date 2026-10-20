# -*- coding: utf-8 -*-
"""
智控成本 · 数创价值 —— 制造企业全流程成本管理虚拟仿真实训（交互版）
依据：西南财经大学天府学院《成本管理会计 ACT1415A》课程组
      2026 中国仿真创新应用大赛 设计方案 V4.0
核心：按步骤做决策，每一步实时刷新「单位成本 / 经营利润 / 成本偏离指数 / 责任绩效分」四项指标（算账闭环）
"""
import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(
    page_title="智控成本 · 数创价值 | 成本管理虚拟仿真",
    page_icon="🧮",
    layout="wide",
)

# ============================ 算账引擎 ============================
QUALITY = {"低劣": 0.85, "合格": 1.0, "优质": 1.08}
SUPPLIERS = {
    "S1 本地供应商": {"price": 11.0, "quality": "合格", "tag": "价格适中 · 交期快"},
    "S2 进口优质料": {"price": 14.0, "quality": "优质", "tag": "质量优 · 交期长 · 价格高"},
    "S3 低价料":     {"price": 8.0,  "quality": "低劣", "tag": "价格低 · 质量差（易返工）"},
}
TRAIN_MODE = {"一次投入": 1.0, "分工序分次投入": 0.5}


def compute(state):
    """由决策状态实时计算四指标（方案 3.3 节公式）。"""
    material_total = state["mat_price"] * state["mat_qty"] * QUALITY[state["quality"]]
    labor_total = state["labor_hours"] * state["wage"]
    processing_total = labor_total + state["mfg_total"]
    mat_done = state["material_done"]          # 投料方式决定的材料完工程度
    proc_done = state["proc_done"]             # 加工完工程度
    mat_eq = state["wip"] * mat_done
    proc_eq = state["wip"] * proc_done
    mat_unit = material_total / (state["finished"] + mat_eq) if (state["finished"] + mat_eq) > 0 else 0
    proc_unit = processing_total / (state["finished"] + proc_eq) if (state["finished"] + proc_eq) > 0 else 0
    unit_cost = mat_unit + proc_unit
    finished_cost = state["finished"] * unit_cost
    wip_cost = mat_eq * mat_unit + proc_eq * proc_unit
    revenue = state["price"] * state["finished"]
    profit = revenue - finished_cost
    std = state["standard_cost"] if state["standard_cost"] > 0 else unit_cost
    deviation = unit_cost / std * 100.0
    perf = max(0.0, 95 - abs(deviation - 100) * 2)
    return {
        "material_total": material_total, "labor_total": labor_total,
        "processing_total": processing_total, "mat_eq": mat_eq, "proc_eq": proc_eq,
        "mat_unit": mat_unit, "proc_unit": proc_unit, "unit_cost": unit_cost,
        "finished_cost": finished_cost, "wip_cost": wip_cost,
        "revenue": revenue, "profit": profit,
        "deviation": deviation, "perf": perf,
        "total_cost": finished_cost + wip_cost,
    }


def deviation_color(d):
    if d <= 95: return "蓝 · 成本偏低"
    if d <= 105: return "绿 · 正常"
    if d <= 115: return "黄 · 成本偏高"
    return "红 · 严重偏高"


# ============================ 步骤定义 ============================
STEPS = [
    (1, "A", "开局签约", "设定目标利润率，确定售价与经营目标"),
    (2, "A", "材料采购", "选择供应商（价格 / 质量 / 交期权衡）"),
    (3, "A", "材料入库", "设定材料单价与采购数量"),
    (4, "A", "生产领料", "选择投料方式（决定在产品材料完工程度）"),
    (5, "A", "人工投入", "设定工时与工资率"),
    (6, "A", "制造费用", "选择分摊基数并设定制造费用总额"),
    (7, "A", "约当产量", "设定完工/在产品数量与加工完工程度"),
    (8, "A", "品种法核算", "归集要素费用，计算完工与在产品成本"),
    (9, "B", "量本利分析", "调整售价与销量，测算保本点与经营利润"),
    (10, "B", "产销情境", "选择产销情境，观察存货吸收固定成本"),
    (11, "B", "标准成本", "设定标准料工费，诊断成本偏离指数"),
    (12, "B", "责任中心", "划分责任中心，落实责任绩效分"),
    (13, "C", "降本金点子", "提交降本增效方案，AI/规则评分"),
    (14, "C", "风险事件", "应对随机风险事件，做出经营决策"),
    (15, "C", "红线检查", "系统检测成本造假 / 虚增存货 / 责任甩锅"),
    (16, "C", "经营决策", "出具定价 / 排产 / 考核建议书与终评分"),
]
TOTAL_STEPS = len(STEPS)
MODULE_NAMES = {"A": "成本核算基本功", "B": "两法对比与决策", "C": "作业责任与降本"}


def default_state():
    return {
        "mat_price": 12.0, "mat_qty": 5000, "quality": "合格", "supplier": None,
        "labor_hours": 2000, "wage": 25.0,
        "mfg_total": 45000.0, "mfg_base": "人工工时",
        "material_done": 1.0, "proc_done": 0.5,
        "finished": 300, "wip": 100,
        "price": 600.0, "standard_cost": 421.0,
        "target_rate": 0.15,
        "scenario": "产销平衡",
        "responsibility": "合理划分",
        "risk": None, "risk_loss": 0.0,
        "suggestion": "", "idea_score": None,
        "resp_penalty": 0.0, "perf_adj": 0.0,
        "redlines": {"成本造假": 0, "虚增存货": 0, "责任甩锅": 0},
        "events": [],
        "notes": {},
    }


# 初始化会话状态
if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.state = default_state()
    st.session_state.done = []
    st.session_state.finished = False


# ============================ 顶部：四指标面板（算账闭环） ============================
st.markdown("## 🧮 智控成本 · 数创价值")
st.caption("制造企业全流程成本管理虚拟仿真决策实训 · 按步骤操作，每一步实时刷新四大指标")

r = compute(st.session_state.state)
c1, c2, c3, c4 = st.columns(4)
c1.metric("单位产品成本", f"¥{r['unit_cost']:.2f}")
c2.metric("经营利润", f"¥{r['profit']:,.0f}")
c3.metric("成本偏离指数", f"{r['deviation']:.1f}%", delta=deviation_color(r["deviation"]), delta_color="off")
c4.metric("责任绩效分", f"{r['perf']:.0f} / 100")


# ============================ 侧边栏：步骤导航 ============================
with st.sidebar:
    st.markdown("### 实验流程")
    prog = len(st.session_state.done) / TOTAL_STEPS
    st.progress(prog, text=f"完成 {len(st.session_state.done)} / {TOTAL_STEPS} 步")
    for mod in ["A", "B", "C"]:
        st.markdown(f"**模块 {mod} · {MODULE_NAMES[mod]}**")
        for num, m, name, _ in STEPS:
            if m != mod:
                continue
            if num in st.session_state.done:
                st.markdown(f"&nbsp;&nbsp;✅ 第{num}步 · {name}")
            elif num == st.session_state.step:
                st.markdown(f"&nbsp;&nbsp;➡️ **第{num}步 · {name}（当前）**")
            else:
                st.markdown(f"&nbsp;&nbsp;⬜ 第{num}步 · {name}")
    if st.session_state.step > 1 and st.button("⬅ 返回上一步"):
        st.session_state.step -= 1
        st.rerun()


# ============================ 步骤渲染 ============================
def indicator_delta(before, after):
    return (f"单位成本 {before['unit_cost']:.2f}→{after['unit_cost']:.2f}；"
            f"利润 {before['profit']:,.0f}→{after['profit']:,.0f}；"
            f"偏离 {before['deviation']:.1f}%→{after['deviation']:.1f}%；"
            f"绩效 {before['perf']:.0f}→{after['perf']:.0f}")


def commit(delta_msg):
    st.session_state.done.append(st.session_state.step)
    st.session_state.state["notes"][st.session_state.step] = delta_msg
    st.session_state.step += 1
    st.success(delta_msg)
    st.rerun()


current = st.session_state.step

# ---------- 步骤 1 · 开局签约 ----------
if current == 1:
    st.markdown("### 第 1 步 · 开局签约（模块 A）")
    st.markdown("**场景**：你是公司财务经理，开工前与团队确定经营目标。设定目标利润率，确定基准售价。")
    before = compute(st.session_state.state)
    rate = st.slider("目标利润率（%）", 5, 40, 15, key="s1_rate")
    price = st.slider("产品售价（元/件）", 200, 1000, int(st.session_state.state["price"]), key="s1_price")
    if st.button("确认本步（签约定价）"):
        st.session_state.state["target_rate"] = rate / 100.0
        st.session_state.state["price"] = float(price)
        after = compute(st.session_state.state)
        commit(f"已签约：目标利润率 {rate}%，售价 ¥{price}/件。" + indicator_delta(before, after))

# ---------- 步骤 2 · 采购 ----------
elif current == 2:
    st.markdown("### 第 2 步 · 材料采购（模块 A）")
    st.markdown("**场景**：你是采购员。三家供应商价格/质量/交期不同，选择影响直接材料成本与潜在返工。")
    before = compute(st.session_state.state)
    s = st.radio("选择供应商", list(SUPPLIERS.keys()),
                 help="S1 均衡 · S2 优质但贵 · S3 便宜但质量差")
    for k, v in SUPPLIERS.items():
        st.caption(f"**{k}**：¥{v['price']}/kg，质量「{v['quality']}」，{v['tag']}")
    if st.button("确认本步（确定供应商）"):
        v = SUPPLIERS[s]
        st.session_state.state["supplier"] = s
        st.session_state.state["mat_price"] = v["price"]
        st.session_state.state["quality"] = v["quality"]
        after = compute(st.session_state.state)
        commit(f"已选供应商 {s}（¥{v['price']}/kg，{v['quality']}）。" + indicator_delta(before, after))

# ---------- 步骤 3 · 入库 ----------
elif current == 3:
    st.markdown("### 第 3 步 · 材料入库（模块 A）")
    st.markdown("**场景**：设定本次采购单价与数量，确定直接材料总额。")
    before = compute(st.session_state.state)
    mp = st.slider("材料单价（元/kg）", 5.0, 20.0, float(st.session_state.state["mat_price"]), step=0.5, key="s3_mp")
    mq = st.slider("采购数量（kg）", 1000, 10000, int(st.session_state.state["mat_qty"]), step=100, key="s3_mq")
    st.caption(f"直接材料总额 = {mp} × {mq} × 质量系数({QUALITY[st.session_state.state['quality']]}) = "
               f"¥{mp*mq*QUALITY[st.session_state.state['quality']]:,.0f}")
    if st.button("确认本步（材料入库）"):
        st.session_state.state["mat_price"] = float(mp)
        st.session_state.state["mat_qty"] = int(mq)
        after = compute(st.session_state.state)
        commit(f"入库：单价¥{mp}/kg × {mq}kg。直接材料 ¥{after['material_total']:,.0f}。" + indicator_delta(before, after))

# ---------- 步骤 4 · 领料 ----------
elif current == 4:
    st.markdown("### 第 4 步 · 生产领料（模块 A）")
    st.markdown("**场景**：投料方式决定在产品材料完工程度，进而影响约当产量与完工/在产成本分配。")
    before = compute(st.session_state.state)
    mode = st.radio("选择投料方式", list(TRAIN_MODE.keys()))
    st.caption("一次投入：在产品材料完工程度 100%；分工序分次投入：约 50%。")
    if st.button("确认本步（确定投料方式）"):
        st.session_state.state["material_done"] = TRAIN_MODE[mode]
        after = compute(st.session_state.state)
        commit(f"投料方式：{mode}（材料完工程度 {TRAIN_MODE[mode]}）。" + indicator_delta(before, after))

# ---------- 步骤 5 · 人工 ----------
elif current == 5:
    st.markdown("### 第 5 步 · 人工投入（模块 A）")
    st.markdown("**场景**：设定本月工时与工资率，直接人工 = 工时 × 工资率。")
    before = compute(st.session_state.state)
    h = st.slider("工时（h）", 1000, 6000, int(st.session_state.state["labor_hours"]), step=100, key="s5_h")
    w = st.slider("工资率（元/h）", 15, 35, int(st.session_state.state["wage"]), key="s5_w")
    st.caption(f"直接人工 = {h} × {w} = ¥{h*w:,.0f}")
    if st.button("确认本步（确定人工成本）"):
        st.session_state.state["labor_hours"] = int(h)
        st.session_state.state["wage"] = float(w)
        after = compute(st.session_state.state)
        commit(f"直接人工 ¥{after['labor_total']:,.0f}（{h}h × ¥{w}）。" + indicator_delta(before, after))

# ---------- 步骤 6 · 制造费用 ----------
elif current == 6:
    st.markdown("### 第 6 步 · 制造费用（模块 A）")
    st.markdown("**场景**：选择制造费用分摊基数并设定总额，制造费用计入加工成本。")
    before = compute(st.session_state.state)
    base = st.radio("分摊基数", ["人工工时", "机器工时", "产量"])
    mfg = st.slider("制造费用总额（元）", 20000, 120000, int(st.session_state.state["mfg_total"]), step=1000, key="s6_mfg")
    if st.button("确认本步（确定制造费用）"):
        st.session_state.state["mfg_base"] = base
        st.session_state.state["mfg_total"] = float(mfg)
        after = compute(st.session_state.state)
        commit(f"制造费用 ¥{mfg:,.0f}，分摊基数：{base}。" + indicator_delta(before, after))

# ---------- 步骤 7 · 约当产量 ----------
elif current == 7:
    st.markdown("### 第 7 步 · 约当产量（模块 A）")
    st.markdown("**场景**：设定完工/在产品数量与加工完工程度，计算材料/加工约当产量。")
    before = compute(st.session_state.state)
    fin = st.slider("完工产品数量", 0, 600, int(st.session_state.state["finished"]), step=10, key="s7_fin")
    wipn = st.slider("月末在产品数量", 0, 400, int(st.session_state.state["wip"]), step=10, key="s7_wip")
    pdone = st.slider("加工完工程度（%）", 0, 100, int(st.session_state.state["proc_done"] * 100), key="s7_pd")
    st.caption(f"材料完工程度 {st.session_state.state['material_done']}；加工约当 = {wipn} × {pdone}%")
    if st.button("确认本步（确定产量与完工程度）"):
        st.session_state.state["finished"] = int(fin)
        st.session_state.state["wip"] = int(wipn)
        st.session_state.state["proc_done"] = pdone / 100.0
        after = compute(st.session_state.state)
        commit(f"完工 {fin} 件、在产品 {wipn} 件，加工完工程度 {pdone}%。" + indicator_delta(before, after))

# ---------- 步骤 8 · 品种法 ----------
elif current == 8:
    st.markdown("### 第 8 步 · 品种法核算（模块 A）")
    st.markdown("**场景**：归集要素费用，用约当产量法计算完工产品与月末在产品成本。")
    rows = pd.DataFrame({
        "项目": ["直接材料总额", "直接人工", "制造费用", "材料约当产量", "加工约当产量",
                "材料单位成本", "加工单位成本", "单位产品成本", "完工产品成本", "月末在产品成本"],
        "金额/数量": [f"¥{r['material_total']:,.0f}", f"¥{r['labor_total']:,.0f}",
                  f"¥{r['processing_total']-r['labor_total']:,.0f}",
                  f"{r['mat_eq']:.0f}", f"{r['proc_eq']:.0f}",
                  f"¥{r['mat_unit']:.2f}", f"¥{r['proc_unit']:.2f}",
                  f"¥{r['unit_cost']:.2f}", f"¥{r['finished_cost']:,.2f}", f"¥{r['wip_cost']:,.2f}"],
    })
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"成本合计 ¥{r['total_cost']:,.0f} 与要素费用合计一致：{r['total_cost'] - (r['material_total']+r['processing_total']) < 0.01}")
    if st.button("确认本步（完成品种法核算）"):
        commit(f"单位产品成本 ¥{r['unit_cost']:.2f}，完工成本 ¥{r['finished_cost']:,.0f}，在产品 ¥{r['wip_cost']:,.0f}。")

# ---------- 步骤 9 · 量本利 ----------
elif current == 9:
    st.markdown("### 第 9 步 · 量本利分析（模块 B）")
    st.markdown("**场景**：调整售价与销量，测算保本点与经营利润（量本利决策）。")
    before = compute(st.session_state.state)
    price = st.slider("售价（元/件）", 200, 1000, int(st.session_state.state["price"]), key="s9_price")
    sales = st.slider("销量（件）", 100, 600, int(st.session_state.state["finished"]), step=10, key="s9_sales")
    vc = st.session_state.state["standard_cost"]
    bep = price - vc
    st.caption(f"贡献毛益 ≈ ¥{bep:.0f}/件；保本销量 ≈ {('%.0f' % (r['processing_total']/bep)) if bep>0 else '—'} 件")
    if st.button("确认本步（完成量本利决策）"):
        st.session_state.state["price"] = float(price)
        st.session_state.state["finished"] = int(sales)
        after = compute(st.session_state.state)
        commit(f"售价 ¥{price}/件、销量 {sales} 件。经营利润 ¥{after['profit']:,.0f}。" + indicator_delta(before, after))

# ---------- 步骤 10 · 产销情境 ----------
elif current == 10:
    st.markdown("### 第 10 步 · 产销情境（模块 B）")
    st.markdown("**场景**：不同产销情境下，固定制造费用是否被存货吸收，导致利润差异。")
    before = compute(st.session_state.state)
    sc = st.radio("选择产销情境", ["产销平衡", "存货增加（产量>销量）", "销售下滑（产量不变）"])
    if st.button("确认本步（确定产销情境）"):
        st.session_state.state["scenario"] = sc
        adj = {"产销平衡": 0.0, "存货增加（产量>销量）": 0.08, "销售下滑（产量不变）": -0.12}[sc]
        st.session_state.state["standard_cost"] = max(200, st.session_state.state["standard_cost"] * (1 + adj))
        after = compute(st.session_state.state)
        commit(f"情境：{sc}。固定成本被存货吸收情况变化，偏离指数变动。" + indicator_delta(before, after))

# ---------- 步骤 11 · 标准成本 ----------
elif current == 11:
    st.markdown("### 第 11 步 · 标准成本（模块 B）")
    st.markdown("**场景**：设定标准料工费，作为成本偏离指数与责任绩效分的基准。")
    before = compute(st.session_state.state)
    std = st.slider("标准成本（元/件）", 200, 800, int(st.session_state.state["standard_cost"]), key="s11_std")
    if st.button("确认本步（确定标准成本）"):
        st.session_state.state["standard_cost"] = float(std)
        after = compute(st.session_state.state)
        commit(f"标准成本 ¥{std}/件。成本偏离指数 {after['deviation']:.1f}%（{deviation_color(after['deviation'])}）。"
               + indicator_delta(before, after))

# ---------- 步骤 12 · 责任中心 ----------
elif current == 12:
    st.markdown("### 第 12 步 · 责任中心（模块 B）")
    st.markdown("**场景**：划分成本中心/利润中心并落实责任，决定责任绩效分。")
    before = compute(st.session_state.state)
    rs = st.radio("责任划分方式", ["合理划分到责任中心", "部分合理部分模糊", "全部推给他人"])
    if st.button("确认本步（划分责任中心）"):
        st.session_state.state["responsibility"] = rs
        penalty = {"合理划分到责任中心": 0.0, "部分合理部分模糊": 5.0, "全部推给他人": 20.0}[rs]
        base = compute(st.session_state.state)["perf"]
        st.session_state.state["resp_penalty"] = penalty
        st.session_state.state["perf_adj"] = base - penalty
        commit(f"责任划分：{rs}（责任绩效扣减 {penalty:.0f} 分）。当前绩效约 {base-penalty:.0f} 分。")

# ---------- 步骤 13 · 金点子 ----------
elif current == 13:
    st.markdown("### 第 13 步 · 降本金点子（模块 C）")
    st.markdown("**场景**：为提升竞争力提交降本增效方案，系统从创新性/可操作性/成本影响/业财融合四维评分。")
    text = st.text_area("输入你的降本增效方案（如：改用优质料降低返工率、优化排产减少工时……）",
                        value=st.session_state.state["suggestion"], height=120)
    if st.button("提交方案并评分"):
        st.session_state.state["suggestion"] = text
        keywords = ["降本", "返工", "排产", "工时", "供应链", "质检", "采购", "产能", "存货", "定价"]
        hit = sum(1 for k in keywords if k in text)
        creativity = min(100, 40 + hit * 6)
        operability = min(100, 40 + len(text) // 6)
        cost_impact = min(100, 30 + hit * 7)
        business = min(100, 30 + hit * 6)
        score = 0.30 * creativity + 0.30 * operability + 0.25 * cost_impact + 0.15 * business
        st.session_state.state["idea_score"] = round(score, 1)
        commit(f"方案评分 {score:.1f}/100（创新{creativity:.0f}·可操作{operability:.0f}·成本影响{cost_impact:.0f}·业财融合{business:.0f}）。")

# ---------- 步骤 14 · 风险事件 ----------
elif current == 14:
    st.markdown("### 第 14 步 · 风险事件（模块 C）")
    st.markdown("**场景**：经营中随机触发风险事件，你需在约束条件下做出应对决策。")
    if "cur_risk" not in st.session_state:
        st.session_state.cur_risk = random.choice([
            ("原材料涨价 20%", "接受涨价并微调售价 / 更换更低价料 / 增加采购量锁价"),
            ("紧急订单插单", "接单加班（增成本） / 拒绝保主单 / 调整排产"),
            ("设备突发故障", "停机检修（产能-30%） / 外协加工 / 加班补产"),
            ("质检发现批量不合格", "返工整改 / 报废重做 / 降价处理"),
            ("客户要求降价 10%", "接受降价降本 / 拒绝维持毛利 / 协商折中"),
        ])
    risk, opts = st.session_state.cur_risk
    parts = [p.strip() for p in opts.split(" / ") if p.strip()]
    st.error(f"⚠️ 风险事件：{risk}")
    choice = st.radio("你的应对决策", parts)
    loss_map = {parts[0]: 1.0}
    if len(parts) >= 2:
        loss_map[parts[1]] = 0.5
    if len(parts) >= 3:
        loss_map[parts[2]] = 0.2
    if st.button("确认应对决策"):
        st.session_state.state["risk"] = risk
        st.session_state.state["risk_loss"] = loss_map.get(choice, 0.5)
        st.session_state.state["events"].append(risk)
        commit(f"应对「{risk}」选择：{choice}。风险损失影响约 {st.session_state.state['risk_loss']}。")

# ---------- 步骤 15 · 红线检查 ----------
elif current == 15:
    st.markdown("### 第 15 步 · 红线检查（模块 C）")
    st.markdown("**场景**：系统检测三类红线。首次触发警告并扣分，第二次直接终止实验。")
    s = st.session_state.state
    checks = []
    if s["mat_price"] > 20:
        checks.append("成本造假（材料单价>20元）")
    if s["wip"] > s["finished"] * 2:
        checks.append("虚增存货（在产品>完工×2）")
    if s.get("responsibility") == "全部推给他人":
        checks.append("责任甩锅（责任全推他人）")
    if checks:
        st.warning("检测到红线：" + "；".join(checks))
    else:
        st.success("未触发任何红线，核算规范。")
    if st.button("确认检查结果（提交判定）"):
        for c in checks:
            key = c.split("（")[0]
            if key in s["redlines"]:
                s["redlines"][key] += 1
        commit("红线检查完成。" + ("触发：" + "；".join(checks) if checks else "无红线，合规。"))

# ---------- 步骤 16 · 经营决策 ----------
elif current == 16:
    st.markdown("### 第 16 步 · 经营决策（模块 C · 终结）")
    st.markdown("**场景**：综合全部分析，出具定价 / 排产 / 考核建议书，并给出终结性评分。")
    s = st.session_state.state
    rr = compute(s)
    perf = rr["perf"] - s.get("perf_adj", 0)
    risk_ded = s.get("risk_loss", 0.0) * 6
    idea = s.get("idea_score") or 0
    red_ded = sum(s["redlines"].values()) * 30
    final = max(0, round(0.5 * perf + 0.3 * idea + 0.2 * (100 - risk_ded) - red_ded, 1))
    st.markdown(f"""
**经营决策建议书**
- **定价**：单位成本 ¥{rr['unit_cost']:.2f}，售价 ¥{s['price']:.0f}/件，毛利 ¥{s['price']-rr['unit_cost']:.2f}/件
- **排产**：完工 {s['finished']} 件 / 在产 {s['wip']} 件，成本偏离 {rr['deviation']:.1f}%（{deviation_color(rr['deviation'])}）
- **考核**：责任绩效 {perf:.0f} 分；降本方案 {idea:.0f} 分；风险损失扣 {risk_ded:.0f}；红线扣 {red_ded:.0f}
""")
    st.metric("终结性评分", f"{final} / 100")
    if st.button("完成实训（生成成绩）"):
        st.session_state.finished = True
        commit(f"实训完成！终结性评分 {final}/100。")

# ---------- 完成页 ----------
if st.session_state.finished and current > TOTAL_STEPS:
    st.success("🎉 恭喜完成全部 16 步虚拟仿真实训！")
    s = st.session_state.state
    rr = compute(s)
    st.markdown("#### 实训复盘")
    notes = s["notes"]
    df = pd.DataFrame({
        "步骤": list(notes.keys()),
        "记录": [str(v) for v in notes.values()],
    })
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption(f"四指标终态：单位成本 ¥{rr['unit_cost']:.2f} · 经营利润 ¥{rr['profit']:,.0f} · "
               f"成本偏离 {rr['deviation']:.1f}% · 责任绩效 {rr['perf']:.0f}")
