import os

# Base directory for the project
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

# Data and logging directories
DATA_DIR = os.path.join(ROOT, 'question-data')
LOGS_DIR = os.path.join(ROOT, 'logs')

# --- Quiz Data Files ---

# JSON files
JSON_DIR = os.path.join(DATA_DIR, 'json')
DEFAULT_DATA_FILE = os.path.join(JSON_DIR, 'ckad_quiz_data.json')
# Built-in YAML-edit quiz data (JSON form)
# The JSON source for YAML editing exercises is named 'yaml_edit.json'
YAML_QUESTIONS_FILE = os.path.join(JSON_DIR, 'yaml_edit.json')
# Built-in Vim quiz data file (JSON-based quiz)
VIM_QUESTIONS_FILE = os.path.join(DATA_DIR, 'json', 'vim.json')
KUBECTL_OPERATIONS_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_operations_quiz.yaml')
KUBECTL_RESOURCE_TYPES_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_resource_types.yaml')
# Renamed syntax quiz from kubectl_syntax_quiz.yaml
KUBECTL_BASIC_SYNTAX_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_basic_syntax_quiz.yaml')
HELM_BASICS_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'helm_basics_quiz.yaml')
KUBECTL_SHELL_SETUP_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_shell_setup_quiz.yaml')
KUBECTL_POD_MANAGEMENT_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_pod_management_quiz.yaml')
KUBECTL_DEPLOYMENT_MANAGEMENT_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_deployment_management_quiz.yaml')
KUBECTL_NAMESPACE_OPERATIONS_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_namespace_operations_quiz.yaml')
KUBECTL_CONFIGMAP_OPERATIONS_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_configmap_operations_quiz.yaml')
KUBECTL_SECRET_MANAGEMENT_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_secret_management_quiz.yaml')
KUBECTL_SERVICE_ACCOUNT_OPS_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_service_account_ops_quiz.yaml')
KUBECTL_ADDITIONAL_COMMANDS_QUIZ_FILE = os.path.join(DATA_DIR, 'yaml', 'kubectl_additional_commands_quiz.yaml')


# --- Enabled Quizzes ---
# Quizzes that appear as primary options in the interactive menu.
ENABLED_QUIZZES = {
    "Vim Quiz": VIM_QUESTIONS_FILE,
    "Kubectl Basic Syntax": KUBECTL_BASIC_SYNTAX_QUIZ_FILE,
    "Kubectl Operations": KUBECTL_OPERATIONS_QUIZ_FILE,
    "Kubectl Resource Types": KUBECTL_RESOURCE_TYPES_QUIZ_FILE,
    "Helm Basics": HELM_BASICS_QUIZ_FILE,
    "Kubectl Shell Setup": KUBECTL_SHELL_SETUP_QUIZ_FILE,
    "Kubectl Pod Management": KUBECTL_POD_MANAGEMENT_QUIZ_FILE,
    "Kubectl Deployment Management": KUBECTL_DEPLOYMENT_MANAGEMENT_QUIZ_FILE,
    "Kubectl Namespace Operations": KUBECTL_NAMESPACE_OPERATIONS_QUIZ_FILE,
    "Kubectl ConfigMap Operations": KUBECTL_CONFIGMAP_OPERATIONS_QUIZ_FILE,
    "Kubectl Secret Management": KUBECTL_SECRET_MANAGEMENT_QUIZ_FILE,
    "Kubectl Service Account Operations": KUBECTL_SERVICE_ACCOUNT_OPS_QUIZ_FILE,
    "Kubectl Additional Commands": KUBECTL_ADDITIONAL_COMMANDS_QUIZ_FILE,
}

# CSV files
CSV_DIR = os.path.join(DATA_DIR, 'csv')
# Killercoda CKAD CSV quiz file
KILLERCODA_CSV_FILE = os.path.join(CSV_DIR, 'killercoda-ckad_072425.csv')
KILLERCODA_CSV_FILE = os.path.join(CSV_DIR, 'killercoda-ckad_072425.csv')

# --- History and Logging ---
HISTORY_FILE = os.path.join(LOGS_DIR, '.cli_quiz_history.json')
INPUT_HISTORY_FILE = os.path.join(LOGS_DIR, '.kubelingo_input_history')
VIM_HISTORY_FILE = os.path.join(LOGS_DIR, '.kubelingo_vim_history')
LOG_FILE = os.path.join(LOGS_DIR, 'quiz_log.txt')
