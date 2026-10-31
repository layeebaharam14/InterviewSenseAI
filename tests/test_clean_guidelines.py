import textwrap

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

start = code.find('elif st.session_state.current_tab == "Guidelines":')
md_start = code.find('st.markdown("""', start) + len('st.markdown("""')
md_end = code.find('""", unsafe_allow_html=True)', md_start)
md_text = code[md_start:md_end]

dedented = textwrap.dedent(md_text)
# Remove blank lines that cause markdown to think next lines are code blocks
lines = [l.strip() for l in dedented.splitlines() if l.strip()]
cleaned_html = "".join(lines)

print("Cleaned HTML length:", len(cleaned_html))
print("Starts with:", cleaned_html[:60])
print("Contains '<div class=\"guidelines-grid\">':", '<div class="guidelines-grid">' in cleaned_html)

