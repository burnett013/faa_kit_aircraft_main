# app/pages/3_About_Me.py
import streamlit as st

st.title("About Me")

st.markdown(
"""
### Hi, I’m Andy 🤟

### This Project in a Nutshell
**FAA Kit Aircraft (FAA Kits, Kits) Explorer** is a full-stack app for exploring kit-built aircraft registered in the U.S.

- **Stack:** FastAPI • PostgreSQL • SQLAlchemy • Pandas • Streamlit  
- **Data:** FAA registry (cleaned & modeled), with a dedicated API layer  
- **Features:** manufacturer/model filters, regional stats, and quick visualizations

---

### Recent Work
- **FAA Full Dataset (300k+ rows):** Sourced, cleaned, and structured the national aircraft registry, forming a foundation for aviation analytics.
- **FAA Kits Dataset (16k+ rows):** Built this end-to-end app (API + DB + UI) to explore kit aircraft—combining data engineering, modeling, and visualization.

---
I recently completed an **M.S. in Artificial Intelligence & Business Analytics (3.8 GPA)** at the University of South Florida’s Muma College of Business, building on a **B.S. in Entrepreneurship (cum laude)**.  
My work lives at the intersection of **data, design, and decision-making**—turning raw data into tools people actually use.

---

### How I Work
I like solving messy problems, telling clear stories with data, and building systems that make decisions easier.  
It’s never just numbers—it’s **context, clarity, and usability**.

---

### Values I Bring
Former **combat medic**, Afghanistan veteran. That experience taught me to stay calm in uncertainty, focus on what matters, and lead with empathy.  
I show up with **resilience, clarity, and commitment** in everything I build.

---

### What Drives Me
Work that matters: blending **data + design + strategy** to bring clarity to complex questions—whether that’s a pipeline, a visualization, or an insight that changes direction.

---
"""
)

# --- Signature ---

st.image("app/assets/signature.png", use_container_width=False, width=200)

# --- Contact buttons ---
st.write("#### Let’s Connect")

col1, col2, col3 = st.columns(3)
with col1:
    st.link_button(
        "LinkedIn",
        "https://www.linkedin.com/in/burnett013/",
        type="primary",
        use_container_width=True
    )
with col2:
    st.link_button(
        "GitHub",
        "https://github.com/burnett013",
        type="primary",
        use_container_width=True
    )
with col3:
    st.link_button(
        "Email Me",
        "mailto:andyburnett013@gmail.com",
        type="primary",
        use_container_width=True
    )