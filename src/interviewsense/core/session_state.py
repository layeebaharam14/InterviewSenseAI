"""Session state initialisation for InterviewSense AI."""
import streamlit as st
import uuid


def init_session_state():
    """Initialize necessary session state variables."""
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 'Home'
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'landing'
    if 'current_questions' not in st.session_state:
        st.session_state.current_questions = []
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'video_results' not in st.session_state:
        st.session_state.video_results = []
    if 'audio_results' not in st.session_state:
        st.session_state.audio_results = []
    if 'question_spoken' not in st.session_state:
        st.session_state.question_spoken = False
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    if 'frames' not in st.session_state:
        st.session_state.frames = []
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'hardware_verified' not in st.session_state:
        st.session_state.hardware_verified = False
    if 'last_audio_error' not in st.session_state:
        st.session_state.last_audio_error = None
    if 'candidate_name' not in st.session_state:
        st.session_state.candidate_name = ""
    if 'technical_domain' not in st.session_state:
        st.session_state.technical_domain = "Python Programming"
    if 'technical_skills' not in st.session_state:
        st.session_state.technical_skills = []
    if 'technical_difficulty' not in st.session_state:
        st.session_state.technical_difficulty = "Intermediate"
    if 'technical_num_questions' not in st.session_state:
        st.session_state.technical_num_questions = "5 Questions"
    if 'previous_technical_domain' not in st.session_state:
        st.session_state.previous_technical_domain = "Python Programming"
    if 'technical_questions' not in st.session_state:
        st.session_state.technical_questions = []
    if 'technical_question_index' not in st.session_state:
        st.session_state.technical_question_index = 0
    if 'technical_interview_stage' not in st.session_state:
        st.session_state.technical_interview_stage = "QUESTION_DISPLAY"
    if 'technical_recording_start_time' not in st.session_state:
        st.session_state.technical_recording_start_time = None
    if 'technical_recording_duration' not in st.session_state:
        st.session_state.technical_recording_duration = 15
    if 'technical_frames' not in st.session_state:
        st.session_state.technical_frames = {}
    if 'technical_video_results' not in st.session_state:
        st.session_state.technical_video_results = {}
    if 'technical_audio_results' not in st.session_state:
        st.session_state.technical_audio_results = {}
    if 'technical_overall_visual_analysis' not in st.session_state:
        st.session_state.technical_overall_visual_analysis = None
    if 'technical_hardware_verified' not in st.session_state:
        st.session_state.technical_hardware_verified = False
    if 'technical_session_id' not in st.session_state:
        st.session_state.technical_session_id = uuid.uuid4().hex[:10]
    if 'technical_audio_files' not in st.session_state:
        st.session_state.technical_audio_files = {}
    if 'technical_transcripts' not in st.session_state:
        st.session_state.technical_transcripts = {}
    if 'technical_raw_transcripts' not in st.session_state:
        st.session_state.technical_raw_transcripts = {}
    if 'technical_answers' not in st.session_state:
        st.session_state.technical_answers = {}
    if 'technical_interview_completed' not in st.session_state:
        st.session_state.technical_interview_completed = False
    if 'technical_interview_submitted' not in st.session_state:
        st.session_state.technical_interview_submitted = False
    if 'confirm_end_technical' not in st.session_state:
        st.session_state.confirm_end_technical = False
    if 'confirm_submit_technical' not in st.session_state:
        st.session_state.confirm_submit_technical = False
    if 'technical_evaluation_results' not in st.session_state:
        st.session_state.technical_evaluation_results = None
    if 'technical_overall_score' not in st.session_state:
        st.session_state.technical_overall_score = 0
    if 'technical_performance_level' not in st.session_state:
        st.session_state.technical_performance_level = "Needs Improvement"
    if 'technical_evaluation_completed' not in st.session_state:
        st.session_state.technical_evaluation_completed = False

