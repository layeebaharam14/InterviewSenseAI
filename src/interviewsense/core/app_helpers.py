"""Shared helper functions for the InterviewSense AI application."""
import streamlit as st
import streamlit.components.v1 as components
import cv2
import threading
import speech_recognition as sr
import re
import uuid
from datetime import datetime

from src.interviewsense.services.technical_speech import record_and_transcribe_audio


QUESTION_POOL = [
    "What are your strengths?",
    "What is your biggest weakness?",
    "Describe a challenge you faced and how you handled it.",
    "Tell me about a time you worked in a team.",
    "Why should we hire you?",
    "Where do you see yourself in 5 years?",
    "Tell me about a failure and what you learned.",
    "How do you handle pressure or deadlines?",
    "Describe a leadership experience.",
    "Why are you interested in this role?"
]

def get_question_duration(question):
    q = question.lower()
    if "tell me about yourself" in q:
        return 30
    if "challenge" in q or "situation" in q:
        return 25
    if "team" in q or "leadership" in q or "failure" in q:
        return 25
    if "strength" in q or "weakness" in q or "hire you" in q or "5 years" in q or "pressure" in q or "role" in q:
        return 20
    return 15

def get_technical_question_duration(q_data=None):
    """Fixed 15-second answer duration for all technical interview questions."""
    return 15

def get_camera():
    # Try cameras 0 (default), 1, 2 with CAP_DSHOW for Windows compatibility
    for index in [0, 1, 2]:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Using camera: {index} with CAP_DSHOW")
                return cap
        cap.release()

    # Fallback without CAP_DSHOW
    for index in [0, 1, 2]:
        cap = cv2.VideoCapture(index)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Using camera: {index} without CAP_DSHOW")
                return cap
        cap.release()

    return None

def record_and_transcribe(duration, result_container, domain=None, skills=None, audio_file_path=None):
    """
    Records audio and performs technical speech recognition with contextual normalization.
    Fully backward-compatible with Mock HR Interview when called with (duration, result_container).
    """
    return record_and_transcribe_audio(
        duration=duration,
        result_container=result_container,
        domain=domain,
        skills=skills,
        audio_file_path=audio_file_path
    )

def record_technical_voice_answer(duration=15, domain=None, skills=None, audio_file_path=None):
    """Records audio from microphone and returns (success: bool, text_or_error: str) for Technical Interview."""
    res = []
    record_and_transcribe_audio(
        duration=duration,
        result_container=res,
        domain=domain,
        skills=skills,
        audio_file_path=audio_file_path
    )
    if not res:
        return False, "No audio response recorded."
    first_res = res[0]
    if first_res.startswith("ERROR:"):
        return False, first_res.replace("ERROR:", "").strip()
    return True, first_res.strip()

def save_current_technical_answer(curr_idx, method=None, raw_transcript=None, audio_path=None):
    """Persists the current question's answer from session state into technical_answers with audio recovery paths."""
    if 'technical_questions' not in st.session_state or not st.session_state.technical_questions:
        return
    if curr_idx < 0 or curr_idx >= len(st.session_state.technical_questions):
        return
    curr_q_data = st.session_state.technical_questions[curr_idx]
    ans_text = st.session_state.get(f"tech_ans_input_{curr_idx}", "").strip()
    
    existing_entry = st.session_state.technical_answers.get(curr_idx, {})
    if method is None:
        method = existing_entry.get("answer_method", "text") if ans_text else "text"
        
    st.session_state.technical_answers[curr_idx] = {
        "question_id": curr_idx + 1,
        "question": curr_q_data.get("question", ""),
        "domain": curr_q_data.get("domain", st.session_state.technical_domain),
        "skill": curr_q_data.get("skill", "General"),
        "difficulty": curr_q_data.get("difficulty", st.session_state.technical_difficulty),
        "question_type": curr_q_data.get("question_type", "Conceptual"),
        "answer_text": ans_text,
        "answer_method": method,
        "raw_transcript": raw_transcript or existing_entry.get("raw_transcript", ""),
        "audio_path": audio_path or existing_entry.get("audio_path", "")
    }


