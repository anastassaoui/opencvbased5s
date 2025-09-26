import streamlit as st
import tempfile
import os
from pathlib import Path
from analyze_rca import analyze_workplace, generate_analysis_mindmap, generate_improvement_wbs, create_plantuml_diagram
from streamlit_option_menu import option_menu
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Root Cause Analysis Platform",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }

    .upload-zone {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        margin: 1rem 0;
    }

    .results-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    .diagram-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border: 1px solid #e1e5e9;
        transition: transform 0.3s ease;
    }

    .diagram-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .status-success { background-color: #52c41a; }
    .status-warning { background-color: #faad14; }
    .status-error { background-color: #ff4d4f; }

    .analysis-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header with modern design
st.markdown("""
<div class="main-header">
    <h1>Root Cause Analysis Platform</h1>
    <p>AI-Powered Problem Identification & Root Cause Resolution with Computer Vision & Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)

# Get API key from environment
api_key = os.getenv("GROQ_API_KEY")

# Navigation menu
selected = option_menu(
    menu_title=None,
    options=["Analysis", "Root Cause Map", "Resolution Plan", "Settings"],
    icons=["search", "diagram-2", "kanban", "gear"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "icon": {"color": "#667eea", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "padding": "10px",
            "--hover-color": "#eee",
        },
        "nav-link-selected": {"background-color": "#667eea"},
    },
)

if selected == "Analysis":
    # Status indicators
    col_status1, col_status2, col_status3 = st.columns(3)

    with col_status1:
        status_color = "success" if api_key else "error"
        st.markdown(f"""
        <div class="metric-card">
            <span class="status-indicator status-{status_color}"></span>
            <strong>API Status:</strong> {'Connected' if api_key else 'Not Configured'}
        </div>
        """, unsafe_allow_html=True)

    with col_status2:
        analysis_status = "success" if hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete else "warning"
        st.markdown(f"""
        <div class="metric-card">
            <span class="status-indicator status-{analysis_status}"></span>
            <strong>Analysis:</strong> {'Complete' if hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete else 'Pending'}
        </div>
        """, unsafe_allow_html=True)

    with col_status3:
        diagrams_ready = hasattr(st.session_state, 'mindmap_path') and hasattr(st.session_state, 'wbs_path')
        diagram_status = "success" if diagrams_ready else "warning"
        st.markdown(f"""
        <div class="metric-card">
            <span class="status-indicator status-{diagram_status}"></span>
            <strong>Diagrams:</strong> {'Ready' if diagrams_ready else 'Not Generated'}
        </div>
        """, unsafe_allow_html=True)

    # Main analysis interface
    main_col1, main_col2 = st.columns([1, 1.5], gap="large")

    with main_col1:
        st.markdown("### Upload Workplace Image")

        st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drag and drop or browse files",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Upload a high-quality image of your workplace for comprehensive Root Cause Analysis",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Workplace Image", use_container_width=True)

            # Analysis button with modern styling
            if st.button("Start AI Analysis", type="primary", use_container_width=True, disabled=not api_key):
                if not api_key:
                    st.error("API key not configured. Please check your .env file.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            temp_path = tmp_file.name

                        status_text.text("Preprocessing image...")
                        progress_bar.progress(25)

                        status_text.text("Running AI analysis...")
                        progress_bar.progress(50)

                        # Perform analysis
                        analysis_result = analyze_workplace(temp_path)
                        progress_bar.progress(75)

                        status_text.text("Generating results...")

                        # Store results in session state
                        st.session_state.analysis_result = analysis_result
                        st.session_state.analysis_complete = True

                        progress_bar.progress(100)
                        status_text.text("Analysis complete!")

                        st.success("Workplace analysis completed successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)

    with main_col2:
        st.markdown("### Analysis Results")

        if hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete:

            # Results container with modern styling
            st.markdown('<div class="results-container">', unsafe_allow_html=True)

            # Analysis text with better formatting
            with st.expander("Detailed Root Cause Analysis Report", expanded=True):
                st.markdown(st.session_state.analysis_result)

            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("Upload an image and start the analysis to see results here")

elif selected == "Root Cause Map":
    st.markdown("### Root Cause Analysis Map")

    if hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete:
        if hasattr(st.session_state, 'mindmap_path') and os.path.exists(st.session_state.mindmap_path):
            st.image(st.session_state.mindmap_path, use_container_width=True)

            with open(st.session_state.mindmap_path, "rb") as file:
                st.download_button(
                    label="Download Root Cause Map",
                    data=file.read(),
                    file_name="root_cause_analysis_map.png",
                    mime="image/png",
                    use_container_width=True
                )
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Generate Root Cause Map", use_container_width=True, type="primary"):
                    if hasattr(st.session_state, 'analysis_result'):
                        with st.spinner("Creating root cause map visualization..."):
                            try:
                                mindmap_code = generate_analysis_mindmap(st.session_state.analysis_result)
                                mindmap_path = create_plantuml_diagram(mindmap_code, "analysis_mindmap")

                                if mindmap_path and os.path.exists(mindmap_path):
                                    st.session_state.mindmap_path = mindmap_path
                                    st.success("Root cause map generated!")
                                    st.rerun()
                                else:
                                    st.error("Failed to generate root cause map")
                            except Exception as e:
                                st.error(f"Root cause map generation failed: {str(e)}")
                    else:
                        st.warning("Please complete an analysis first")
    else:
        st.info("Please complete an analysis first to generate root cause map")

elif selected == "Resolution Plan":
    st.markdown("### Root Cause Resolution Plan")

    if hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete:
        if hasattr(st.session_state, 'wbs_path') and os.path.exists(st.session_state.wbs_path):
            st.image(st.session_state.wbs_path, use_container_width=True)

            with open(st.session_state.wbs_path, "rb") as file:
                st.download_button(
                    label="Download Resolution Plan",
                    data=file.read(),
                    file_name="root_cause_resolution_plan.png",
                    mime="image/png",
                    use_container_width=True
                )
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Generate Resolution Plan", use_container_width=True, type="primary"):
                    if hasattr(st.session_state, 'analysis_result'):
                        with st.spinner("Creating resolution plan..."):
                            try:
                                wbs_code = generate_improvement_wbs(st.session_state.analysis_result)
                                wbs_path = create_plantuml_diagram(wbs_code, "improvement_wbs")

                                if wbs_path and os.path.exists(wbs_path):
                                    st.session_state.wbs_path = wbs_path
                                    st.success("Resolution plan generated!")
                                    st.rerun()
                                else:
                                    st.error("Failed to generate resolution plan")
                            except Exception as e:
                                st.error(f"Resolution plan generation failed: {str(e)}")
                    else:
                        st.warning("Please complete an analysis first")
    else:
        st.info("Please complete an analysis first to generate resolution plan")

elif selected == "Settings":
    st.markdown("### Configuration")

    if api_key:
        st.success(f"Groq API Key: Configured (ends with ...{api_key[-4:]})")
    else:
        st.error("Groq API Key: Not found in .env file")
        st.code('GROQ_API_KEY=your_api_key_here')

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <strong>Root Cause Analysis Platform</strong> | Powered by OpenCV, Groq AI & PlantUML | Built with Streamlit
</div>
""", unsafe_allow_html=True)