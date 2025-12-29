import streamlit as st
import json
import os
import uuid
from datetime import datetime
from PIL import Image
import os

# ---------------- CONFIG ----------------
DB_FILE = "database.json"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR + "/proof", exist_ok=True)
os.makedirs(UPLOAD_DIR + "/suggestion", exist_ok=True)
os.makedirs(UPLOAD_DIR + "/user", exist_ok=True)

# ---------------- DB UTILS ----------------
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"pages": {}}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

db = load_db()

# ---------------- HELPERS ----------------
def save_files(files, folder):
    paths = []
    if files:
        for file in files:
            filename = f"{uuid.uuid4()}_{file.name}"
            path = os.path.join(UPLOAD_DIR, folder, filename)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            paths.append(path)
    return paths

def safe_show_image(path, width=None, caption=None):
    try:
        if not path or not os.path.exists(path):
            return

        with open(path, "rb") as f:
            img = Image.open(f)
            img.load()  # force decode

        st.image(img, width=width, caption=caption, use_container_width=True)

    except Exception:
        st.warning("⚠️ Unable to display image (file may be corrupted or removed)")


def search_db(query, db):
    results = {
        "pages": [],
        "problems": []
    }

    q = query.lower()

    for page_name, page_data in db["pages"].items():

        # Page name search
        if q in page_name.lower():
            results["pages"].append({
                "page": page_name,
                "creator": page_data.get("creator", {})
            })

        # Problem search
        for p in page_data["problems"]:
            text_match = q in p["problem"].lower()
            tag_match = q in " ".join(p.get("tags", [])).lower()

            if text_match or tag_match:
                results["problems"].append({
                    "page": page_name,
                    "problem": p
                })

    return results

def get_pages():
    return list(db["pages"].keys())

# ---------------- SIDEBAR (NAVBAR) ----------------
with st.sidebar:
    st.title("🛑 AjjKiProblem")

    menu = st.radio(
        "Navigation",
        ["Home", "Problems","Pages", "Create Page", "About"]
    )

    # if "menu" not in st.session_state:
    #     st.session_state.menu = "Home"

    #     menu = st.sidebar.radio(
    #         "Navigation",
    #         ["Home", "Pages", "Problems", "Create Page", "About"],
    #         index=["Home", "Pages", "Problems", "Create Page", "About"]
    #         .index(st.session_state.menu)
    #     )

    # search = st.text_input("🔍 Search Problem / Page")


    # if search.strip():
    #     st.header("🔎 Search Results")

    #     results = search_db(search, db)

    #     # -------- PAGES RESULT --------
    #     if results["pages"]:
    #         st.subheader("📄 Pages")
    #         for p in results["pages"]:
    #             with st.container():
    #                 st.markdown(f"### 📌 {p['page']}")
    #                 st.caption(f"Creator: {p['creator'].get('name', 'N/A')}")

    #                 # if st.button("View Page", key=f"search_page_{p['page']}"):
    #                 #     st.session_state["open_page"] = p["page"]
    #                 #     st.rerun()

    #     # -------- PROBLEMS RESULT --------
    #     if results["problems"]:
    #         st.subheader("📝 Problems")
    #         for item in results["problems"]:
    #             p = item["problem"]
    #             page = item["page"]

    #             st.markdown(f"**{p['problem']}**")
    #             st.caption(f"📍 Page: {page}")
    #             st.write(f"🏷️ Tags: {', '.join(p.get('tags', []))}")

    #             # if st.button("Open Problem", key=f"search_prob_{p['id']}"):
    #             #     st.session_state["open_page"] = page
    #             #     st.rerun()

    #             st.divider()

    #     if not results["pages"] and not results["problems"]:
    #         st.info("No matching pages or problems found.")

    #     st.stop()


# ---------------- HOME ----------------
if menu == "Home":

    st.header("📌 Report a Problem")

    pages = get_pages()
    if not pages:
        st.warning("No pages available. Create a page first.")
        st.stop()

    selected_page = st.selectbox("Choose Page", pages)

    with st.form("problem_form"):
        problem_text = st.text_area("Describe the Problem")

        tags_input = st.text_input(
            "Related Keywords / Fields (comma separated)",
            placeholder="eg: exam, fee, hostel, transport, scholarship"
        )


        st.subheader("Proof that problem exists")
        proof_text = st.text_area("Explain the proof")
        proof_files = st.file_uploader(
            "Upload proof files",
            accept_multiple_files=True
        )

        st.subheader("Suggestions")
        suggestion_text = st.text_area("Your suggestion")
        suggestion_files = st.file_uploader(
            "Upload suggestion files",
            accept_multiple_files=True,
            key="suggestion_files"
        )

        extra_thought = st.text_area("Extra thoughts (optional)")

        next_btn = st.form_submit_button("Next ➡")

        tags = [t.strip().lower() for t in tags_input.split(",") if t.strip()]

    if next_btn:

        st.session_state.problem_data = {
            "problem_text": problem_text,
            "tags": tags,
            "proof_text": proof_text,
            "proof_files": proof_files,
            "suggestion_text": suggestion_text,
            "suggestion_files": suggestion_files,
            "extra_thought": extra_thought,
            "page": selected_page
        }
        st.session_state.show_user = True

    # -------- USER DETAILS --------
    if st.session_state.get("show_user"):
        st.subheader("👤 User Details (Optional)")

        with st.form("user_form"):
            name = st.text_input("Name")
            mobile = st.text_input("Mobile")
            email = st.text_input("Email")
            address = st.text_area("Address")
            photo = st.file_uploader("Upload Photo")

            col1, col2 = st.columns(2)
            back = col1.form_submit_button("⬅ Previous")
            submit = col2.form_submit_button("Submit")

        if submit:
            pdata = st.session_state.problem_data

            proof_paths = save_files(pdata["proof_files"], "proof")
            suggestion_paths = save_files(pdata["suggestion_files"], "suggestion")
            photo_path = save_files([photo], "user") if photo else []

            problem_id = f"{pdata['page']}_P{len(db['pages'][pdata['page']]['problems']) + 1}"

            problem_obj = {
                "id": problem_id,
                "problem": pdata["problem_text"],
                "tags": pdata["tags"],
                "proof_text": pdata["proof_text"],
                "proof_files": proof_paths,
                "suggestion_text": pdata["suggestion_text"],
                "suggestion_files": suggestion_paths,
                "extra": pdata["extra_thought"],
                "likes": 0,
                "timestamp": str(datetime.now()),
                "user": {
                    "name": name,
                    "mobile": mobile,
                    "email": email,
                    "address": address,
                    "photo": photo_path
                } if name or mobile or email else None
            }

            db["pages"][pdata["page"]]["problems"].append(problem_obj)
            save_db(db)

            st.success("✅ Problem submitted successfully")
            st.session_state.clear()

# ---------------- CREATE PAGE ----------------
elif menu == "Create Page":
    st.header("➕ Create New Page")

    with st.form("create_page"):
        page_name = st.text_input("Page Name")
        creator = st.text_input("Your Name")
        cr_position = st.text_input("Your Position")
        cr_address = st.text_input("Your Address")
        mobile = st.text_input("Mobile (OTP assumed verified)")
        email = st.text_input("Email (OTP assumed verified)")
        photo = st.file_uploader("Upload Photo")

        create = st.form_submit_button("Create Page")

    if create:
        if page_name in db["pages"]:
            st.error("Page already exists")
        else:
            photo_path = save_files([photo], "user") if photo else []
            db["pages"][page_name] = {
                "verified": True,
                "creator": {
                    "name": creator,
                    "position": cr_position,
                    "address": cr_address,
                    "mobile": mobile,
                    "email": email,
                    "photo": photo_path
                },
                "problems": []
            }
            save_db(db)
            st.success("🎉 Page created successfully")

# ---------------- PAGES ----------------
elif menu == "Pages":
    st.header("📄 All Pages")

    pages = db["pages"]

    if not pages:
        st.info("No pages created yet.")
        st.stop()

    # -------- PAGE LIST --------
    for page_name, page_data in pages.items():

        with st.container():
            col1, col2 = st.columns([3, 1])

            # PAGE INFO
            with col1:
                st.markdown(f"## 📌 {page_name}")
                if page_data.get("verified"):
                    st.caption("✅ Verified Page")

                creator = page_data.get("creator", {})
                st.markdown("**Creator Information:**")
                st.write(f"👤 Name: {creator.get('name', 'N/A')}")
                st.write(f"📧 Email: {creator.get('email', 'N/A')}")
                st.write(f"📱 Mobile: {creator.get('mobile', 'N/A')}")

            # CREATOR PHOTO
            with col2:
                if creator.get("photo"):
                    st.image(creator["photo"][0], width=120)
                else:
                    st.caption("No photo")

            # BUTTON TO OPEN PROBLEMS
            if st.button(f"View Problems →", key=f"view_{page_name}"):
                st.session_state["open_page"] = page_name

        st.divider()

    # -------- PAGE PROBLEMS VIEW --------
    if st.session_state.get("open_page"):

        page = st.session_state["open_page"]
        page_data = pages[page]

        st.markdown(f"# 🧾 Problems in {page}")
        st.caption("Sorted by most liked")

        problems = sorted(
            page_data["problems"],
            key=lambda x: x["likes"],
            reverse=True
        )

        if not problems:
            st.info("No problems added to this page yet.")
            st.stop()

        for p in problems:

            st.markdown(f"### 📝 {p['problem']}")
            st.write(p["proof_text"])

            # TAGS
            if p.get("tags"):
                st.caption("🏷️ " + ", ".join(p["tags"]))

            # MEDIA
            # if p.get("proof_files"):
            #     with st.expander("📎 Proof Files"):
            #         for file in p.get("proof_files", []):
            
            #             # ---- Safety: file exists ----
            #             if not file or not os.path.exists(file):
            #                 st.warning("⚠️ File not available")
            #                 continue
            
            #             file_lower = file.lower()
            
            #             # ---- Image ----
            #             if file_lower.endswith((".png", ".jpg", ".jpeg")):
            #                 safe_show_image(file)
            
            #             # ---- Video ----
            #             elif file_lower.endswith(".mp4"):
            #                 st.video(file)
            
            #             # ---- Audio ----
            #             elif file_lower.endswith(".mp3"):
            #                 st.audio(file)
            
            #             # ---- Document / Others ----
            #             else:
            #                 st.markdown(f"📄 [Download document]({file})")
            
                        
            # ACTIONS
            col1, col2, col3 = st.columns(3)

            if col1.button(f"👍 {p['likes']}", key=f"like_{p['id']}"):
                p["likes"] += 1
                save_db(db)
                st.experimental_rerun()

            col2.button("💬 Comment", key=f"cmt_{p['id']}")
            col3.button("🔗 Share", key=f"share_{p['id']}")

            # USER INFO
            if p.get("user"):
                with st.expander("👤 User Info"):
                    if p["user"].get("photo"):
                        # st.image(p["user"]["photo"][0], width=120)
                        pass
                    st.write(p["user"])

            st.divider()

        # BACK BUTTON
        if st.button("⬅ Back to Pages List"):
            del st.session_state["open_page"]
            st.rerun()


elif menu == "Problems":
    st.header("📊 Explore Problems")

    # ---------- FILTER CONTROLS ----------
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_type = st.selectbox(
            "Sort By",
            ["Trending", "Most Liked", "Least Liked", "Newest", "Oldest"]
        )

    with col2:
        page_filter = st.selectbox(
            "Filter by Page",
            ["All"] + get_pages()
        )

    with col3:
        keyword = st.text_input(
            "Search by keyword / tag",
            placeholder="eg: exam, fee, hostel"
        )

    # ---------- COLLECT ALL PROBLEMS ----------
    all_problems = []

    for page_name, page_data in db["pages"].items():
        for p in page_data["problems"]:
            p_copy = p.copy()
            p_copy["page"] = page_name
            p_copy["verified"] = page_data.get("verified", False)
            all_problems.append(p_copy)

    if not all_problems:
        st.info("No problems available yet.")
        st.stop()

    # ---------- APPLY PAGE FILTER ----------
    if page_filter != "All":
        all_problems = [p for p in all_problems if p["page"] == page_filter]

    # ---------- APPLY KEYWORD / TAG FILTER ----------
    if keyword.strip():
        kw = keyword.lower()
        all_problems = [
            p for p in all_problems
            if kw in p["problem"].lower()
            or any(kw in tag for tag in p.get("tags", []))
        ]

    # ---------- SORTING ----------
    if filter_type == "Most Liked":
        all_problems.sort(key=lambda x: x["likes"], reverse=True)

    elif filter_type == "Least Liked":
        all_problems.sort(key=lambda x: x["likes"])

    elif filter_type == "Newest":
        all_problems.sort(key=lambda x: x["timestamp"], reverse=True)

    elif filter_type == "Oldest":
        all_problems.sort(key=lambda x: x["timestamp"])

    elif filter_type == "Trending":
        all_problems.sort(
            key=lambda x: (x["likes"], x["timestamp"]),
            reverse=True
        )

    # ---------- RENDER PROBLEMS ----------
    for p in all_problems:

        st.markdown(f"## 📝 {p['problem']}")
        st.caption(f"📄 Page: {p['page']} {'✅ Verified' if p['verified'] else ''}")
        st.write(p["proof_text"])

        # ---------- TAGS ----------
        if p.get("tags"):
            st.caption("🏷️ " + " | ".join(p["tags"]))

        # ---------- MEDIA PREVIEW ----------
           

        if p.get("proof_files"):
            with st.expander("📎 View Proof Files"):
                for file in p.get("proof_files", []):
        
                    # Safety check: file exists
                    if not os.path.exists(file):
                        st.warning("⚠️ File not found or removed")
                        continue
        
                    file_lower = file.lower()
        
                    # IMAGE
                    if file_lower.endswith((".png", ".jpg", ".jpeg")):
                        st.image(file, use_container_width=True)
        
                    # VIDEO
                    elif file_lower.endswith(".mp4"):
                        st.video(file)
        
                    # AUDIO
                    elif file_lower.endswith(".mp3"):
                        st.audio(file)
        
                    # DOCUMENT / OTHER FILES
                    else:
                        st.markdown(f"📄 [Download document]({file})")


        # ---------- ACTION BUTTONS ----------
        colA, colB, colC, colD = st.columns([1, 1, 1, 2])

        # LIKE
        if colA.button(f"👍 {p['likes']}", key=f"like_global_{p['id']}"):
            for page in db["pages"].values():
                for original in page["problems"]:
                    if original["id"] == p["id"]:
                        original["likes"] += 1
                        save_db(db)
                        st.rerun()

        # COMMENT
        if colB.button("💬 Comment", key=f"cmt_global_{p['id']}"):
            st.session_state[f"show_cmt_{p['id']}"] = True

        # SHARE
        if colC.button("🔗 Share", key=f"share_global_{p['id']}"):
            st.code(
                f"Problem ID: {p['id']}\n"
                f"Page: {p['page']}\n"
                f"Problem: {p['problem']}",
                language="text"
            )

        # USER INFO
                
        
        if p.get("user"):
            with colD:
                with st.expander("👤 User Info"):
        
                    user = p.get("user", {})
        
                    # ---------- USER PHOTO ----------
                    photo_list = user.get("photo", [])
        
                    if photo_list and isinstance(photo_list, list):
                        photo_path = photo_list[0]
        
                        if photo_path and os.path.exists(photo_path):
                            st.image(photo_path, width=120)
                        else:
                            st.caption("📷 Photo not available")
        
                    # ---------- USER DETAILS ----------
                    name = user.get("name")
                    email = user.get("email")
                    mobile = user.get("mobile")
        
                    st.write(f"**Name:** {name if name else 'Not shared'}")
                    st.write(f"**Email:** {email if email else 'Not shared'}")
                    st.write(f"**Mobile:** {mobile if mobile else 'Not shared'}")
        

        # ---------- COMMENT FORM ----------
        if st.session_state.get(f"show_cmt_{p['id']}"):

            for page in db["pages"].values():
                for original in page["problems"]:
                    if original["id"] == p["id"]:
                        if "comments" not in original:
                            original["comments"] = []

                        with st.form(f"comment_form_global_{p['id']}"):
                            comment_text = st.text_area("Write your comment")
                            post = st.form_submit_button("Post Comment")

                        if post and comment_text.strip():
                            original["comments"].append({
                                "text": comment_text,
                                "time": str(datetime.now())
                            })
                            save_db(db)
                            st.session_state[f"show_cmt_{p['id']}"] = False
                            st.rerun()

        # ---------- COMMENT LIST ----------
        if p.get("comments"):
            with st.expander(f"💬 View Comments ({len(p['comments'])})"):
                for c in p["comments"]:
                    st.markdown(f"- {c['text']}")
                    st.caption(c["time"])

        st.divider()


# ---------------- ABOUT ----------------
elif menu == "About":
    st.header("ℹ️ About AjjKiProblem")

    st.markdown("""
    ### 🌱 What is AjjKiProblem?

    **AjjKiProblem** is a community-driven platform created to help people **share real problems**, 
    **prove that those problems exist**, and **connect with others** who are facing similar situations 
    or who want to help.

    This platform is not only about reporting issues —  
    it is about **understanding, collaboration, emotional support, and collective problem-solving**.
    """)

    st.markdown("""
    ---
    ### 🎯 Why AjjKiProblem Exists

    Many times in life:
    - People face problems but **don’t know where to share**
    - They feel **alone**, unheard, or unsupported
    - The problem is real, but **no proper proof or visibility exists**
    - Even if solutions exist, **people don’t connect with the right ones**

    **AjjKiProblem solves this gap.**
    """)

    st.markdown("""
    ---
    ### 🧩 What Problems This Platform Solves

    ✔ Gives a **safe place** to report genuine problems  
    ✔ Allows uploading **proof** (images, videos, voice, documents)  
    ✔ Helps users **suggest solutions**, not just complain  
    ✔ Connects people facing **similar issues**  
    ✔ Helps communities, colleges, organizations, and individuals  
    ✔ Allows people to **stay anonymous** if they want  
    ✔ Converts problems into **actionable discussions**
    """)

    st.markdown("""
    ---
    ### 🛠️ Key Features

    🔹 **Problem Reporting**
    - Write your problem clearly
    - Add related keywords (tags)
    - Upload proof (image / video / audio / document)

    🔹 **Suggestions & Extra Thoughts**
    - Share ideas, solutions, or improvements
    - Add extra thoughts or emotional context

    🔹 **User Information (Optional)**
    - You can submit anonymously
    - Or share your details to allow others to contact you

    🔹 **Pages System**
    - Individual pages
    - Organization / University pages
    - User-created verified pages
    - Each page has its own problem list

    🔹 **Likes, Comments & Search**
    - Like problems to show priority
    - Comment to discuss
    - Search problems by words, tags, or page name
    """)

    st.markdown("""
    ---
    ### 🤝 Human Connection & Collaboration (Important)

    Imagine this situation:

    > Two people are facing the same problem,  
    > but they don’t know each other and no one around them understands.

    On **AjjKiProblem**:
    - One person can post the problem
    - The second person can find it through search or tags
    - If user info is shared, they can **connect**
    - Both can **collaborate, share skills, ideas, and emotional support**
    - Pages help **bring more people together** for the same cause

    This platform helps people:
    - Share not only problems, but **feelings**
    - Feel **less alone**
    - Help each other grow and solve issues together
    """)

    st.markdown("""
    ---
    ### 📖 How to Use AjjKiProblem (User Manual)

    **Step 1️⃣ – Choose a Page**
    - Select an existing page (Individual / University / Organization)
    - Or create a new page if needed

    **Step 2️⃣ – Post a Problem**
    - Describe the problem
    - Add related keywords (tags)
    - Upload proof to show authenticity

    **Step 3️⃣ – Add Suggestions**
    - Share solutions or ideas
    - Upload supporting files if required

    **Step 4️⃣ – Submit User Info (Optional)**
    - Stay anonymous OR
    - Share details so others can contact and collaborate

    **Step 5️⃣ – Explore & Connect**
    - Like problems
    - Comment and discuss
    - Search similar problems
    - Join others facing the same issue
    """)

    st.markdown("""
    ---
    ### 🌍 Vision of AjjKiProblem

    AjjKiProblem is not just a website.

    It is a **problem-sharing space**,  
    a **support system**,  
    and a **bridge between people** who want to help each other.

    Together, small voices become strong.
    """)

    st.markdown("""
    ---
    **Developed with ❤️ using Streamlit**  
    *For people, by people.*
    """)







