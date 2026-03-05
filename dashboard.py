"""
Clara AI Zentrades -- Operations Dashboard
Run: python -m streamlit run dashboard.py
"""
import os, json, streamlit as st
from datetime import datetime

st.set_page_config(page_title="Clara AI Zentrades", page_icon="🎙", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.stApp{background:#0d1117;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#161b22 0%,#0d1117 100%)!important;border-right:1px solid #21262d;}
[data-testid="metric-container"]{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px 20px;}
[data-testid="metric-container"] label{color:#8b949e!important;font-size:0.7rem!important;text-transform:uppercase;letter-spacing:1px;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#e6edf3!important;font-size:1.8rem!important;font-weight:700!important;}
[data-testid="stVerticalBlockBorderWrapper"]{background:#161b22!important;border:1px solid #21262d!important;border-radius:12px!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent;border-bottom:1px solid #21262d;gap:2px;}
.stTabs [data-baseweb="tab"]{background:transparent;color:#8b949e;border-radius:8px 8px 0 0;padding:8px 18px;font-size:0.83rem;font-weight:500;}
.stTabs [aria-selected="true"]{background:#1c2333!important;color:#58a6ff!important;border-bottom:2px solid #58a6ff!important;}
.stProgress>div>div{background:#21262d;border-radius:6px;height:8px!important;}
.stProgress>div>div>div{border-radius:6px;background:linear-gradient(90deg,#1f6feb 0%,#58a6ff 100%)!important;height:8px!important;}
.stSuccess{background:rgba(35,134,54,0.12)!important;border:1px solid rgba(35,134,54,0.35)!important;border-radius:8px!important;color:#3fb950!important;}
.stWarning{background:rgba(187,128,9,0.12)!important;border:1px solid rgba(187,128,9,0.35)!important;border-radius:8px!important;color:#d29922!important;}
.stError{background:rgba(218,54,51,0.12)!important;border:1px solid rgba(218,54,51,0.35)!important;border-radius:8px!important;color:#f85149!important;}
.stInfo{background:rgba(31,111,235,0.12)!important;border:1px solid rgba(31,111,235,0.35)!important;border-radius:8px!important;color:#58a6ff!important;}
code{background:#0d1117!important;border:1px solid #21262d!important;border-radius:6px!important;color:#79c0ff!important;font-size:0.78rem!important;}
h1,h2,h3{color:#e6edf3!important;}
p,li{color:#c9d1d9;}
hr{border-color:#21262d!important;margin:12px 0;}
.stSelectbox>div>div{background:#161b22!important;border-color:#30363d!important;color:#e6edf3!important;border-radius:8px!important;}
</style>
""", unsafe_allow_html=True)

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(ROOT,"outputs","accounts")
CHANGELOG_DIR = os.path.join(ROOT,"changelog")
REPORTS_DIR = os.path.join(ROOT,"outputs","reports")
TASK_LOG = os.path.join(ROOT,"outputs","task_log.json")
TRANS_DEMO = os.path.join(ROOT,"transcripts","demo")
TRANS_OB = os.path.join(ROOT,"transcripts","onboarding")

def jsafe(path):
    try:
        if os.path.exists(path):
            with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except: pass
    return None

def rfile(path):
    try:
        if os.path.exists(path):
            with open(path,"r",encoding="utf-8") as f: return f.read()
    except: pass
    return ""

def fv(memo,*keys):
    obj=memo
    for k in keys:
        if not isinstance(obj,dict): return ""
        obj=obj.get(k,{})
    if isinstance(obj,dict): return obj.get("value","") or ""
    return str(obj) if obj else ""

def fc(memo,*keys):
    obj=memo
    for k in keys:
        if not isinstance(obj,dict): return ""
        obj=obj.get(k,{})
    if isinstance(obj,dict): return obj.get("confidence","") or ""
    return ""

def fl(memo,*keys):
    obj=memo
    for k in keys:
        if not isinstance(obj,dict): return []
        obj=obj.get(k,{})
    if isinstance(obj,dict):
        v=obj.get("value",[])
        return v if isinstance(v,list) else []
    return []

def load_accounts():
    accts=[]
    if not os.path.exists(BASE): return accts
    for a in sorted(os.listdir(BASE)):
        p=os.path.join(BASE,a)
        if not os.path.isdir(p): continue
        v1m=jsafe(os.path.join(p,"v1","memo.json"))
        v2m=jsafe(os.path.join(p,"v2","memo.json"))
        memo=v2m or v1m
        company=fv(memo,"company_name") if memo else a
        accts.append({
            "account_id":a,"company_name":company or a,
            "v1_memo":v1m,"v2_memo":v2m,
            "v1_agent":jsafe(os.path.join(p,"v1","agent_spec.json")),
            "v2_agent":jsafe(os.path.join(p,"v2","agent_spec.json")),
            "v1_val":jsafe(os.path.join(p,"v1","validation.json")),
            "v2_val":jsafe(os.path.join(p,"v2","validation.json")),
            "v1_score":(jsafe(os.path.join(p,"v1","completeness.json")) or {}).get("score_percent",0),
            "v2_score":(jsafe(os.path.join(p,"v2","completeness.json")) or {}).get("score_percent",0),
            "v1_history":jsafe(os.path.join(p,"v1","transcript_history.json")) or [],
            "v2_history":jsafe(os.path.join(p,"v2","transcript_history.json")) or [],
            "changelog":jsafe(os.path.join(CHANGELOG_DIR,a+"_changes.json")) or {},
        })
    return accts

accounts=load_accounts()
task_log=jsafe(TASK_LOG) or []
batch_results=jsafe(os.path.join(REPORTS_DIR,"batch_results.json")) or []

with st.sidebar:
    st.markdown("## 🎙 Clara AI Zentrades")
    st.caption("VOICE AGENT OPERATIONS PLATFORM")
    st.divider()
    page=st.radio("",["📊  Overview","🏢  Account Detail","🔀  Diff Viewer","📋  Task Log","📈  Batch Report"],label_visibility="collapsed")
    st.divider()
    total=len(accounts)
    with_v2=sum(1 for a in accounts if a["v2_memo"])
    avg_v2=round(sum(a["v2_score"] for a in accounts if a["v2_memo"])/max(with_v2,1),1)
    avg_v1=round(sum(a["v1_score"] for a in accounts)/max(total,1),1)
    st.caption("PIPELINE STATS")
    ca,cb=st.columns(2)
    ca.metric("Accounts",total); cb.metric("With v2",with_v2)
    ca2,cb2=st.columns(2)
    ca2.metric("Avg v1",str(avg_v1)+"%"); cb2.metric("Avg v2",str(avg_v2)+"%")
    if accounts:
        st.divider()
        st.caption("SELECT ACCOUNT")
        acct_names={a["account_id"]:a["company_name"] for a in accounts}
        selected_id=st.selectbox("",list(acct_names.keys()),format_func=lambda x:acct_names[x],label_visibility="collapsed")
    st.divider()
    st.caption("Updated: "+datetime.now().strftime("%b %d %Y %H:%M"))

if not accounts:
    st.title("🎙 Clara AI Zentrades")
    st.info("No accounts found. Run `python scripts/main.py` first.")
    st.stop()

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
if "Overview" in page:
    st.markdown("# 📊 Pipeline Overview")
    st.caption("All configured voice agent accounts  ·  "+datetime.now().strftime("%B %d, %Y"))
    st.divider()
    err_count=sum(1 for a in accounts if a.get("v2_val") and a["v2_val"].get("errors"))
    warn_count=sum(1 for a in accounts if a.get("v2_val") and a["v2_val"].get("warnings"))
    total_changes=sum(len(a["changelog"]) for a in accounts)
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Total Accounts",total)
    c2.metric("Fully Configured",with_v2,delta=str(with_v2)+"/"+str(total)+" complete")
    c3.metric("Avg v2 Score",str(avg_v2)+"%",delta="+"+str(round(avg_v2-avg_v1,1))+"% from v1")
    c4.metric("Warnings",warn_count)
    c5.metric("Total Changes",total_changes)
    st.divider()
    for acct in accounts:
        memo=acct["v2_memo"] or acct["v1_memo"]
        v2=acct["v2_memo"]
        has_err=bool(acct.get("v2_val") and acct["v2_val"].get("errors"))
        has_warn=bool(acct.get("v2_val") and acct["v2_val"].get("warnings"))
        warn_n=len(acct["v2_val"]["warnings"]) if has_warn else 0
        services=fl(memo,"services_supported") if memo else []
        phone=fv(memo,"phone_number") if memo else ""
        tz=fv(memo,"business_hours","timezone") if memo else ""
        days=fv(memo,"business_hours","days") if memo else ""
        start=fv(memo,"business_hours","start") if memo else ""
        end_h=fv(memo,"business_hours","end") if memo else ""
        with st.container(border=True):
            r1,r2,r3=st.columns([4,2,2])
            with r1:
                st.markdown("### "+acct["company_name"])
                st.caption("  ·  ".join(filter(None,[acct["account_id"],phone,tz])))
            with r2:
                if days and start and end_h:
                    st.caption("BUSINESS HOURS")
                    st.write("**"+start+" - "+end_h+"**")
                    st.caption(days)
            with r3:
                if v2: st.success("v1 + v2 Complete")
                else: st.warning("v1 Only - Awaiting Onboarding")
                if has_err: st.error(str(len(acct["v2_val"]["errors"]))+" error(s)")
            if services:
                st.caption("SERVICES")
                svc_cols=st.columns(min(len(services),7))
                for idx,svc in enumerate(services[:7]): svc_cols[idx].info(svc)
            st.write("")
            sc1,sc2,sc3,sc4=st.columns(4)
            sc1.caption("V2 COMPLETENESS  "+str(acct["v2_score"])+"%")
            sc1.progress(int(acct["v2_score"])/100)
            sc2.caption("V1 BASELINE  "+str(acct["v1_score"])+"%")
            sc2.progress(int(acct["v1_score"])/100)
            sc3.caption("FIELDS UPDATED")
            sc3.metric("",str(len(acct["changelog"])),label_visibility="collapsed")
            with sc4:
                if has_warn: st.warning(str(warn_n)+" warning(s)")
                else: st.success("No warnings")

# ── ACCOUNT DETAIL ────────────────────────────────────────────────────────────
elif "Account" in page:
    acct_map={a["account_id"]:a for a in accounts}
    acct=acct_map.get(selected_id)
    if not acct: st.error("Account not found."); st.stop()
    v1=acct["v1_memo"]; v2=acct["v2_memo"]; memo=v2 or v1
    agent=acct["v2_agent"] or acct["v1_agent"]
    st.markdown("# 🏢 "+acct["company_name"])
    st.caption(acct["account_id"]+"  ·  Active: "+("v2 - Onboarding confirmed" if v2 else "v1 - Demo only"))
    st.divider()
    m1,m2,m3,m4=st.columns(4)
    m1.metric("v1 Score",str(acct["v1_score"])+"%")
    m2.metric("v2 Score",str(acct["v2_score"])+"%",delta="+"+str(round(acct["v2_score"]-acct["v1_score"],1))+"%")
    m3.metric("Fields Updated",len(acct["changelog"]))
    m4.metric("Open Questions",len(memo.get("questions_or_unknowns",[]) if memo else []))
    st.divider()
    tab1,tab2,tab3,tab4,tab5=st.tabs(["Configuration","Agent Spec","Validation","Transcripts","Raw JSON"])

    with tab1:
        col1,col2=st.columns(2)
        with col1:
            with st.container(border=True):
                st.caption("BUSINESS INFO")
                st.write("**Company:** "+acct["company_name"])
                st.write("**Phone:** "+(fv(memo,"phone_number") or "not extracted"))
                st.write("**Address:** "+(fv(memo,"office_address") or "not extracted"))
            with st.container(border=True):
                st.caption("BUSINESS HOURS")
                st.write("**Days:** "+(fv(memo,"business_hours","days") or "—"))
                st.write("**Hours:** "+(fv(memo,"business_hours","start") or "—")+" - "+(fv(memo,"business_hours","end") or "—"))
                tz_val=fv(memo,"business_hours","timezone"); tz_conf=fc(memo,"business_hours","timezone")
                tza,tzb=st.columns([2,1])
                tza.write("**Timezone:** "+(tz_val or "—"))
                if tz_conf=="confirmed": tzb.success("confirmed")
                elif tz_conf=="demo_assumed": tzb.warning("assumed")
            with st.container(border=True):
                st.caption("CALL TRANSFER RULES")
                st.write("**Primary:** "+(fv(memo,"call_transfer_rules","primary_number") or "—"))
                st.write("**Secondary:** "+(fv(memo,"call_transfer_rules","secondary_number") or "—"))
                st.write("**Timeout:** "+(fv(memo,"call_transfer_rules","timeout_seconds") or "—")+"s")
                fm=fv(memo,"call_transfer_rules","failure_message")
                if fm: st.caption("FALLBACK MESSAGE"); st.info('"'+fm+'"')
            with st.container(border=True):
                st.caption("FLOW SUMMARIES")
                os_val=fv(memo,"office_hours_flow_summary")
                ah_val=fv(memo,"after_hours_flow_summary")
                if os_val: st.caption("Office Hours"); st.write(os_val)
                if ah_val: st.caption("After Hours"); st.write(ah_val)
                if not os_val and not ah_val: st.caption("Not generated yet")
        with col2:
            with st.container(border=True):
                st.caption("EMERGENCY DEFINITIONS")
                em=fl(memo,"emergency_definition")
                em_conf=fc(memo,"emergency_definition")
                for e in em: st.error("🔴  "+e)
                if not em: st.warning("Not specified")
                elif em_conf: st.caption("Confidence: "+em_conf)
            with st.container(border=True):
                st.caption("SERVICES SUPPORTED")
                svc=fl(memo,"services_supported")
                if svc:
                    cols=st.columns(min(len(svc),3))
                    for idx,s in enumerate(svc): cols[idx%3].info(s)
                else: st.caption("Not specified")
            with st.container(border=True):
                st.caption("NON-EMERGENCY ROUTING")
                ne=fv(memo,"non_emergency_routing_rules")
                if ne: st.write(ne)
                else: st.warning("Not defined")
            with st.container(border=True):
                st.caption("INTEGRATION CONSTRAINTS")
                cons=fl(memo,"integration_constraints")
                for c in cons: st.warning("  "+c)
                if not cons: st.success("No constraints")
            with st.container(border=True):
                st.caption("OPEN QUESTIONS")
                unk=memo.get("questions_or_unknowns",[]) if memo else []
                for u in unk: st.warning("?  "+u)
                if not unk: st.success("No open questions")

    with tab2:
        if not agent: st.info("No agent spec. Run pipeline first.")
        else:
            mc1,mc2=st.columns([1,2])
            with mc1:
                with st.container(border=True):
                    st.caption("AGENT METADATA")
                    for k,v in {"Name":agent.get("agent_name","—"),"Voice":agent.get("voice_style","—"),"Language":agent.get("language","—"),"Version":agent.get("version","—"),"Generated":str(agent.get("generated_at","—"))[:10]}.items():
                        a1,b1=st.columns([1,2]); a1.caption(k); b1.write(str(v))
                with st.container(border=True):
                    st.caption("TRANSFER PROTOCOL")
                    tp=agent.get("call_transfer_protocol",{})
                    for k,v in {"Primary":tp.get("primary_number","—"),"Secondary":tp.get("secondary_number","—") or "—","Timeout":str(tp.get("timeout_seconds","—"))+"s","Attempts":tp.get("max_attempts","—")}.items():
                        a1,b1=st.columns([1,2]); a1.caption(k); b1.write(str(v))
                st.write("")
                st.download_button("Download Agent Spec JSON",data=json.dumps(agent,indent=2,ensure_ascii=False),file_name=acct["account_id"]+"_agent_spec.json",mime="application/json",use_container_width=True)
            with mc2:
                with st.container(border=True):
                    st.caption("SYSTEM PROMPT")
                    st.code(agent.get("system_prompt","No prompt generated."),language=None)

    with tab3:
        vc1,vc2=st.columns(2)
        for col,ver,vd in [(vc1,"v1",acct["v1_val"]),(vc2,"v2",acct["v2_val"])]:
            with col:
                with st.container(border=True):
                    lbl="DEMO" if ver=="v1" else "ONBOARDING"
                    st.caption(lbl+" VALIDATION -- "+ver.upper())
                    if not vd: st.caption("No data available"); continue
                    errs=vd.get("errors",[]); warns=vd.get("warnings",[])
                    if not errs and not warns: st.success(ver.upper()+" -- All checks passed")
                    elif vd.get("is_valid"): st.success(ver.upper()+" -- Valid")
                    else: st.error(ver.upper()+" -- Has blocking errors")
                    for e in errs: st.error(e)
                    for w in warns: st.warning(w)
        st.divider()
        sc1,sc2,sc3=st.columns(3)
        sc1.caption("V1 COMPLETENESS"); sc1.progress(int(acct["v1_score"])/100); sc1.write("**"+str(acct["v1_score"])+"%**")
        sc2.caption("V2 COMPLETENESS"); sc2.progress(int(acct["v2_score"])/100); sc2.write("**"+str(acct["v2_score"])+"%**")
        diff_s=round(acct["v2_score"]-acct["v1_score"],1)
        sc3.caption("IMPROVEMENT"); sc3.metric("",("+" if diff_s>=0 else "")+str(diff_s)+"%",label_visibility="collapsed")
        st.divider()
        st.caption("TRANSCRIPT VERSION HISTORY")
        hc1,hc2=st.columns(2)
        for col,lbl,hist in [(hc1,"Demo (v1)",acct["v1_history"]),(hc2,"Onboarding (v2)",acct["v2_history"])]:
            with col:
                with st.container(border=True):
                    st.caption(lbl.upper())
                    if hist:
                        for entry in hist:
                            st.write("**v"+str(entry.get("version",""))+"**  "+str(entry.get("timestamp",""))[:16])
                            st.caption("Hash: "+str(entry.get("hash",""))[:16]+"...")
                    else: st.caption("No history yet")

    with tab4:
        st.caption("RAW TRANSCRIPT SOURCE FILES")
        tc1,tc2=st.columns(2)
        with tc1:
            with st.container(border=True):
                st.caption("DEMO CALL TRANSCRIPT")
                demo_text=rfile(os.path.join(TRANS_DEMO,acct["account_id"]+"_demo.txt"))
                if demo_text:
                    st.code(demo_text,language=None)
                    st.download_button("Download Demo Transcript",data=demo_text,file_name=acct["account_id"]+"_demo.txt",mime="text/plain")
                else: st.info("Not found")
        with tc2:
            with st.container(border=True):
                st.caption("ONBOARDING CALL TRANSCRIPT")
                ob_text=rfile(os.path.join(TRANS_OB,acct["account_id"]+"_onboarding.txt"))
                if ob_text:
                    st.code(ob_text,language=None)
                    st.download_button("Download Onboarding Transcript",data=ob_text,file_name=acct["account_id"]+"_onboarding.txt",mime="text/plain")
                else: st.info("Not found")

    with tab5:
        c1,c2=st.columns(2)
        with c1:
            with st.container(border=True):
                st.caption("V1 MEMO")
                st.json(v1 or {})
                if v1: st.download_button("Download v1 Memo",data=json.dumps(v1,indent=2,ensure_ascii=False),file_name=acct["account_id"]+"_memo_v1.json",mime="application/json")
        with c2:
            with st.container(border=True):
                st.caption("V2 MEMO")
                st.json(v2 or {})
                if v2: st.download_button("Download v2 Memo",data=json.dumps(v2,indent=2,ensure_ascii=False),file_name=acct["account_id"]+"_memo_v2.json",mime="application/json")

# ── DIFF VIEWER ───────────────────────────────────────────────────────────────
elif "Diff" in page:
    acct_map={a["account_id"]:a for a in accounts}
    acct=acct_map.get(selected_id)
    if not acct: st.error("Account not found."); st.stop()
    changelog=acct["changelog"]
    st.markdown("# 🔀 Diff Viewer -- "+acct["company_name"])
    st.caption(acct["account_id"]+"  ·  Field changes from v1 to v2")
    st.divider()
    dm1,dm2,dm3,dm4=st.columns(4)
    dm1.metric("Account",acct["company_name"])
    dm2.metric("Fields Changed",len(changelog))
    dm3.metric("v1 Score",str(acct["v1_score"])+"%")
    dm4.metric("v2 Score",str(acct["v2_score"])+"%",delta="+"+str(round(acct["v2_score"]-acct["v1_score"],1))+"%")
    st.divider()
    if not changelog:
        st.info("No changes detected between v1 and v2 for this account.")
    else:
        st.caption("SHOWING "+str(len(changelog))+" CHANGE(S)  ·  RED = BEFORE (v1)  ·  GREEN = AFTER (v2)")
        st.write("")
        hc1,hc2,hc3,hc4=st.columns([2,3,3,2])
        hc1.caption("FIELD"); hc2.caption("BEFORE (v1)"); hc3.caption("AFTER (v2)"); hc4.caption("CONFIDENCE")
        st.divider()
        for field,change in changelog.items():
            old_v=change.get("old","—"); new_v=change.get("new","—")
            conf_c=change.get("confidence_change","")
            if isinstance(old_v,list): old_v="\n".join("- "+str(x) for x in old_v) or "—"
            if isinstance(new_v,list): new_v="\n".join("- "+str(x) for x in new_v) or "—"
            with st.container(border=True):
                fc1,fc2,fc3,fc4=st.columns([2,3,3,2])
                fc1.code(field,language=None)
                fc2.error(str(old_v) if old_v else "empty")
                fc3.success(str(new_v) if new_v else "empty")
                fc4.caption(conf_c or change.get("reason","onboarding"))
    cl_md=rfile(os.path.join(CHANGELOG_DIR,acct["account_id"]+"_changes.md"))
    if cl_md:
        st.divider()
        st.download_button("Download Changelog (.md)",data=cl_md,file_name=acct["account_id"]+"_changes.md",mime="text/markdown")
    st.divider()
    st.markdown("### Side-by-side Raw JSON")
    c1,c2=st.columns(2)
    with c1:
        with st.container(border=True):
            st.caption("V1 MEMO"); st.json(acct["v1_memo"] or {})
    with c2:
        with st.container(border=True):
            st.caption("V2 MEMO"); st.json(acct["v2_memo"] or {})

# ── TASK LOG ──────────────────────────────────────────────────────────────────
elif "Task" in page:
    st.markdown("# 📋 Task Tracker")
    st.caption("All pipeline-generated tasks and statuses")
    st.divider()
    if not task_log: st.info("No tasks yet. Run `python scripts/main.py`."); st.stop()
    total_t=len(task_log); open_t=sum(1 for t in task_log if t.get("status")=="open")
    done_t=sum(1 for t in task_log if t.get("status") in ("complete","v2_complete"))
    review_t=sum(1 for t in task_log if t.get("task_type")=="needs_review")
    tm1,tm2,tm3,tm4=st.columns(4)
    tm1.metric("Total Tasks",total_t); tm2.metric("Completed",done_t)
    tm3.metric("Open",open_t); tm4.metric("Needs Review",review_t)
    st.divider()
    fc1,fc2=st.columns(2)
    sf=fc1.selectbox("Status",["All","open","complete","v2_complete"],format_func=lambda x:{"All":"All Statuses","open":"Open","complete":"Complete","v2_complete":"v2 Complete"}.get(x,x))
    tf=fc2.selectbox("Type",["All","v1_generated","v2_updated","needs_review","onboarding_pending"],format_func=lambda x:x.replace("_"," ").title() if x!="All" else "All Types")
    filtered=[t for t in task_log if (sf=="All" or t.get("status")==sf) and (tf=="All" or t.get("task_type")==tf)]
    st.caption("SHOWING "+str(len(filtered))+" OF "+str(total_t)+" TASKS"); st.write("")
    for task in filtered:
        status=task.get("status",""); ttype=task.get("task_type","").replace("_"," ").title()
        with st.container(border=True):
            tc1,tc2,tc3=st.columns([4,1,1])
            with tc1:
                st.markdown("**"+task.get("company_name","")+"**  `"+task.get("task_id","") +"`")
                st.caption(task.get("account_id","")+"  ·  "+ttype)
                if task.get("notes"): st.write(task["notes"])
                st.caption("Created: "+str(task.get("created_at",""))[:16]+"  ·  Updated: "+str(task.get("updated_at",""))[:16])
            with tc2:
                st.caption("TYPE"); st.info(ttype)
            with tc3:
                st.caption("STATUS")
                if status in ("complete","v2_complete"): st.success(status)
                elif status=="open": st.warning(status)
                else: st.info(status)
    st.divider()
    st.download_button("Download Task Log",data=json.dumps(task_log,indent=2,ensure_ascii=False),file_name="task_log.json",mime="application/json")

# ── BATCH REPORT ──────────────────────────────────────────────────────────────
elif "Batch" in page:
    st.markdown("# 📈 Batch Processing Report")
    st.caption("Full pipeline run results across all accounts")
    st.divider()
    if not batch_results: st.info("No batch results. Run `python scripts/main.py`."); st.stop()
    total_b=len(batch_results)
    success_b=sum(1 for r in batch_results if r.get("status")=="success")
    failed_b=sum(1 for r in batch_results if r.get("status")=="failed")
    avg_v1_b=round(sum(r.get("v1_score",0) for r in batch_results)/max(total_b,1),1)
    avg_v2_b=round(sum(r.get("v2_score",0) for r in batch_results)/max(total_b,1),1)
    bm1,bm2,bm3,bm4,bm5=st.columns(5)
    bm1.metric("Total",total_b); bm2.metric("Successful",success_b); bm3.metric("Failed",failed_b)
    bm4.metric("Avg v1",str(avg_v1_b)+"%"); bm5.metric("Avg v2",str(avg_v2_b)+"%",delta="+"+str(round(avg_v2_b-avg_v1_b,1))+"%")
    st.divider()
    for r in batch_results:
        status=r.get("status","")
        with st.container(border=True):
            rc1,rc2,rc3=st.columns([3,2,2])
            with rc1:
                st.markdown("**"+r.get("company_name","Unknown")+"**  `"+r.get("account_id","")+"`")
                for e in r.get("errors",[]): st.error(e)
                if r.get("warnings"): st.warning(str(len(r["warnings"]))+" warning(s)")
            with rc2:
                st.caption("SCORES")
                st.write("v1: **"+str(r.get("v1_score",0))+"%**  to  v2: **"+str(r.get("v2_score",0))+"%**")
                diff_r=round(r.get("v2_score",0)-r.get("v1_score",0),1)
                if diff_r>0: st.success("+"+str(diff_r)+"% improvement")
                elif diff_r==0: st.info("No score change")
            with rc3:
                st.caption("STATUS")
                if status=="success": st.success("Complete")
                elif status=="v1_only": st.warning("v1 Only")
                elif status=="failed": st.error("Failed")
                else: st.info(status)
                st.write("**"+str(r.get("change_count",0))+"** fields updated")
    st.divider()
    report_md=rfile(os.path.join(REPORTS_DIR,"batch_summary.md"))
    if report_md:
        col1,col2=st.columns(2)
        col1.download_button("Download Batch Report (.md)",data=report_md,file_name="batch_summary.md",mime="text/markdown")
        col2.download_button("Download Results JSON",data=json.dumps(batch_results,indent=2,ensure_ascii=False),file_name="batch_results.json",mime="application/json")
