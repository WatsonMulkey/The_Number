@echo off
REM Rebuild the Resume Tailor executable and verify
cd /d C:\Users\watso\Dev\resume-tailor
claude -p "Rebuild the resume-tailor exe using PyInstaller. Run: python -m PyInstaller --onefile --windowed --name \"Resume Tailor\" --icon=NONE --add-data \"import_career_data.py;.\" --add-data \"generator.py;.\" --add-data \"pdf_generator.py;.\" --add-data \"html_template.py;.\" --add-data \"docx_generator.py;.\" --add-data \"conflict_detector.py;.\" --add-data \"provenance.py;.\" --add-data \"trace_validator.py;.\" --add-data \".env;.\" --hidden-import anthropic --hidden-import dotenv --hidden-import docx --hidden-import reportlab resume_tailor_gui.py. Then verify dist/Resume Tailor.exe exists and report its size and path." --allowedTools "Bash,Read,Glob"
