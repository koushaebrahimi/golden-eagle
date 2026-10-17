# 🦅 Golden Eagle (عقاب زرین)

**Daily Work Time Recording System**

A cross-platform desktop application designed to make daily time-tracking and monthly analysis easier for the Captain and coworkers. 

## ✨ Features
- **Bilingual UI:** Persian and English support.
- **Time Tracking:** Precise `HH:MM` input.
- **Task Management:** Add tasks and subtasks with automatic hour summation.
- **Day Types:** Normal, Leave, Holiday, Overtime, and Remote work.
- **Reports:** Export monthly reports to CSV and PDF.
- **Consistency Check:** Automatically validates in/out times against task hours.

## 🚀 How to Run (Development)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt

2. Run the app:

bash'''
python golden_eagle.py
'''

## 📦 Building the Windows Executable

The repository is configured with GitHub Actions. Every push to the main branch automatically builds a Windows .exe file. You can download it from the Actions tab.

## 📂 File Structure
- golden_eagle.py: Main UI application.

- golden_eagle_core.py: Backend logic (calculations, JSON, PDF).

- lang.py: Translations dictionary.

- requirements.txt: Python dependencies.
