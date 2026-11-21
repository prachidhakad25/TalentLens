import os
import html
import base64
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from api_client import get, post, put, patch, request

load_dotenv()
st.set_page_config(page_title="TalentLens — See Talent Beyond the Resume", page_icon="assets/favicon.svg", layout="wide", initial_sidebar_state="expanded")

FOREST, EMERALD, IVORY, GOLD = "#1F4D3A", "#2F8F6B", "#F8F6EE", "#C9A227"
PHOTO_HERO = "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=2200&q=88"
PHOTO_STUDENTS = "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=85"
PHOTO_OFFICE = "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=85"
PHOTO_TEAM = "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1200&q=85"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@1,600;1,700&display=swap');
:root{{--forest:{FOREST};--emerald:{EMERALD};--ivory:{IVORY};--gold:{GOLD};--ink:#1f2937;--muted:#748078;--line:#e5e9e1;}}
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;}}
.stApp{{background:radial-gradient(ellipse at 85% 5%,rgba(47,143,107,.09),transparent 27%),radial-gradient(ellipse at 5% 80%,rgba(201,162,39,.06),transparent 24%),{IVORY};color:#24362e;}}
[data-testid="stHeader"]{{background:rgba(248,246,238,.76);backdrop-filter:blur(16px);}}
.block-container{{max-width:1500px;padding-top:1.5rem;padding-bottom:3rem;}}
h1,h2,h3,h4{{font-family:'Manrope',sans-serif;color:{FOREST};letter-spacing:-.035em;}}
h1{{font-weight:850;}} h2,h3{{font-weight:800;}}
p{{line-height:1.7;}} a{{color:{EMERALD}!important;}}
[data-testid="stSidebar"]{{background:linear-gradient(180deg,#fffefa,#eef4ed);border-right:1px solid rgba(31,77,58,.1);}}
[data-testid="stSidebar"]>div:first-child{{padding-top:1.1rem;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label{{border-radius:12px;padding:.55rem .7rem;transition:all .22s ease;}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{{background:#e8f1e9;transform:translateX(3px);}}
[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"]{{background:#e8f1e9;color:{FOREST};font-weight:800;}}
.tl-brand{{display:flex;align-items:center;padding:.15rem 0 1.1rem;width:100%;}}
.tl-brand img{{display:block;width:min(100%,270px);height:auto;filter:drop-shadow(0 7px 14px rgba(31,77,58,.08));}}
.hero-photo{{position:relative;isolation:isolate;overflow:hidden;border-radius:30px;padding:4rem 3.5rem;min-height:460px;color:#fff;background-image:linear-gradient(90deg,rgba(8,43,31,.94) 0%,rgba(17,69,49,.82) 48%,rgba(17,69,49,.18) 100%),url('{PHOTO_HERO}');background-size:cover;background-position:center 45%;box-shadow:0 25px 65px rgba(19,67,48,.2);animation:rise .8s cubic-bezier(.2,.8,.2,1) both;margin:.3rem 0 1.5rem;}}
.hero-photo:before{{content:"";position:absolute;z-index:-1;width:420px;height:420px;border:1px solid rgba(255,255,255,.2);border-radius:50%;right:-70px;top:-160px;box-shadow:0 0 0 38px rgba(255,255,255,.04),0 0 0 82px rgba(255,255,255,.025);}}
.hero-copy{{max-width:720px;}}
.hero-kicker{{font-size:.7rem;font-weight:850;letter-spacing:.22em;text-transform:uppercase;color:#d8e7d7;}}
.hero-photo h1{{font-size:clamp(2.7rem,5.4vw,5rem);line-height:1.02;color:white;margin:.8rem 0 1.1rem;max-width:760px;}}
.hero-photo h1 em{{font-family:'Playfair Display',serif;color:#b6e0c7;font-weight:600;}}
.hero-photo p{{font-size:1.08rem;color:#e2eee7;max-width:620px;}}
.float-panel{{position:absolute;right:5%;bottom:12%;width:280px;border:1px solid rgba(255,255,255,.42);border-radius:19px;padding:1rem 1.15rem;background:rgba(255,255,255,.91);color:#1f2937;backdrop-filter:blur(16px);box-shadow:0 18px 45px rgba(0,0,0,.2);animation:float 5s ease-in-out infinite;}}
.float-panel small{{color:#718078;letter-spacing:.12em;font-size:.62rem;font-weight:800;}}
.float-score{{font-family:'Manrope';font-size:2.3rem;font-weight:850;color:{FOREST};}}
.section-kicker{{font-size:.68rem;letter-spacing:.2em;font-weight:850;color:{EMERALD};text-transform:uppercase;}}
.photo-band{{border-radius:24px;overflow:hidden;min-height:250px;background-size:cover;background-position:center;position:relative;display:flex;align-items:end;padding:1.6rem;color:white;box-shadow:0 14px 35px rgba(25,60,44,.13);}}
.photo-band:before{{content:"";position:absolute;inset:0;background:linear-gradient(0deg,rgba(8,43,31,.86),rgba(8,43,31,.04) 80%);}}
.photo-band>*{{position:relative;z-index:1;color:white;}}
.metric{{background:rgba(255,255,255,.9);border:1px solid rgba(31,77,58,.1);border-radius:19px;padding:1.15rem 1.3rem;min-height:120px;box-shadow:0 8px 25px rgba(20,60,40,.045);transition:.25s;animation:rise .65s ease both;}}
.metric:hover{{transform:translateY(-5px);box-shadow:0 18px 35px rgba(20,60,40,.1);border-color:#9ac4a9;}}
.metric-label{{font-size:.8rem;color:#7a8980;font-weight:650;}} .metric-value{{font-family:'Manrope';font-size:2.3rem;font-weight:850;color:{FOREST};}}
.feature-card{{border:1px solid #e5e9e1;background:rgba(255,255,255,.82);border-radius:18px;padding:1.3rem;height:100%;box-shadow:0 8px 22px rgba(25,60,44,.035);transition:.25s;}}
.feature-card:hover{{transform:translateY(-4px);box-shadow:0 16px 30px rgba(25,60,44,.09);}}
div[data-testid="stVerticalBlockBorderWrapper"]{{border-radius:18px!important;border-color:#e4e9e1!important;background:rgba(255,255,255,.82);box-shadow:0 7px 22px rgba(30,60,43,.035);}}
div.stButton>button,div.stFormSubmitButton>button{{background:linear-gradient(110deg,#174b38,#286d50);color:white;border:1px solid transparent;border-radius:12px;padding:.68rem 1.15rem;font-weight:800;box-shadow:0 8px 20px rgba(31,77,58,.13);transition:all .22s ease;}}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{{background:linear-gradient(110deg,#286d50,#36936e);color:white;transform:translateY(-2px);box-shadow:0 13px 26px rgba(31,77,58,.2);}}
div[data-testid="stForm"]{{background:rgba(255,255,255,.88);border:1px solid #e5e9e1;border-radius:20px;padding:1.25rem;box-shadow:0 10px 28px rgba(30,60,43,.04);}}
[data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div{{border-radius:11px!important;border-color:#dfe6dc!important;background:#fffefa!important;}}
[data-baseweb="input"]>div:focus-within,[data-baseweb="textarea"]>div:focus-within{{border-color:#2f8f6b!important;box-shadow:0 0 0 3px rgba(47,143,107,.12)!important;}}
[data-testid="stFileUploader"] section{{border:1.5px dashed #9fc5ad;border-radius:16px;background:#f6faf5;}}
[data-testid="stAlert"]{{border-radius:13px;}}
button[data-baseweb="tab"]{{font-weight:750;}}
button[data-baseweb="tab"][aria-selected="true"]{{color:{FOREST};}}
div[data-testid="stDataFrame"]{{border:1px solid #e5e9e1;border-radius:14px;overflow:hidden;}}
@keyframes rise{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}}}}
@media(max-width:850px){{.hero-photo{{padding:2.2rem 1.5rem;min-height:560px;background-position:60% center;}}.float-panel{{position:relative;right:auto;bottom:auto;margin-top:2rem;width:min(100%,290px);}}.hero-photo h1{{font-size:2.7rem;}}}}
@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;}}}}
</style>
""", unsafe_allow_html=True)

def logo():
    logo_path = Path(__file__).resolve().parents[1] / "assets" / "talentlens-logo.svg"
    svg_data = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    st.markdown(
        f'<div class="tl-brand"><img src="data:image/svg+xml;base64,{svg_data}" alt="TalentLens — See talent beyond the resume"></div>',
        unsafe_allow_html=True,
    )

def metric_row(items):
    cols = st.columns(len(items))
    for col,(label,value) in zip(cols,items):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{html.escape(str(label))}</div><div class="metric-value">{html.escape(str(value))}</div></div>',unsafe_allow_html=True)

def hero(title, subtitle, kicker="TALENTLENS WORKSPACE"):
    st.markdown(f'<div class="hero-photo"><div class="hero-copy"><div class="hero-kicker">{html.escape(kicker)}</div><h1>{title}</h1><p>{html.escape(subtitle)}</p></div></div>',unsafe_allow_html=True)

def split_csv(value):
    return [x.strip() for x in (value or "").split(",") if x.strip()]

def logout():
    for key in ["token","user"]:
        st.session_state.pop(key,None)
    st.rerun()

def auth_screen():
    st.markdown(f"""
    <div class="hero-photo">
      <div class="hero-copy">
        <div class="hero-kicker">A new lens on human potential</div>
        <h1>See talent <em>beyond the resume.</em></h1>
        <p>Skills tell a richer story. TalentLens connects ambitious students with forward-thinking companies through transparent, evidence-based talent discovery.</p>
      </div>
      <div class="float-panel"><small>LIVE TALENT SNAPSHOT</small><div style="display:flex;justify-content:space-between;align-items:center;margin-top:.4rem"><b style="font-size:1rem">Role alignment</b><span style="color:#2f8f6b;font-weight:800">● LIVE</span></div><div class="float-score">86<small style="font-size:.9rem"> / 100</small></div><div style="font-size:.8rem;color:#748078">Skills and project evidence detected</div></div>
    </div>
    """,unsafe_allow_html=True)
    left,right=st.columns([1.05,.95],gap="large")
    with left:
        st.markdown('<div class="section-kicker">A more human way to discover talent</div>',unsafe_allow_html=True)
        st.markdown("## Built around skills. Designed for what comes next.")
        st.write("A transparent workspace where student potential is supported by projects, skills, education and public portfolio evidence.")
        a,b,c=st.columns(3)
        with a: st.markdown("**01**  \nSkills-first")
        with b: st.markdown("**02**  \nExplainable fit")
        with c: st.markdown("**03**  \nHuman-led hiring")
        st.markdown(f'<div class="photo-band" style="background-image:url({PHOTO_STUDENTS});margin-top:1.2rem"><div><div class="section-kicker" style="color:#d3e8d9">FOR THE NEXT GENERATION</div><h3 style="color:white">Show the work behind your ambition.</h3></div></div>',unsafe_allow_html=True)
    with right:
        st.markdown("## Welcome to TalentLens")
        sign,create=st.tabs(["Sign in","Create account"])
        with sign:
            with st.form("login"):
                email=st.text_input("Email address")
                password=st.text_input("Password",type="password")
                go=st.form_submit_button("Sign in →",use_container_width=True)
            if go:
                try:
                    result=post("/api/auth/login",{"email":email,"password":password})
                    st.session_state.token=result["token"];st.session_state.user=result["user"];st.rerun()
                except Exception as e: st.error(str(e))
        with create:
            with st.form("register"):
                name=st.text_input("Full name")
                email=st.text_input("Email address",key="signup_email")
                password=st.text_input("Password · minimum 8 characters",type="password",key="signup_password")
                role=st.radio("Create account as",["student","recruiter"],horizontal=True,format_func=lambda x:x.title())
                go=st.form_submit_button("Create your account →",use_container_width=True)
            if go:
                try:
                    result=post("/api/auth/register",{"name":name,"email":email,"password":password,"role":role})
                    st.session_state.token=result["token"];st.session_state.user=result["user"];st.rerun()
                except Exception as e: st.error(str(e))
    st.markdown("### The TalentLens approach")
    cols=st.columns(3)
    with cols[0]:
        st.markdown(f'<div class="photo-band" style="background-image:url({PHOTO_STUDENTS})"><div><h3>Student potential</h3><p style="color:#e5eee7">Build a story beyond a one-page resume.</p></div></div>',unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="photo-band" style="background-image:url({PHOTO_OFFICE})"><div><h3>Modern teams</h3><p style="color:#e5eee7">Find capability with better evidence.</p></div></div>',unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="photo-band" style="background-image:url({PHOTO_TEAM})"><div><h3>Better alignment</h3><p style="color:#e5eee7">Understand why a profile matches a role.</p></div></div>',unsafe_allow_html=True)
    st.caption("TalentLens fit scores support human review; they are not hiring probabilities or automated decisions.")

# Session / auth
if not st.session_state.get("token"):
    auth_screen()
    st.stop()

try:
    me=get("/api/me")
    st.session_state.user=me
except Exception as e:
    st.error(f"Your session could not be verified: {e}")
    if st.button("Return to sign in"): logout()
    st.stop()

user=st.session_state.user
role=user["role"]
with st.sidebar:
    logo()
    st.divider()
    if role=="student":
        pages=["Overview","My profile","Resume intelligence","Explore opportunities","Applications"]
    else:
        pages=["Overview","Company profile","Publish a role","Manage roles","Discover talent","Applications"]
    requested_page = st.session_state.pop("nav_jump", None) or st.session_state.pop("recruiter_page", None)
    page_index = pages.index(requested_page) if requested_page in pages else 0
    page=st.radio("WORKSPACE",pages,index=page_index,label_visibility="visible")
    st.divider()
    st.markdown(f"**{html.escape(user['name'])}**")
    st.caption(role.title()+" workspace")
    st.markdown('<div style="background:#eaf2eb;border-radius:14px;padding:12px;margin:.8rem 0"><span style="color:#2f8f6b;font-weight:800">● Workspace active</span><br><small style="color:#78867e">Your talent journey is in motion.</small></div>',unsafe_allow_html=True)
    if st.button("Sign out",use_container_width=True): logout()

# STUDENT PORTAL
if role=="student":
    try:
        profile=get("/api/profile").get("profile",{})
        applications=get("/api/applications")
        jobs=get("/api/jobs")
    except Exception as e:
        st.error(str(e));st.stop()
    skills=profile.get("skills",[])
    completeness=sum([bool(profile.get("education")),bool(profile.get("college")),bool(skills),bool(profile.get("projects")),bool(profile.get("github_url")),bool(profile.get("bio"))])/6*100

    if page=="Overview":
        hero("Make your potential visible.","Build your skills story, surface project evidence and discover opportunities that fit.","YOUR TALENT JOURNEY")
        metric_row([("Open opportunities",len(jobs)),("Applications sent",len(applications)),("Skills on profile",len(skills)),("Profile strength",f"{completeness:.0f}%")])
        st.markdown("### Your next best steps")
        a,b=st.columns([1.15,.85],gap="large")
        with a:
            st.markdown('<div class="feature-card"><div class="section-kicker">PROFILE MOMENTUM</div><h3>Build a stronger talent story</h3><p>Recruiters get a clearer picture when skills are supported by projects, certifications and public work.</p></div>',unsafe_allow_html=True)
            st.progress(int(completeness),text=f"Profile completeness · {completeness:.0f}%")
            if st.button("Complete my profile →"): st.session_state["nav_jump"]="My profile";st.rerun()
        with b:
            st.markdown(f'<div class="photo-band" style="background-image:url({PHOTO_STUDENTS});min-height:225px"><div><div class="section-kicker" style="color:#d9eadc">KEEP GROWING</div><h3>One skill can open a new door.</h3></div></div>',unsafe_allow_html=True)
        st.markdown("### Recommended opportunities")
        if jobs:
            for job in jobs[:4]:
                with st.container(border=True):
                    l,r=st.columns([4,1])
                    with l:
                        st.markdown(f"**{html.escape(job['title'])}**")
                        st.caption(f"{html.escape(job['company'])} · {html.escape(job['location'])} · {job['job_type']}")
                        st.write("Required: "+", ".join(job["required_skills"][:8]))
                    with r:
                        if st.button("Explore",key=f"overview_job_{job['id']}"): st.session_state["selected_job"]=job["id"];st.session_state["nav_jump"]="Explore opportunities";st.rerun()
        else: st.info("No live roles yet. Check back as recruiters publish opportunities.")

    elif page=="My profile":
        hero("Your talent profile.","Bring your education, projects and experience together in one credible profile.","STUDENT PROFILE")
        with st.form("student_profile"):
            c1,c2=st.columns(2)
            with c1:
                degree=st.text_input("Degree",profile.get("degree",""))
                education=st.text_input("Education / specialization",profile.get("education",""))
                college=st.text_input("College / university",profile.get("college",""))
                grad=st.number_input("Graduation year",2020,2040,int(profile.get("graduation_year") or 2027))
                skills_raw=st.text_input("Skills · comma separated",", ".join(skills))
                github=st.text_input("GitHub profile URL",profile.get("github_url",""),placeholder="https://github.com/username")
            with c2:
                roles_raw=st.text_input("Preferred roles · comma separated",", ".join(profile.get("preferred_roles",[])))
                location=st.text_input("Preferred location",profile.get("preferred_location",""))
                remote=st.checkbox("Open to remote opportunities",bool(profile.get("remote_preference",True)))
                exp_years=st.number_input("Experience in years",0.0,50.0,float(profile.get("experience_years",0)),step=.5)
                bio=st.text_area("Professional summary",profile.get("bio",""),height=120)
                github_langs=st.text_input("GitHub languages · optional manual entry",", ".join(profile.get("github_languages",[])))
            st.markdown("#### Projects")
            projects_raw=st.text_area("One project per line: Project name | technology1, technology2", "\n".join(f"{p.get('title','')} | {', '.join(p.get('technologies',[]))}" for p in profile.get("projects",[])),height=110)
            certs_raw=st.text_area("Certifications · one per line: Name | Issuer", "\n".join(f"{x.get('name','')} | {x.get('issuer','')}" for x in profile.get("certifications",[])),height=80)
            exp_raw=st.text_area("Experience · one per line: Role | Organization | description", "\n".join(f"{x.get('role','')} | {x.get('organization','')} | {x.get('description','')}" for x in profile.get("experience",[])),height=80)
            save=st.form_submit_button("Save talent profile →",use_container_width=True)
        if save:
            projects=[]
            for line in projects_raw.splitlines():
                if line.strip():
                    bits=line.split("|",1);projects.append({"title":bits[0].strip(),"technologies":split_csv(bits[1]) if len(bits)>1 else []})
            certs=[]
            for line in certs_raw.splitlines():
                if line.strip():
                    bits=[x.strip() for x in line.split("|")];certs.append({"name":bits[0],"issuer":bits[1] if len(bits)>1 else ""})
            exp=[]
            for line in exp_raw.splitlines():
                if line.strip():
                    bits=[x.strip() for x in line.split("|")];exp.append({"role":bits[0],"organization":bits[1] if len(bits)>1 else "","description":bits[2] if len(bits)>2 else ""})
            payload={"degree":degree,"education":education,"college":college,"graduation_year":int(grad),"skills":split_csv(skills_raw),
                     "projects":projects,"certifications":certs,"experience":exp,"github_url":github,
                     "github_languages":split_csv(github_langs),"github_repos":profile.get("github_repos",[]),
                     "preferred_roles":split_csv(roles_raw),"preferred_location":location,"remote_preference":remote,
                     "experience_years":exp_years,"bio":bio,"resume_skills":profile.get("resume_skills",[])}
            try: put("/api/profile",payload);st.success("Profile saved successfully.");st.rerun()
            except Exception as e: st.error(str(e))
        st.markdown("### Public portfolio evidence")
        if profile.get("github_url"):
            if st.button("Sync public GitHub profile"):
                try:
                    data=post("/api/github/sync")
                    st.success(f"Synced {data['public_repos']} public repositories and detected {len(data['languages'])} languages.")
                    st.rerun()
                except Exception as e: st.error(str(e))
        if profile.get("github_languages"): st.write("Detected languages:",", ".join(profile["github_languages"]))
        if profile.get("github_repos"):
            st.dataframe(pd.DataFrame(profile["github_repos"]),use_container_width=True,hide_index=True)

    elif page=="Resume intelligence":
        hero("Resume intelligence.","Extract skills from your PDF and review the evidence before using it in your profile.","RESUME INSIGHTS")
        uploaded=st.file_uploader("Upload your resume · PDF · max 8 MB",type=["pdf"])
        if uploaded and st.button("Analyze resume →",use_container_width=True):
            with st.spinner("Reading resume and identifying skills…"):
                try:
                    result=request("POST","/api/resume/analyze",files={"file":(uploaded.name,uploaded.getvalue(),"application/pdf")})
                    st.success(result["message"])
                    st.markdown("#### Skills detected")
                    st.write(", ".join(result["extracted_skills"]) if result["extracted_skills"] else "No supported skills found in selectable PDF text.")
                    st.caption(f"{result['pages']} page(s) · {len(result['extracted_skills'])} detected skills")
                    with st.expander("Review extracted text"): st.text(result["text_preview"])
                    st.info("Extracted skills are saved as resume evidence. Check your profile and correct anything that was misread.")
                except Exception as e: st.error(str(e))
        st.markdown("### Optional AI career narrative")
        st.caption("Requires OPENAI_API_KEY in backend/.env. No generated insight is shown unless the provider responds.")
        if st.button("Generate profile feedback"):
            try:
                result=post("/api/ai/profile-insight")
                st.markdown(result["insight"])
            except Exception as e: st.warning(str(e))

    elif page=="Explore opportunities":
        hero("Explore opportunities.","Discover internships and roles aligned with your skills, projects and preferences.","OPPORTUNITY DISCOVERY")
        search=st.text_input("Search roles or companies",key="job_search")
        filtered=[j for j in jobs if search.lower() in (j["title"]+" "+j["company"]+" "+j["description"]).lower()]
        if not filtered: st.info("No roles match this search right now.")
        for job in filtered:
            with st.container(border=True):
                left,right=st.columns([4,1])
                with left:
                    st.markdown(f"### {html.escape(job['title'])}")
                    st.caption(f"{html.escape(job['company'])} · {html.escape(job['location'])} · {job['job_type']} · {job['work_mode']}")
                    st.write(job["description"])
                    st.write("**Required:** "+", ".join(job["required_skills"]))
                    st.write("**Preferred:** "+(", ".join(job["preferred_skills"]) or "Not specified"))
                with right:
                    if st.button("Apply now",key=f"apply_{job['id']}",use_container_width=True):
                        try:
                            result=post(f"/api/jobs/{job['id']}/apply")
                            st.success(f"Application submitted · profile-to-role fit {result['match_score']}%")
                            st.rerun()
                        except Exception as e: st.error(str(e))

    elif page=="Applications":
        hero("Your applications.","Keep track of where your profile has been shared and the latest status.","APPLICATION TRACKER")
        if applications:
            st.dataframe(pd.DataFrame([{"Role":(x.get("job") or {}).get("title"),"Company":(x.get("job") or {}).get("company"),
                "Status":x["status"].title(),"Fit score":f"{x['match_score']}%"} for x in applications]),use_container_width=True,hide_index=True)
        else: st.info("No applications yet. Explore roles that align with your profile.")

# RECRUITER PORTAL
else:
    try:
        jobs=get("/api/jobs/mine"); applications=get("/api/applications"); candidates=get("/api/candidates")
    except Exception as e: st.error(str(e));st.stop()
    if page=="Overview":
        hero("Discover the people behind the potential.","Create focused roles and review candidates with explainable evidence—not keyword counts alone.","RECRUITER WORKSPACE")
        metric_row([("Open positions",sum(1 for j in jobs if j["is_active"])),("Student profiles",len(candidates)),("Applications",len(applications)),("Shortlisted",sum(1 for a in applications if a["status"]=="shortlisted"))])
        st.markdown("### Your hiring workspace")
        x,y=st.columns([1.1,.9],gap="large")
        with x:
            st.markdown('<div class="feature-card"><div class="section-kicker">HIRING MOMENTUM</div><h3>Turn role requirements into a talent map.</h3><p>Publish a role, compare candidate evidence, inspect missing skills and shortlist people for human review.</p></div>',unsafe_allow_html=True)
            if st.button("Publish a new role →"): st.session_state["recruiter_page"]="Publish a role";st.rerun()
        with y:
            st.markdown(f'<div class="photo-band" style="background-image:url({PHOTO_OFFICE});min-height:235px"><div><div class="section-kicker" style="color:#d9eadc">PEOPLE FIRST</div><h3>Better signals. Better conversations.</h3></div></div>',unsafe_allow_html=True)
        st.markdown("### Recent applications")
        if applications:
            st.dataframe(pd.DataFrame([{"Candidate":(a.get("student") or {}).get("name"),"Role":(a.get("job") or {}).get("title"),"Fit":f"{a['match_score']}%","Status":a["status"].title()} for a in applications[:6]]),use_container_width=True,hide_index=True)
        else: st.info("Applications will appear here when students apply.")

    elif page=="Company profile":
        hero("Your company story.","Help candidates understand the people and mission behind the opportunity.","COMPANY PROFILE")
        company=get("/api/company").get("company",{})
        with st.form("company_profile"):
            name=st.text_input("Company name",company.get("company_name",""))
            website=st.text_input("Website",company.get("website",""))
            industry=st.text_input("Industry",company.get("industry",""))
            size=st.selectbox("Company size",["","1–10","11–50","51–200","201–500","501–1,000","1,000+"],index=["","1–10","11–50","51–200","201–500","501–1,000","1,000+"].index(company.get("company_size","")) if company.get("company_size","") in ["","1–10","11–50","51–200","201–500","501–1,000","1,000+"] else 0)
            about=st.text_area("About the company",company.get("about",""),height=130)
            save=st.form_submit_button("Save company profile →")
        if save:
            try: put("/api/company",{"company_name":name,"website":website,"industry":industry,"company_size":size,"about":about});st.success("Company profile saved.")
            except Exception as e: st.error(str(e))

    elif page=="Publish a role":
        hero("Create an opportunity.","Describe the outcomes, skills and context that matter for this role.","ROLE BUILDER")
        with st.form("new_job"):
            a,b=st.columns(2)
            with a:
                title=st.text_input("Role title",placeholder="Junior Data Analyst")
                company=st.text_input("Company",placeholder="Your organization")
                required=st.text_input("Required skills",placeholder="Python, SQL, Pandas")
                preferred=st.text_input("Preferred skills",placeholder="Power BI, Plotly, Statistics")
                degree=st.text_input("Education requirement",placeholder="B.Tech, BCA, B.Sc or equivalent")
            with b:
                job_type=st.selectbox("Opportunity type",["Internship","Full-time","Part-time","Contract","Graduate programme"])
                location=st.text_input("Location", "Remote")
                work_mode=st.selectbox("Work mode",["Remote","Hybrid","On-site"])
                exp_min=st.number_input("Minimum relevant experience (years)",0.0,50.0,0.0,.5)
                description=st.text_area("Role description",height=150)
            publish=st.form_submit_button("Publish opportunity →",use_container_width=True)
        if publish:
            if not title.strip() or not company.strip(): st.error("Role title and company are required.")
            else:
                try:
                    result=post("/api/jobs",{"title":title,"company":company,"required_skills":split_csv(required),"preferred_skills":split_csv(preferred),
                        "degree":degree,"experience_min":exp_min,"location":location,"remote":work_mode=="Remote","work_mode":work_mode,"job_type":job_type,"description":description})
                    st.success(f"Published {result['title']}.")
                except Exception as e: st.error(str(e))

    elif page=="Manage roles":
        hero("Your opportunities.","Manage published roles and pause openings when needed.","ROLE MANAGEMENT")
        if not jobs: st.info("No roles published yet.")
        for job in jobs:
            with st.container(border=True):
                a,b=st.columns([4,1])
                with a:
                    st.markdown(f"### {html.escape(job['title'])}")
                    st.caption(f"{html.escape(job['company'])} · {job['work_mode']} · {job['job_type']}")
                    st.write("Required: "+", ".join(job["required_skills"]))
                    st.caption("Active" if job["is_active"] else "Paused")
                with b:
                    if st.button("Pause" if job["is_active"] else "Activate",key=f"toggle_{job['id']}"):
                        try: patch(f"/api/jobs/{job['id']}/toggle");st.rerun()
                        except Exception as e: st.error(str(e))

    elif page=="Discover talent":
        hero("Discover relevant talent.","Compare student evidence against your role requirements. Scores support review; they never make hiring decisions.","TALENT DISCOVERY")
        active_jobs=[j for j in jobs if j["is_active"]]
        if not active_jobs: st.info("Publish an active role to start candidate discovery.")
        else:
            selected=st.selectbox("Select role",active_jobs,format_func=lambda j:f"{j['title']} · {j['company']}")
            threshold=st.slider("Minimum fit score",0,100,0)
            ranked=get(f"/api/candidates?job_id={selected['id']}")
            ranked=[r for r in ranked if r["match_score"]>=threshold]
            if ranked:
                st.markdown(f"**{len(ranked)} profiles** ranked for {selected['title']}")
                st.dataframe(pd.DataFrame([{"Rank":r["rank"],"Candidate":r["student"]["name"],"Fit":f"{r['match_score']}%",
                    "Skills":f"{r['skill_score']}%","Projects":f"{r['project_score']}%","GitHub":f"{r['github_score']}%",
                    "Education":f"{r['education_score']}%","Experience":f"{r['experience_score']}%"} for r in ranked]),use_container_width=True,hide_index=True)
                for r in ranked:
                    s=r["student"]
                    with st.expander(f"#{r['rank']} · {s['name']} · {r['match_score']}% profile-to-role fit"):
                        c1,c2=st.columns(2)
                        with c1:
                            st.write("**Education:**",s.get("degree") or s.get("education") or "Not provided")
                            st.write("**College:**",s.get("college") or "Not provided")
                            st.write("**Skills:**",", ".join(s.get("skills",[])) or "Not provided")
                            st.write("**Matched:**",", ".join(r["matched_skills"]) or "None evidenced")
                        with c2:
                            st.write("**Missing required skills:**",", ".join(r["missing_skills"]) or "None")
                            st.write("**Projects:**",", ".join(r["relevant_projects"]) or "No directly relevant project evidence")
                            st.write("**GitHub:**",s.get("github_url") or "Not connected")
                            st.caption(r["score_note"])
                        st.markdown("**Why this score?**")
                        for label,value in r["components"].items():
                            st.progress(int(value),text=f"{label} · {value:.0f}%")
            else: st.info("No profiles meet this threshold. Try reducing the minimum score.")

    elif page=="Applications":
        hero("Candidate pipeline.","Review applicants and update the next step in your hiring process.","APPLICATION MANAGEMENT")
        if not applications: st.info("No applications received yet.")
        for app in applications:
            student=app.get("student") or {};job=app.get("job") or {}
            with st.container(border=True):
                a,b,c=st.columns([2,2,1])
                with a:
                    st.markdown(f"**{html.escape(student.get('name','Candidate'))}**")
                    st.caption(student.get("email",""))
                with b:
                    st.write(job.get("title","Role"))
                    st.caption(f"{job.get('company','')} · Profile fit {app['match_score']}%")
                with c:
                    current=app["status"]
                    options=["applied","shortlisted","interview","rejected","hired"]
                    choice=st.selectbox("Status",options,index=options.index(current) if current in options else 0,key=f"status_{app['id']}")
                    if st.button("Update",key=f"update_status_{app['id']}"):
                        try: patch(f"/api/applications/{app['id']}/status",{"status":choice});st.success("Pipeline status updated.");st.rerun()
                        except Exception as e: st.error(str(e))

st.markdown("---")
st.caption("© 2026 TalentLens · See talent beyond the resume. Fit scores are explainable signals for human review—not hiring predictions.")
