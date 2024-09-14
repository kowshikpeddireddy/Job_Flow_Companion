import os
from flask import Flask, render_template, redirect, request,send_from_directory
from resume_screening import job
import subprocess
from flask import jsonify
app = Flask(__name__, template_folder='templates',static_folder='static')
# Ensure that the 'resume_files' directory exists
resume_files_dir = os.path.join(app.instance_path, 'resume_files')
os.makedirs(resume_files_dir, exist_ok=True)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/employee')
def employee():
    return render_template('employee.html')
@app.route("/home")
def home():
    return redirect('/')
@app.route('/employee_submit', methods=['POST'])
def employee_submit_data():
    if request.method == 'POST':
        f = request.files['userfile']
        # Ensure that the 'resume_files' directory exists
        os.makedirs(resume_files_dir, exist_ok=True)
        f.save(os.path.join(resume_files_dir, f.filename))

    path = os.path.join(resume_files_dir, f.filename)
    result_cosine = job.find_sort_job(path)
    return render_template('employee.html', column_names=result_cosine.columns.values, row_data=list(result_cosine.values.tolist()),
                           link_column="Link", zip=zip)
@app.route('/chatbot')
def chatbot():
    # Call the chatbot code as a subprocess
    subprocess.Popen(['python', 'bot.py'])
    return render_template('chatbot.html')

@app.route('/ai.html')
def ai_page():
    return render_template('ai.html')
@app.route('/ds.html')
def ds_page():
    return render_template('ds.html')
@app.route('/cs.html')
def cs_page():
    return render_template('cs.html')
@app.route('/cc.html')
def cc_page():
    return render_template('cc.html')
# Route to serve static files
#@app.route('/static/<path:filename>')
#def serve_static(filename):
    #return send_from_directory(app.static_folder, filename)

# Route to serve interview_tips.html
@app.route('/interview_tips.html')
def serve_interview_tips():
    return send_from_directory(app.static_folder, 'interview_tips.html')

# Route to serve resume.html
@app.route('/resume.html')
def serve_resume_template():
    return render_template('resume.html')
    #return send_from_directory(app.template_folder, filename)
@app.route('/roles.html')
def serve_role_template():
    return render_template('roles.html')
@app.route('/ui')
def tkinter_interaction():
    # Run the Tkinter app as a subprocess
    subprocess.Popen(['python', 'ui.py'])
    return render_template('tkinter.html')


@app.errorhandler(500)
def internal_server_error(e):
     app.logger.error("Internal Server Error: " + str(e))
     return "Internal Server Error: " + str(e)


if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)




