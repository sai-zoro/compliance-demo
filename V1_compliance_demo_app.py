
import streamlit as st
import pandas as pd
import json
import hashlib
from PIL import Image

st.set_page_config(page_title="AI Compliance Framework", layout="wide")

# ---- Load Preloaded Files ----
with open("data/enriched_use_case_metadata.json") as f:
    use_case_metadata = json.load(f)

with open("data/cv_rule_engine.json") as f:
    rules = json.load(f)["rules"]

# ---- Page Navigation ----
if "page" not in st.session_state:
    st.session_state.page = "intro"

# ---- Front Page ----
if st.session_state.page == "intro":
    st.title("🌍 Cross-Border AI Compliance Demo")

    st.markdown("""
    ###  Use Case: Automated Resume Screening

    A company based in **Germany** has purchased a third-party **AI tool** developed in the **USA**.  
    The tool will be used in the **HR department** to automatically **screen resumes** for job applications.

    ###  Regulatory Differences – Tool Origin(USA) vs Tool Application(Germany)
    - **Germany (EU)**: GDPR & EU AI Act → strict rules on personal data, fairness, transparency.
    - **USA**: No federal AI law → less strict, more fragmented.

    ###  What This Framework Does
    - Detects **legal and ethical risks** before data reaches the AI model.
    - Applies rule-based filters for **GDPR & AI Act** compliance.
    - Logs actions for **audit & traceability**.
    """)

    st.markdown("---")

    # Display framework diagram
    st.subheader("🧠 Framework Structure")
    image = Image.open("data/framework_diagram.png")
    st.image(image, caption="Ethical AI Compliance Framework")

    st.markdown("""
    **Framework Component:**

    1. **Rules Repository**: Holds legal and ethical conditions (e.g., GDPR, EU AI Act)
    2. **Contextual Rule Engine**: Selects only relevant rules for the specific AI use case
    3. **Policy Mapping Layer**: Maps and Applies the required actions to the Data
    4. **Compliance Monitoring**: Logs every action for audit + sends feedback to rules
    5. **AI System**: Only compliant data is passed to the AI tool for decision-making
    """)

    if st.button("🚀 Let's Go"):
        st.session_state.page = "demo"
        st.rerun()

# ---- Main Functional Page ----
elif st.session_state.page == "demo":
    st.title("🛠️ AI Compliance Framework")

    st.sidebar.title("Upload Your Input")
    data_file = st.sidebar.file_uploader("📊 Upload HR Data (CSV)", type="csv")

    if data_file:
        st.success("✅ File uploaded.")
        # Hide sidebar after upload
        hide_sidebar = """
            <style>
                 [data-testid="stSidebar"] {display: none;}
            </style>
        """
        st.markdown(hide_sidebar, unsafe_allow_html=True)

        st.markdown("###  Use Case Metadata")
        st.markdown(" ")
        st.info(f"**Risk Level**: {use_case_metadata['risk_level']}  \n**Reason**: {use_case_metadata['risk_reason']}")

        # Now start metadata details in columns
        col1, col2 = st.columns(2)
        with col1:
         st.markdown("**Input Source:**")
         st.markdown(f"- {use_case_metadata['input_data_source']}")
        with col2:
         st.markdown("**Users:**")
         st.markdown(f"- {use_case_metadata['who_uses']}")

        # Raw data
        st.markdown("### Uploaded Dataset")
        df_raw = pd.read_csv(data_file)
        st.dataframe(df_raw)

        # Apply rule engine
        st.markdown("###  Applying Rules and Transforming the Dataset")
        df_transformed = df_raw.copy()
        audit_log = []
        changed_fields = set()

        for rule in rules:
            field = rule["condition"]["field"]
            action = rule["action"]
            legal_ref = rule["legal_reference"]

            if field not in df_transformed.columns:
                continue

            if action == "pseudonymize":
                for idx in df_transformed.index:
                    val = str(df_transformed.at[idx, field])
                    pseudo = hashlib.sha256(val.encode()).hexdigest()[:10]
                    df_transformed.at[idx, field] = pseudo
                    audit_log.append({
                        "field": field,
                        "action": "pseudonymized",
                        "row": int(idx),
                        "legal_reference": legal_ref
                    })
                changed_fields.add(field)

            elif action == "remove":
                df_transformed.drop(columns=[field], inplace=True)
                audit_log.append({
                    "field": field,
                    "action": "removed",
                    "row": "all",
                    "legal_reference": legal_ref
                })
                changed_fields.add(field)

            elif action == "log_sensitive":
                for idx in df_transformed.index:
                    audit_log.append({
                        "field": field,
                        "action": "logged sensitive field",
                        "row": int(idx),
                        "legal_reference": legal_ref
                    })

        # Transformed data
        st.markdown("Output – Transformed Dataset")
        st.dataframe(df_transformed)

        if changed_fields:
            st.markdown("**Data Points Transformed:**")
            for field in changed_fields:
                st.markdown(f"- `{field}` field was processed for compliance.")

        # Audit Log
        with st.expander("🧾 Show Audit Log"):
            st.json(audit_log)

        # Downloads
        st.markdown("### 📦 Download Outputs")
        st.download_button("⬇️ Download Transformed CSV", df_transformed.to_csv(index=False), file_name="transformed_data.csv", mime="text/csv")
        st.download_button("⬇️ Download Audit Log (JSON)", json.dumps(audit_log, indent=2), file_name="audit_log.json", mime="application/json")

    else:
        st.info("📤 Please upload the HR dataset.")
