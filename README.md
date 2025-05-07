# LLM-for-SA
 A tool to generate software design document using LLM models

 # Steps to run locally the first time

 1. Clone the repository
 2. Open terminal and go to where repo was cloned.

        cd <repo name>

 4. Run this command there

        python -m venv venv

 5. Then run this command to activate the virtual environment 

        For macOS/Linux:
            
            source venv/bin/activate

        For Windows (PowerShell)
        
            .\venv\Scripts\Activate.ps1
        
        (If you get the error saying running scripts is disabled on this system… -> Run this command in the root folder in PowerShell)

            Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

            (When prompted, type Y and press Enter.)

 7. To install dependencies run this command:
        
        pip install -r requirements.txt

 8. Then this command to run the tool

        python gui.py
 
  
# After setting up for the first time:
1.  Navigate to your project folder
2.  Activate the existing virtual venv (Step 4 from earlier)
3.  Install dependencies again only if any changes or additions made
4.  Run the tool with the same command as before
