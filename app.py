import streamlit as st
import os

def is_excluded_folder(path):
    excluded_folders = {'venv', '.git', 'node_modules', '.venv'}
    path_parts = path.split(os.sep)
    return any(part in excluded_folders for part in path_parts)

def is_code_file(file_name):
    code_extensions = {'.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.rb', '.go', '.ts', '.md', '.json', '.yml', '.yaml'}
    return any(file_name.endswith(ext) for ext in code_extensions)

def get_folder_structure(path):
    structure = []
    for root, dirs, files in os.walk(path):
        if is_excluded_folder(root):
            continue
        level = root.replace(path, '').count(os.sep)
        indent = '&nbsp;' * 4 * level
        folder_name = os.path.basename(root)
        structure.append(f"<span style='color: black;'>{indent}{folder_name}/</span>")
        for file in files:
            is_excluded_file = not is_code_file(file)
            color = 'red' if is_excluded_file else 'black'
            structure.append(f"<span style='color: {color};'>{indent}&nbsp;&nbsp;&nbsp;&nbsp;{file}</span>")
    return '<br>'.join(structure)

def consolidate_code(folder_path, progress_bar, progress_text):
    consolidated_code = ""
    all_files = []
    for root, _, files in os.walk(folder_path):
        if is_excluded_folder(root):
            continue
        all_files.extend([os.path.join(root, file) for file in files if is_code_file(file)])
    total_files = len(all_files)
    
    for i, file_path in enumerate(all_files):
        file_size = os.path.getsize(file_path) / 1024  # Size in KB
        progress_text.text(f"Converting file {i+1}/{total_files}: {file_path} ({file_size:.2f} KB)")
        progress_bar.progress((i + 1) / total_files)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        file_extension = os.path.splitext(file_path)[1][1:]  # Remove the dot
        consolidated_code += f"# File: {file_path}\n\n```{file_extension}\n{content}\n```\n\n"
    
    return consolidated_code

st.set_page_config(layout="wide")
st.title('Code Consolidation App')

folder_path = st.text_input('Enter the path to your project folder:')

if folder_path:
    if st.button('Scan'):
        structure = get_folder_structure(folder_path)
        st.markdown(f"""
        <div style="border:1px solid #ccc; padding:10px; max-height:400px; overflow-y:scroll; font-size:0.8em;">
        {structure}
        </div>
        """, unsafe_allow_html=True)

    if st.button('Convert'):
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        with st.spinner('Consolidating code...'):
            consolidated_code = consolidate_code(folder_path, progress_bar, progress_text)
            st.text_area("Consolidated Code", consolidated_code, height=300)
            st.download_button(
                label="Download consolidated code as MD",
                data=consolidated_code,
                file_name="consolidated_code.md",
                mime="text/markdown"
            )
        
        progress_text.text("Conversion completed!")