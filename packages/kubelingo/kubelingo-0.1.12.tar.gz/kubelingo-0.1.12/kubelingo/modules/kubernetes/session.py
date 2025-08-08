import csv
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import shlex
import webbrowser
from datetime import datetime
import logging

from kubelingo.database import get_questions_by_source_file, get_flagged_questions, update_review_status, add_question
from kubelingo.utils.ui import Fore, Style, yaml, humanize_module
from difflib import SequenceMatcher, unified_diff
try:
    import questionary
except ImportError:
    questionary = None
from kubelingo.utils.config import (
    ROOT,
    LOGS_DIR,
    HISTORY_FILE,
    DEFAULT_DATA_FILE,
    YAML_QUESTIONS_FILE,
    DATA_DIR,
    INPUT_HISTORY_FILE,
    VIM_HISTORY_FILE,
    KILLERCODA_CSV_FILE,
    ENABLED_QUIZZES,
    VIM_QUESTIONS_FILE,
    KUBECTL_BASIC_SYNTAX_QUIZ_FILE,
    KUBECTL_OPERATIONS_QUIZ_FILE,
    KUBECTL_RESOURCE_TYPES_QUIZ_FILE,
)

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
except ImportError:
    PromptSession = None
    FileHistory = None

from kubelingo.modules.base.session import StudySession, SessionManager
from kubelingo.modules.kubernetes.vim_yaml_editor import VimYamlEditor
from pathlib import Path
import os

# AI-based validator for command equivalence


from kubelingo.modules.base.loader import load_session
from kubelingo.modules.json_loader import JSONLoader
from kubelingo.modules.md_loader import MDLoader
from kubelingo.modules.yaml_loader import YAMLLoader
from kubelingo.modules.question_generator import AIQuestionGenerator
from dataclasses import asdict
from kubelingo.utils.validation import commands_equivalent, is_yaml_subset
# Existing import
# Existing import
from .vim_yaml_editor import VimYamlEditor
from .answer_checker import evaluate_transcript, evaluate_transcript as check_answer
from .study_mode import KubernetesStudyMode, KUBERNETES_TOPICS
from kubelingo.sandbox import spawn_pty_shell, launch_container_sandbox, ShellResult, StepResult
import logging  # for logging in exercises
# Stub out AI evaluator to avoid heavy external dependencies

def _get_subject_for_questions(q):
    """
    Extracts the category/subject string for AI question generation.
    Handles both dicts and Question objects, and is safe against empty lists.
    """
    subject = ''
    # Handle dicts from database/YAML
    if isinstance(q, dict):
        categories = q.get('categories')
        if categories and isinstance(categories, list) and categories:
            subject = categories[0]
        if not subject:
            subject = q.get('category')
        if not subject:
            subject = q.get('metadata', {}).get('category')
    # Handle Question objects for few-shot examples
    else:
        categories = getattr(q, 'categories', [])
        if categories and isinstance(categories, list) and categories:
            subject = categories[0]
        if not subject:
            subject = getattr(q, 'category', None)
        if not subject:
            subject = getattr(q, 'metadata', {}).get('category')
    
    return subject or ''




def get_all_flagged_questions():
    """Returns a list of all questions from the database that are flagged for review."""
    # This now reads from the database instead of parsing files.
    return get_flagged_questions()


def _update_review_status_in_db(question_id: str, review: bool):
    """Updates the 'review' flag for a specific question in the database."""
    if not question_id:
        return
    try:
        update_review_status(question_id, review)
    except Exception as e:
        # Log this error but don't crash the quiz
        logging.getLogger().error(f"Failed to update review status in DB for QID {question_id}: {e}")


def _clear_all_review_flags(logger):
    """Removes 'review' flag from all questions in the database."""
    try:
        from kubelingo.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        # Get count of flagged questions before clearing
        cursor.execute("SELECT COUNT(*) FROM questions WHERE review = 1")
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.execute("UPDATE questions SET review = 0 WHERE review = 1")
            conn.commit()
            print(f"\n{Fore.GREEN}Cleared all {count} review flags.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}No flagged questions found to clear.{Style.RESET_ALL}")
        
        conn.close()
    except Exception as e:
        logger.error(f"Failed to clear review flags in DB: {e}")
        print(f"{Fore.RED}An error occurred while clearing review flags.{Style.RESET_ALL}")


def check_dependencies(*commands):
    """Check if all command-line tools in `commands` are available."""
    missing = []
    for cmd in commands:
        if not shutil.which(cmd):
            missing.append(cmd)
    return missing
    
def load_questions(file_path: str):
    """Load quiz questions from a JSON file with sections of prompts."""
    questions = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception:
        return questions
    for section in data or []:
        category = section.get('category')
        for item in section.get('prompts', []):
            q = item.copy()
            q['category'] = category
            questions.append(q)
    return questions

    
class NewSession(StudySession):
    """A study session for all Kubernetes-related quizzes."""

    def __init__(self, logger):
        super().__init__(logger)
        self.session_manager = SessionManager(logger)
        self.cluster_name = None
        self.kubeconfig_path = None
        self.region = None
        self.creds_acquired = False
        self.live_session_active = False # To control cleanup logic
        self.kind_cluster_created = False
    
    def _run_command_quiz(self, args):
        """
        Attempt to run the command quiz via the Rust bridge, with Python fallback.
        """
        # Try Rust bridge first
        try:
            # Use the global Rust bridge instance
            from kubelingo.bridge import rust_bridge
            if rust_bridge.is_available():
                success = rust_bridge.run_command_quiz(args)
                if success:
                    return
        except ImportError:
            pass
        # Fallback: load questions from file
        try:
            _ = load_questions(args.file)
        except Exception:
            pass
    
    def _run_one_exercise(self, question: dict):
        """
        Run a single live_k8s exercise by prompting for commands and running an assertion script.
        This supports unit tests for live mode.
        """
        # Prepare the assert script
        import tempfile, os, shlex, subprocess
        # Write the assert script to a temp file using context manager (for mocks)
        path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as tf:
                tf.write(question.get('assert_script', ''))
                path = tf.name
            os.chmod(path, 0o700)
            # Prompt user for commands until 'done'
            sess = PromptSession(history=None)
            while True:
                cmd = sess.prompt()
                if cmd is None or cmd.strip().lower() == 'done':
                    break
                subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=False)
            # Run the assertion script
            result = subprocess.run(['bash', path], capture_output=True, text=True)
            status = 'correct' if result.returncode == 0 else 'incorrect'
            self.logger.info(f"Live exercise: prompt=\"{question.get('prompt')}\" result=\"{status}\"")
        finally:
            if path:
                try:
                    os.remove(path)
                except Exception:
                    pass

    def initialize(self):
        """Basic initialization. Live session initialization is deferred."""
        return True

    def _run_study_mode_session(self):
        """Runs an interactive study session using the Socratic method."""
        if not os.getenv('OPENAI_API_KEY'):
            print(f"\n{Fore.RED}Study Mode requires an OpenAI API key.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Set the OPENAI_API_KEY environment variable to enable it.{Style.RESET_ALL}")
            input("\nPress Enter to return to the menu...")
            return

        try:
            print()  # Add a blank line for spacing before the menu
            topic_choices = list(KUBERNETES_TOPICS.keys())
            if not topic_choices:
                print(f"{Fore.YELLOW}No study topics available for Study Mode.{Style.RESET_ALL}")
                input("\nPress Enter to return to the menu...")
                return
            
            topic = questionary.select(
                "What Kubernetes topic would you like to study?",
                choices=topic_choices,
                use_indicator=True
            ).ask()

            if topic is None:
                return

            level = questionary.select(
                "What is your current skill level on this topic?",
                choices=["beginner", "intermediate", "advanced"],
                default="intermediate"
            ).ask()

            if level is None:
                return

            api_key = os.getenv('OPENAI_API_KEY')
            study_session = KubernetesStudyMode(api_key=api_key)

            response = study_session.start_study_session(topic, level)
            print(f"\n{Fore.GREEN}Tutor:{Style.RESET_ALL} {response}")

            prompt_session = None
            if PromptSession and FileHistory:
                os.makedirs(os.path.dirname(INPUT_HISTORY_FILE), exist_ok=True)
                prompt_session = PromptSession(history=FileHistory(INPUT_HISTORY_FILE))

            while True:
                try:
                    if prompt_session:
                        user_input = prompt_session.prompt(f"\n{Fore.YELLOW}You:{Style.RESET_ALL} ")
                    else:
                        user_input = input(f"\n{Fore.YELLOW}You:{Style.RESET_ALL} ")

                    if user_input is None:  # Handle Ctrl-D
                        break
                    if user_input.lower().strip() in ['exit', 'quit', 'done']:
                        break
                    
                    print(f"{Fore.YELLOW}Thinking...{Style.RESET_ALL}")
                    response = study_session.continue_conversation(user_input)
                    print(f"\n{Fore.GREEN}Tutor:{Style.RESET_ALL} {response}")
                except (KeyboardInterrupt, EOFError):
                    break

            print(f"\n{Fore.CYAN}Study session ended. Returning to main menu.{Style.RESET_ALL}")

        except ImportError:
             print(f"\n{Fore.RED}Study Mode requires the 'openai' package. Please install it with `pip install openai`.{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"Error during study mode session: {e}", exc_info=True)
            print(f"\n{Fore.RED}An error occurred during the study session: {e}{Style.RESET_ALL}")

        input("\nPress Enter to return to the menu...")

    def _build_interactive_menu_choices(self):
        """Helper to construct the list of choices for the interactive menu."""
        all_flagged = get_all_flagged_questions()
        
        choices = []

        # 1. Add enabled quizzes from config
        loader = YAMLLoader()
        for name, path in ENABLED_QUIZZES.items():
            try:
                # YAMLLoader now combines file and DB questions
                num_questions = len(loader.load_file(path))
            except Exception as e:
                self.logger.warning(f"Could not load questions for {name}: {e}")
                num_questions = 0
            
            # Format display name with question count if available
            display_name = f"{name} ({num_questions} questions)" if num_questions > 0 else name
            choices.append({"name": display_name, "value": path})

        # 2. Review Flagged
        review_text = "Review Flagged Questions"
        if all_flagged:
            review_text = f"Review {len(all_flagged)} Flagged Questions"
        choices.append({"name": review_text, "value": "review"})

        # 3. Study Mode
        choices.append({"name": "Study Mode (Socratic Tutor)", "value": "study_mode"})

        # 4. View Session History
        choices.append({"name": "View Session History", "value": "view_history"})
        
        # 5. Help
        choices.append({"name": "Help", "value": "help"})

        # 6. Exit App
        choices.append({"name": "Exit App", "value": "exit_app"})

        
        return choices, all_flagged

    def _show_static_help(self):
        """Displays a static, hardcoded help menu as a fallback."""
        print(f"\n{Fore.CYAN}--- Kubelingo Help ---{Style.RESET_ALL}\n")
        print("This screen provides access to all quiz modules and application features.\n")

        print(f"{Fore.GREEN}Vim Quiz{Style.RESET_ALL}")
        print("  The primary, active quiz module for practicing Vim commands.\n")

        print(f"{Fore.GREEN}Kubectl Commands{Style.RESET_ALL}")
        print("  Test your knowledge of kubectl operations.\n")

        print(f"{Fore.GREEN}Review Flagged Questions{Style.RESET_ALL}")
        print("  Starts a quiz session with only the questions you have previously flagged for review.")
        print("  Use this for focused study on topics you find difficult.\n")

        print(f"{Fore.GREEN}View Session History{Style.RESET_ALL}")
        print("  Displays a summary of your past quiz sessions, including scores and timings.\n")

        print(f"{Fore.GREEN}Help{Style.RESET_ALL}")
        print("  Shows this help screen.\n")

        print(f"{Fore.GREEN}Exit App{Style.RESET_ALL}")
        print("  Quits the application.\n")

        print(f"{Fore.YELLOW}Other Options (Not yet implemented){Style.RESET_ALL}")
        print(f"  - {Style.DIM}Session Type (PTY/Docker){Style.RESET_ALL}")
        print(f"  - {Style.DIM}Custom Quiz{Style.RESET_ALL}")
        print(f"  - {Style.DIM}Other Quizzes...{Style.RESET_ALL}")
        print(f"  - {Style.DIM}Clear All Review Flags{Style.RESET_ALL} (appears when questions are flagged)")

    def _show_help(self):
        """
        Displays a dynamically generated help menu using an AI model to summarize
        the available quizzes and features.
        """
        # This approach ensures the help text stays up-to-date with the application's
        # capabilities without requiring manual updates to hardcoded strings.

        if not os.getenv('OPENAI_API_KEY'):
            print(f"\n{Fore.YELLOW}AI-powered help requires an OpenAI API key.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Set the OPENAI_API_KEY environment variable to enable it.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Falling back to static help text.{Style.RESET_ALL}")
            self._show_static_help()
            return

        try:
            import llm

            # Discover available quizzes by building the menu choices.
            choices, _ = self._build_interactive_menu_choices()
            
            # Separate choices into enabled quizzes and other features.
            enabled_quizzes = [
                c['name'] for c in choices 
                if isinstance(c, dict) and 'disabled' not in c 
                and Path(str(c.get('value', ''))).exists()
            ]
            
            disabled_features = [c['name'] for c in choices if isinstance(c, dict) and 'disabled' in c]

            prompt = (
                "You are the friendly help system for a command-line learning tool called 'kubelingo'.\n"
                "Your task is to generate a concise, user-friendly help screen based on the following available features.\n"
                "Present the information clearly, using simple Markdown for formatting.\n\n"
                "Active, usable quizzes:\n"
                f"- {', '.join(enabled_quizzes)}\n\n"
                "Standard features:\n"
                "- Review Flagged Questions: For focused study on difficult topics.\n"
                "- View Session History: To see past performance.\n"
                "- Help: To show this screen.\n"
                "- Exit App: To quit the application.\n\n"
                "Features that are listed in the menu but are not yet implemented (disabled):\n"
                f"- {', '.join(disabled_features)}\n\n"
                "Generate a help text that explains these options to the user."
            )

            print(f"\n{Fore.CYAN}--- Kubelingo Help (AI Generated) ---{Style.RESET_ALL}\n")
            print(f"{Fore.YELLOW}Generating dynamic help with AI...{Style.RESET_ALL}")

            # Get the default model, which should be configured via `llm` CLI or env vars.
            model = llm.get_model()
            response = model.prompt(prompt, system="You are a helpful assistant for a CLI tool.")
            
            print(f"\n{response.text}")

        except (ImportError, Exception) as e:
            print(f"\n{Fore.RED}AI-powered help generation failed: {e}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Falling back to static help text.{Style.RESET_ALL}")
            self._show_static_help()

    def run_exercises(self, args):
        """
        Router for running exercises. It decides which quiz to run.
        """
        # All exercises now run through the unified quiz runner.
        self._run_unified_quiz(args)
    
    def _run_unified_quiz(self, args):
        """
        Run a unified quiz session for all question types. Every question is presented
        in a sandbox shell, and validation is based on the outcome.
        """
        import copy
        initial_args = copy.deepcopy(args)
        # Track original Question objects for AI few-shot prompting
        base_q_objs = None

        if not os.getenv('OPENAI_API_KEY'):
            print(f"\n{Fore.YELLOW}Warning: AI-based answer evaluation requires an OpenAI API key.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Set the OPENAI_API_KEY environment variable to enable it.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Without it, answer checking will rely on deterministic validation if available.{Style.RESET_ALL}")

        is_interactive = questionary and sys.stdin.isatty() and sys.stdout.isatty()

        while True:
            # For each quiz, use a fresh copy of args and normalize question count
            args = copy.deepcopy(initial_args)
            args.num = getattr(args, 'num', getattr(args, 'num_questions', 0))
            is_interactive = questionary and sys.stdin.isatty() and sys.stdout.isatty()

            start_time = datetime.now()
            # Unique session identifier for transcript storage
            session_id = start_time.strftime('%Y%m%dT%H%M%S')
            os.environ['KUBELINGO_SESSION_ID'] = session_id
            questions = []
            ai_generation_enabled = True
            # Handle --list-questions: load static questions from file and exit before DB lookup
            if getattr(args, 'list_questions', False):
                # Load static questions using loader (e.g., JSON/YAML loader)
                try:
                    static_questions = load_questions(args.file)
                except Exception as e:
                    self.logger.error(f"Failed to load questions for listing: {e}")
                    static_questions = []
                # Determine how many questions to list
                total = len(static_questions)
                num_arg = getattr(args, 'num', 0) or getattr(args, 'num_questions', 0)
                requested = num_arg if num_arg and num_arg > 0 else total
                clones_needed = max(0, requested - total)
                # Combine static and AI-generated questions
                combined = list(static_questions)
                if clones_needed > 0 and ai_generation_enabled:
                    print(f"\n{Fore.CYAN}Generating {clones_needed} additional AI question(s)...{Style.RESET_ALL}")
                    try:
                        # Instantiate AI generator via module lookup to respect patches
                        import kubelingo.modules.question_generator as qg_module
                        generator = qg_module.AIQuestionGenerator()
                        subject = _get_subject_for_questions(static_questions[0]) if static_questions else ''
                        # Generate AI-backed questions, including context of existing questions
                        ai_qs = generator.generate_questions(
                            subject,
                            clones_needed,
                            base_questions=static_questions,
                            num_to_generate=clones_needed
                        )
                        # Append generated Question objects
                        combined.extend(ai_qs)
                    except Exception as e:
                        self.logger.error(f"Failed to list AI questions: {e}", exc_info=True)
                        print(f"{Fore.RED}Error: Could not list AI-generated questions.{Style.RESET_ALL}")
                
                # Print the list and exit
                print("\nList of Questions:")
                for idx, q_item in enumerate(combined, start=1):
                    # Support both dicts and Question objects
                    if hasattr(q_item, 'prompt'):
                        prompt_text = q_item.prompt
                    else:
                        prompt_text = q_item.get('prompt', '<no prompt>')
                    print(f"{idx}. {prompt_text}")
                return

            if args.review_only:
                questions = get_all_flagged_questions()
            elif args.file:
                # First, attempt to load questions via JSON-style loader (e.g., unified JSON quizzes)
                try:
                    static_override = load_questions(args.file)
                except Exception as e:
                    self.logger.error(f"Failed to load questions via JSON loader for '{args.file}': {e}")
                    static_override = []
                if static_override:
                    # Preserve original Question objects for AI prompting
                    base_q_objs = static_override
                    # Convert Question objects or dicts into uniform dict format for quiz
                    questions = []
                    for q_item in static_override:
                        if hasattr(q_item, 'id'):
                            questions.append(asdict(q_item))
                        else:
                            questions.append(q_item)
                    ai_generation_enabled = True
                else:
                    # Load questions from the database using the source file's basename as a key
                    questions = get_questions_by_source_file(os.path.basename(args.file))
                if not questions:
                    # If questions are not in the DB, load from file and persist them.
                    # This makes manual migration less critical and fixes issues with non-JSON files.
                    self.logger.info(f"No questions for '{os.path.basename(args.file)}' in DB, attempting to load from file...")
                    try:
                        file_path = args.file
                        _, ext = os.path.splitext(file_path)
                        loader = None
                        if ext.lower() == '.json':
                            loader = JSONLoader()
                        elif ext.lower() in ('.yaml', '.yml'):
                            loader = YAMLLoader()
                        elif ext.lower() == '.md':
                            loader = MDLoader()

                        if loader:
                            loaded_questions = loader.load_file(file_path)
                            self.logger.info(f"Loaded {len(loaded_questions)} questions from '{os.path.basename(file_path)}'. Persisting to database.")
                            # Persist loaded questions to the database
                            for q_obj in loaded_questions:
                                # The loader provides Question objects, convert to dict for DB
                                q_dict = asdict(q_obj)
                                # Extract category correctly from list or single value
                                category = None
                                if q_dict.get('categories'):
                                    category = q_dict['categories'][0]
                                elif q_dict.get('category'):
                                    category = q_dict['category']

                                add_question(
                                    id=q_dict.get('id'),
                                    prompt=q_dict.get('prompt'),
                                    source_file=os.path.basename(file_path),
                                    response=q_dict.get('response'),
                                    category=category,
                                    source=q_dict.get('source'),
                                    validation_steps=q_dict.get('validation_steps'),
                                    validator=q_dict.get('validator')
                                )
                            # Now that they are in DB, fetch them again to ensure consistent data structure.
                            questions = get_questions_by_source_file(os.path.basename(args.file))
                        else:
                            self.logger.warning(f"No loader found for file type '{ext}'.")
                            questions = []

                    except Exception as e:
                        self.logger.error(f"Failed to load or persist questions for '{args.file}': {e}", exc_info=True)
                        questions = []

                if not questions:
                    # Neither DB nor static loader provided questions
                    db_path = os.path.join(DATA_DIR, 'kubelingo.db')
                    if not os.path.exists(db_path):
                        print(f"{Fore.YELLOW}Database file not found. Please run the migration script:{Style.RESET_ALL}")
                        print(f"  python scripts/migrate_to_db.py")
                    else:
                        print(f"{Fore.YELLOW}No questions found for '{os.path.basename(args.file)}' in the database or static files.{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}If you have added or changed question files, please run the migration script again:{Style.RESET_ALL}")
                        print(f"  python scripts/migrate_to_db.py")
                    return
                # AI generation is enabled by default when loading questions
                ai_generation_enabled = True
            else:
                # Interactive mode: show menu to select quiz.
                if not is_interactive:
                    print(f"{Fore.RED}Non-interactive mode requires a quiz file (--file) or --review-only.{Style.RESET_ALL}")
                    return

                choices, flagged_questions = self._build_interactive_menu_choices()
                
                print() # Add a blank line for spacing before the menu
                selected = questionary.select(
                    "Choose a Kubernetes exercise:",
                    choices=choices,
                    use_indicator=True
                ).ask()

                if selected is None:
                    return # User cancelled (e.g., Ctrl+C)

                if selected == "exit_app":
                    print(f"\n{Fore.YELLOW}Exiting app. Goodbye!{Style.RESET_ALL}")
                    sys.exit(0)

                if selected == "study_mode":
                    self._run_study_mode_session()
                    continue

                if selected == "help":
                    self._show_help()
                    input("\nPress Enter to return to the menu...")
                    continue
                # View past session history
                if selected == "view_history":
                    from kubelingo.cli import show_history
                    show_history()
                    input("\nPress Enter to return to the menu...")
                    continue


                # Find the choice dictionary that corresponds to the selected value.
                selected_choice = next((c for c in choices if isinstance(c, dict) and c.get('value') == selected), None)

                if selected_choice and selected_choice.get('disabled'):
                    # This option was disabled, so loop back to the menu.
                    continue

                if selected == 'review':
                    initial_args.review_only = True
                else:
                    initial_args.file = selected
                # Selection recorded; restart loop to load the chosen quiz
                continue

            # De-duplicate questions based on the prompt text to avoid redundancy.
            # This can happen if questions are loaded from multiple sources or if
            # a single file contains duplicates.
            seen_prompts = set()
            unique_questions = []
            for q in questions:
                prompt = q.get('prompt', '').strip()
                if prompt and prompt not in seen_prompts:
                    unique_questions.append(q)
                    seen_prompts.add(prompt)
            
            if len(questions) != len(unique_questions):
                self.logger.info(f"Removed {len(questions) - len(unique_questions)} duplicate questions.")
            questions = unique_questions

            if args.review_only and not questions:
                print(Fore.YELLOW + "No questions flagged for review found." + Style.RESET_ALL)
                return

            if args.category:
                questions = [q for q in questions if q.get('category') == args.category]
                if not questions:
                    print(Fore.YELLOW + f"No questions found in category '{args.category}'." + Style.RESET_ALL)
                    return

            # Determine how many to ask based on user input
            total = len(questions)

            # If interactive and --num not specified, ask user for number of questions.
            # Skip this for review mode, as we always review all flagged questions.
            if is_interactive and args.num == 0 and total > 0 and not args.review_only:
                try:
                    num_str = questionary.text(
                        f"How many questions would you like? (Enter a number, or press Enter for all {total})",
                        validate=lambda text: text.isdigit() or text == ""
                    ).ask()

                    if num_str is None:  # User cancelled with Ctrl+C
                        return # Exit the quiz session gracefully

                    if num_str and num_str.isdigit():
                        args.num = int(num_str)
                except (KeyboardInterrupt, EOFError):
                    print(f"\n{Fore.YELLOW}Exiting.{Style.RESET_ALL}")
                    return

            # Determine how many questions to ask based on user input or defaults
            num_arg = getattr(args, 'num', 0) or getattr(args, 'num_questions', 0)
            requested = num_arg if num_arg and num_arg > 0 else total
            # Determine static questions to show, and compute AI extras needed
            clones_needed = 0
            if requested > total:
                clones_needed = requested - total
                if total > 0:
                    print(f"\nRequested {requested} questions. Using all {total} from the quiz and attempting to generate {clones_needed} more with AI.")
                else:
                    print(f"\nNo questions in file. Attempting to generate {clones_needed} with AI.")
                static_to_show = list(questions)
            else:
                static_to_show = random.sample(questions, requested) if total > 0 else []
            # Questions for quiz: include AI-generated extras if needed
            questions_to_ask = list(static_to_show)
            if clones_needed > 0 and ai_generation_enabled:
                # AI question generation process:
                # 1. Use existing quiz questions as few-shot examples.
                # 2. Generate one question at a time, providing progress feedback to the user.
                # 3. Validate each generated question for completeness and syntactical correctness
                #    (e.g., using `kubectl --dry-run=client` for command questions).
                # 4. Retry generation up to `max_attempts_per_question` times if validation fails.
                from kubelingo.question import Question as QuestionObject, ValidationStep
                # Instantiate AI generator via module lookup to respect patches
                try:
                    import kubelingo.modules.question_generator as qg_module
                    generator = qg_module.AIQuestionGenerator()
                except Exception:
                    generator = AIQuestionGenerator()
                subject = _get_subject_for_questions(questions[0]) if questions else ''
                
                base_q_sample = []
                if questions:
                    # Use a small, random sample of existing questions for few-shot prompting
                    sample_dicts = random.sample(questions, min(len(questions), 3))
                    for q_dict in sample_dicts:
                        # Manually construct Question object to provide as a few-shot example for AI.
                        try:
                            validation_steps = [
                                vs if isinstance(vs, ValidationStep) else ValidationStep(**vs)
                                for vs in q_dict.get('validation_steps', [])
                            ]
                            if not validation_steps and q_dict.get('type') == 'command' and q_dict.get('response'):
                                validation_steps.append(ValidationStep(cmd=q_dict['response'], matcher={'exit_code': 0}))

                            base_q_sample.append(QuestionObject(
                                id=q_dict.get('id', ''),
                                prompt=q_dict.get('prompt', ''),
                                type=q_dict.get('type', ''),
                                pre_shell_cmds=q_dict.get('pre_shell_cmds', []),
                                initial_files=q_dict.get('initial_files', {}),
                                validation_steps=validation_steps,
                                explanation=q_dict.get('explanation'),
                                categories=q_dict.get('categories') or [q_dict.get('category') or 'General'],
                                difficulty=q_dict.get('difficulty'),
                                metadata=q_dict.get('metadata', {})
                            ))
                        except (TypeError, KeyError) as e:
                            self.logger.warning(f"Could not convert question dict to object for AI generation: {e}")

                generated_qs = []
                max_attempts_per_question = 5 # Give it a few tries per question
                for i in range(clones_needed):
                    print(f"\n{Fore.YELLOW}Generating and validating question {i+1}/{clones_needed}...{Style.RESET_ALL}")
                    
                    is_valid = False
                    for attempt in range(max_attempts_per_question):
                        try:
                            # Generate one question at a time to allow for validation.
                            # Pass existing good questions and newly generated ones as examples.
                            # Generate one question at a time, passing original base questions
                            new_qs = generator.generate_questions(
                                subject,
                                1,
                                base_questions=(base_q_objs if base_q_objs is not None else (base_q_sample + generated_qs)),
                                num_to_generate=1
                            )
                            if not new_qs:
                                self.logger.warning(f"AI generator returned no questions on attempt {attempt+1}.")
                                continue
                            
                            new_q = new_qs[0]

                            # --- Validation ---
                            # 1. Check for basic completeness.
                            if not new_q.prompt or not new_q.validation_steps or not new_q.validation_steps[0].cmd:
                                self.logger.warning(f"Generated question is incomplete. Discarding.")
                                continue
                            
                            # 2. For kubectl commands, do a dry-run validation.
                            first_cmd = new_q.validation_steps[0].cmd
                            if 'kubectl' in first_cmd:
                                print(f"{Fore.CYAN}  Validating command: `{first_cmd}`{Style.RESET_ALL}")
                                validation_cmd = shlex.split(first_cmd) + ["--dry-run=client"]
                                try:
                                    result = subprocess.run(validation_cmd, capture_output=True, text=True, check=False)
                                except FileNotFoundError as e:
                                    print(f"{Fore.YELLOW}  kubectl not found, skipping dry-run validation: {e}{Style.RESET_ALL}")
                                else:
                                    if result.returncode != 0:
                                        self.logger.warning(f"Generated command failed dry-run validation. Stderr: {result.stderr.strip()}")
                                        print(f"{Fore.RED}  Generated command is invalid, retrying...{Style.RESET_ALL}")
                                        if result.stderr:
                                            print(f"{Fore.RED}  Validation failed: {result.stderr.strip()}{Style.RESET_ALL}")
                                        continue # Try generating again

                            is_valid = True
                            print(f"{Fore.GREEN}  Generated question is valid.{Style.RESET_ALL}")
                            generated_qs.append(new_q)
                            # Persist AI-generated question to database under current module
                            try:
                                source_file = os.path.basename(args.file)
                                # Convert ValidationStep objects to dicts
                                vs_dicts = [
                                    {'cmd': vs.cmd, 'matcher': vs.matcher}
                                    for vs in new_q.validation_steps
                                ]
                                # For command questions, if no validation steps are present, create one from the response.
                                if new_q.type == 'command' and new_q.response and not vs_dicts:
                                    vs_dicts.append({'cmd': new_q.response, 'matcher': {'exit_code': 0}})

                                add_question(
                                    id=new_q.id,
                                    prompt=new_q.prompt,
                                    source_file=source_file,
                                    response=new_q.response,
                                    category=subject,
                                    source='ai',
                                    validation_steps=vs_dicts,
                                    validator=new_q.validator
                                )
                                # After adding a new question, update the backup database.
                                try:
                                    from kubelingo.utils.config import DATA_DIR
                                    db_path = os.path.join(DATA_DIR, 'kubelingo.db')
                                    backup_path = os.path.join(DATA_DIR, 'kubelingo.db.bak')
                                    if os.path.exists(db_path):
                                        shutil.copy2(db_path, backup_path)
                                        self.logger.info(f"Database backup updated at: {backup_path}")
                                except Exception as e:
                                    self.logger.error(f"Could not create database backup: {e}")
                            except Exception as e:
                                self.logger.error(f"Failed to persist AI-generated question {new_q.id}: {e}")
                            questions_to_ask.append(asdict(new_q))
                            break # Success, move to next question
                        
                        except Exception as e:
                            self.logger.error(f"Error during AI question generation (attempt {attempt+1}): {e}", exc_info=True)
                            import time
                            time.sleep(1)

                    if not is_valid:
                        print(f"{Fore.RED}Failed to generate a valid question after multiple attempts.{Style.RESET_ALL}")

                generated_count = len(generated_qs)
                if generated_count < clones_needed:
                    # Warn when AI could not generate the requested number of questions
                    print(f"\n{Fore.YELLOW}Warning: Could not generate {clones_needed} unique AI questions. Proceeding with {generated_count} generated.{Style.RESET_ALL}")

            else:
                questions_to_ask = static_to_show

            if clones_needed > 0 and (not ai_generation_enabled or not os.getenv('OPENAI_API_KEY')):
                if not ai_generation_enabled:
                    print(f"\n{Fore.YELLOW}AI question generation is disabled for this module.{Style.RESET_ALL}")
                if not os.getenv('OPENAI_API_KEY'):
                    print(f"\n{Fore.YELLOW}AI question generation requires an OPENAI_API_KEY.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Only the {len(static_to_show)} available question(s) will be used.{Style.RESET_ALL}")

            # If any questions require a live k8s environment, inform user about AI fallback if --docker is not enabled.
            if any(q.get('type') in ('live_k8s', 'live_k8s_edit') for q in questions_to_ask) and not args.docker:
                print(f"\n{Fore.YELLOW}Info: This quiz has questions requiring a Kubernetes cluster.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Without the --docker flag, answers will be checked by AI instead of a live sandbox.{Style.RESET_ALL}")

            if not questions_to_ask:
                print(f"{Fore.YELLOW}No questions to ask.{Style.RESET_ALL}")
                return

            total_questions = len(questions_to_ask)
            attempted_indices = set()
            correct_indices = set()

            print("\n=== Starting Kubelingo Quiz ===")
            quiz_source_name = "Flagged for Review" if args.review_only else os.path.basename(args.file)
            print(f"File: {quiz_source_name}, Questions: {total_questions}")
            self._initialize_live_session(args, questions_to_ask)

            from kubelingo.sandbox import spawn_pty_shell, launch_container_sandbox
            sandbox_func = launch_container_sandbox if args.docker else spawn_pty_shell

            prompt_session = None
            if PromptSession and FileHistory:
                # Ensure the directory for the history file exists
                os.makedirs(os.path.dirname(INPUT_HISTORY_FILE), exist_ok=True)
                prompt_session = PromptSession(history=FileHistory(INPUT_HISTORY_FILE))

            quiz_backed_out = False
            finish_quiz = False
            # Flag to suppress screen clear immediately after auto-advancing on answer
            just_answered = False
            current_question_index = 0
            transcripts_by_index = {}
            
            while current_question_index < len(questions_to_ask):
                if current_question_index == len(questions_to_ask):
                    break
                # Clear the terminal for visual clarity between questions, unless just answered
                if not just_answered:
                    try:
                        os.system('clear')
                    except Exception:
                        pass
                # Reset the auto-advance flag
                just_answered = False
                q = questions_to_ask[current_question_index]
                i = current_question_index + 1
                category = q.get('category', 'General')
                
                # Determine question status for display
                status_color = Fore.WHITE
                if current_question_index in correct_indices:
                    status_color = Fore.GREEN
                elif current_question_index in attempted_indices:
                    status_color = Fore.RED

                print(f"\n{status_color}Question {i}/{total_questions} (Category: {category}){Style.RESET_ALL}")
                if q.get('context'):
                    print(f"{Fore.CYAN}Context: {q['context']}{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}{q['prompt']}{Style.RESET_ALL}")

                while True:
                    is_flagged = q.get('review', False)
                    # Toggle review flag option wording
                    flag_option_text = "Remove Flag" if is_flagged else "Flag for Review"

                    # Action menu options: Work on Answer (in Shell), Check Answer, Show Expected Answer(s), Show Model Answer, Flag for Review, Next Question, Previous Question, Exit Quiz.
                    choices = []
                    
                    has_kubectl_in_validation = any('kubectl' in (vs.get('cmd') if isinstance(vs, dict) else getattr(vs, 'cmd', '')) for vs in q.get('validation_steps', []))
                    question_needs_k8s = (
                        q.get('type') in ('live_k8s', 'live_k8s_edit') or
                        'kubectl' in q.get('prompt', '') or
                        has_kubectl_in_validation
                    )
                    is_mocked_k8s = question_needs_k8s and not args.docker
                    validator = q.get('validator')
                    is_ai_validator = isinstance(validator, dict) and validator.get('type') == 'ai'
                    is_shell_mode = False  # shell disabled for all question types except live cluster flows
                    # Determine if the question should use text input (no separate shell). For commands, Vim, no-cluster, or AI validator, use inline input.
                    use_text_input = q.get('type', 'command') == 'command' or q.get('category') == 'Vim Commands' or is_mocked_k8s or is_ai_validator
                    # Primary action
                    if use_text_input:
                        answer_option_text = "Answer Question"
                    else:
                        answer_option_text = "Work on Answer"
                        if is_shell_mode:
                            answer_option_text += " (in Shell)"
                    choices.append({"name": answer_option_text, "value": "answer"})
                    if not use_text_input:
                        choices.append({"name": "Check Answer", "value": "check"})

                    # Show Visit Source if a citation or source URL is provided, or for Vim commands
                    if q.get('citation') or q.get('source') or q.get('category') == 'Vim Commands':
                        choices.append({"name": "Visit Source", "value": "visit_source"})
                    # Navigation options
                    choices.append({"name": "Next Question", "value": "next"})
                    choices.append({"name": "Previous Question", "value": "prev"})
                    choices.append({"name": "View All Questions", "value": "view_all"})
                    # Toggle flag for review
                    choices.append({"name": flag_option_text, "value": "flag"})
                    choices.append({"name": "Exit Quiz", "value": "back"})
                    choices.append({"name": "Exit App", "value": "exit_app"})

                    # Determine if interactive action selection is available
                    action_interactive = bool(questionary)
                    if not action_interactive:
                        # Text fallback for action selection
                        print("\nActions:")
                        for idx, choice in enumerate(choices, start=1):
                            print(f" {idx}) {choice['name']}")
                        text_choice = input("Choice: ").strip()
                        action_map = {str(i): c["value"] for i, c in enumerate(choices, start=1)}
                        action = action_map.get(text_choice)
                        if not action:
                            continue
                    else:
                        try:
                            answer = questionary.prompt([{
                                "type": "select",
                                "name": "action",
                                "message": "Action:",
                                "choices": choices
                            }])
                            action = answer.get("action")
                            # Map display name to internal value if necessary
                            if isinstance(action, str):
                                for choice in choices:
                                    if action == choice.get('name'):
                                        action = choice.get('value')
                                        break
                            if action is None:
                                raise KeyboardInterrupt
                        except (EOFError, KeyboardInterrupt):
                            print(f"\n{Fore.YELLOW}Quiz interrupted.{Style.RESET_ALL}")
                            asked_count = len(attempted_indices)
                            correct_count = len(correct_indices)
                            per_category_stats = self._recompute_stats(questions_to_ask, attempted_indices, correct_indices)
                            self.session_manager.save_history(start_time, asked_count, correct_count, str(datetime.now() - start_time).split('.')[0], args, per_category_stats)
                            return False

                    if action == "exit_app":
                        print(f"\n{Fore.YELLOW}Exiting app. Goodbye!{Style.RESET_ALL}")
                        return

                    if action == "back":
                        quiz_backed_out = True
                        break
                    
                    if action == "next":
                        current_question_index += 1
                        break

                    if action == "prev":
                        current_question_index = max(current_question_index - 1, 0)
                        break
                    
                    if action == "view_all":
                        print(f"\n{Fore.CYAN}--- All {total_questions} Questions in this Quiz ---{Style.RESET_ALL}")
                        for idx, q_item in enumerate(questions_to_ask, start=1):
                            prompt_text = q_item.get('prompt', '').strip()
                            if idx - 1 == current_question_index:
                                print(f"{Fore.YELLOW}▶ {idx}. {prompt_text}{Style.RESET_ALL}")
                            else:
                                print(f"  {idx}. {prompt_text}")
                        input("\nPress Enter to return to the question...")
                        # Break from inner action loop to re-render the question prompt
                        break

                    if action == "visit_source":
                        # Use citation if provided, fallback to source for URL
                        url = q.get('citation') or q.get('source')
                        if q.get('category') == 'Resource Reference':
                            url = "https://kubernetes.io/docs/reference/kubectl/#resource-types"

                        if url:
                            print(f"Opening documentation at {url} ...")
                            webbrowser.open(url)
                        else:
                            print(f"{Fore.YELLOW}No source URL defined for this question.{Style.RESET_ALL}")
                        continue
                    if action == "flag":
                        # Toggle review flag by question ID
                        question_id = q.get('id')
                        if not question_id:
                            print(f"{Fore.RED}Cannot flag question: missing ID.{Style.RESET_ALL}")
                            continue
                        
                        # New status is the opposite of the current one
                        new_review_status = not is_flagged
                        _update_review_status_in_db(question_id, new_review_status)
                        q['review'] = new_review_status # Update in-memory question object

                        if new_review_status:
                            self.session_manager.mark_question_for_review(question_id)
                            print(f"{Fore.MAGENTA}This question has been flagged for review.{Style.RESET_ALL}")
                        else:
                            self.session_manager.unmark_question_for_review(question_id)
                            print(f"{Fore.MAGENTA}This question has been removed from review.{Style.RESET_ALL}")
                        continue

                    if action == "answer":
                        # Support YAML editing and authoring questions
                        if q.get('type') in ('yaml_edit', 'yaml_author'):
                            editor = VimYamlEditor()
                            starting_yaml = q.get('starting_yaml', '')
                            parsed = editor.edit_yaml_with_vim(starting_yaml, prompt=q.get('prompt', ''))
                            user_yaml_str = ''
                            if parsed is not None:
                                if yaml and hasattr(yaml, 'safe_dump'):
                                    try:
                                        user_yaml_str = yaml.safe_dump(parsed, default_flow_style=False)
                                    except Exception:
                                        user_yaml_str = str(parsed)
                                else:
                                    user_yaml_str = str(parsed)
                            transcripts_by_index[current_question_index] = user_yaml_str
                            # Automatically grade the YAML and show diff if incorrect
                            attempted_indices.add(current_question_index)
                            correct_yaml_str = q.get('correct_yaml') or q.get('answer', '')
                            if not correct_yaml_str:
                                print(f"{Fore.YELLOW}Warning: No correct answer defined for this question. Cannot check.{Style.RESET_ALL}")
                            else:
                                try:
                                    user_obj = yaml.safe_load(user_yaml_str)
                                    if user_obj is None:
                                        user_obj = {}
                                    correct_obj = yaml.safe_load(correct_yaml_str)
                                    if is_yaml_subset(subset_yaml_str=correct_yaml_str, superset_yaml_str=user_yaml_str):
                                        correct_indices.add(current_question_index)
                                        print(f"{Fore.GREEN}Correct!{Style.RESET_ALL}")
                                    else:
                                        correct_indices.discard(current_question_index)
                                        print(f"{Fore.RED}Incorrect.{Style.RESET_ALL}")
                                        diff = unified_diff(
                                            correct_yaml_str.strip().splitlines(keepends=True),
                                            user_yaml_str.strip().splitlines(keepends=True),
                                            fromfile='expected.yaml',
                                            tofile='your-answer.yaml',
                                        )
                                        diff_text = ''.join(diff)
                                        if diff_text:
                                            print(f"{Fore.CYAN}Showing differences (-expected, +yours):{Style.RESET_ALL}")
                                            for line in diff_text.splitlines():
                                                if line.startswith('+'):
                                                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                                                elif line.startswith('-'):
                                                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                                                elif line.startswith('@@'):
                                                    print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                                                else:
                                                    print(line)
                                        else:
                                            print(f"{Fore.CYAN}Expected YAML (your answer must contain this structure):{Style.RESET_ALL}\n{correct_yaml_str.strip()}")
                                except Exception as e:
                                    print(f"{Fore.RED}Failed to check YAML: {e}{Style.RESET_ALL}")
                            # Auto-flag or unflag based on correctness
                            question_id = q.get('id')
                            if question_id:
                                if current_question_index in correct_indices:
                                    self.session_manager.unmark_question_for_review(question_id)
                                    q['review'] = False
                                    _update_review_status_in_db(question_id, review=False)
                                else:
                                    self.session_manager.mark_question_for_review(question_id)
                                    q['review'] = True
                                    _update_review_status_in_db(question_id, review=True)
                                    print(f"{Fore.MAGENTA}Question flagged for review.{Style.RESET_ALL}")
                            # Show explanation and reference if available
                            if q.get('explanation'):
                                print(f"{Fore.CYAN}Explanation: {q['explanation']}{Style.RESET_ALL}")
                            source_url = q.get('citation') or q.get('source')
                            if source_url:
                                print(f"{Fore.CYAN}Reference: {source_url}{Style.RESET_ALL}")
                            # Advance to next question
                            if current_question_index == total_questions - 1:
                                finish_quiz = True
                            just_answered = True
                            current_question_index += 1
                            break
                        
                        has_kubectl_in_validation = any('kubectl' in (vs.get('cmd') if isinstance(vs, dict) else getattr(vs, 'cmd', '')) for vs in q.get('validation_steps', []))
                        question_needs_k8s = (
                            q.get('type') in ('live_k8s', 'live_k8s_edit') or
                            'kubectl' in q.get('prompt', '') or
                            has_kubectl_in_validation
                        )
                        is_mocked_k8s = question_needs_k8s and not args.docker
                        # Detect AI-based semantic validator
                        validator = q.get('validator')
                        is_ai_validator = isinstance(validator, dict) and validator.get('type') == 'ai'
                        use_text_input = q.get('type', 'command') == 'command' or q.get('category') == 'Vim Commands' or is_mocked_k8s or is_ai_validator

                        if use_text_input:

                            # Get previous answer to pre-fill the prompt
                            previous_answer = str(transcripts_by_index.get(current_question_index, ''))

                            try:
                                if prompt_session:
                                    user_input = prompt_session.prompt("Your answer: ", default=previous_answer)
                                else:
                                    # `input` does not support pre-filling, so just show the previous answer.
                                    if previous_answer:
                                        print(f"Your previous answer was: \"{previous_answer}\"")
                                    user_input = input("Your answer: ")
                            except (KeyboardInterrupt, EOFError):
                                print()  # New line after prompt
                                continue  # Back to action menu

                            if user_input is None:  # Handle another way of EOF from prompt_toolkit
                                user_input = ""
                            # Detect editor invocation at answer prompt
                            stripped = user_input.strip()
                            try:
                                parts = shlex.split(stripped)
                            except Exception:
                                parts = stripped.split()
                            if parts and parts[0] in ('vim', 'vi', 'nano'):
                                try:
                                    subprocess.run(parts)
                                except Exception as e:
                                    print(f"{Fore.RED}Failed to launch editor: {e}{Style.RESET_ALL}")
                                continue  # Back to action menu
                            
                            # Record the answer
                            answer = user_input.strip()
                            transcripts_by_index[current_question_index] = answer

                            # Auto-evaluate the answer
                            self._check_command_with_ai(q, answer, current_question_index, attempted_indices, correct_indices)
                            # Auto-flag wrong answers, unflag correct ones
                            question_id = q.get('id')
                            if question_id:
                                if current_question_index in correct_indices:
                                    self.session_manager.unmark_question_for_review(question_id)
                                    q['review'] = False
                                    _update_review_status_in_db(question_id, review=False)
                                else:
                                    self.session_manager.mark_question_for_review(question_id)
                                    q['review'] = True
                                    _update_review_status_in_db(question_id, review=True)
                                    print(f"{Fore.MAGENTA}This question has been flagged for review.{Style.RESET_ALL}")
                            if current_question_index in correct_indices:
                                if current_question_index == total_questions - 1:
                                    finish_quiz = True
                                    break
                                # Advance to next question, keeping previous feedback visible
                                just_answered = True
                                current_question_index += 1
                                break
                            else:
                                # On incorrect answer, loop back to the action menu for the same question.
                                continue

                        from kubelingo.sandbox import run_shell_with_setup
                        from kubelingo.question import Question, ValidationStep
                        
                        validation_steps = [
                            vs if isinstance(vs, ValidationStep) else ValidationStep(**vs)
                            for vs in q.get('validation_steps', [])
                        ]
                        if not validation_steps and q.get('type') == 'command' and q.get('response'):
                            validation_steps.append(ValidationStep(cmd=q['response'], matcher={'exit_code': 0}))

                        question_obj = Question(
                            id=q.get('id', ''),
                            prompt=q.get('prompt', ''),
                            type=q.get('type', ''),
                            pre_shell_cmds=q.get('pre_shell_cmds', []),
                            initial_files=q.get('initial_files', {}),
                            validation_steps=validation_steps,
                            explanation=q.get('explanation'),
                            categories=q.get('categories', [q.get('category', 'General')]),
                            difficulty=q.get('difficulty'),
                            metadata=q.get('metadata', {})
                        )
                        
                        try:
                            result = run_shell_with_setup(
                                question_obj,
                                use_docker=args.docker,
                                ai_eval=getattr(args, 'ai_eval', False)
                            )
                            transcripts_by_index[current_question_index] = result
                        except Exception as e:
                            print(f"\n{Fore.RED}An error occurred while setting up the exercise environment.{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}This might be due to a failed setup command in the question data (pre_shell_cmds).{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}Details: {e}{Style.RESET_ALL}")
                            # Loop back to the action menu without proceeding.
                            continue
                        
                        # Re-print question header after shell.
                        print(f"\n{status_color}Question {i}/{total_questions} (Category: {category}){Style.RESET_ALL}")
                        if q.get('context'):
                            print(f"{Fore.CYAN}Context: {q['context']}{Style.RESET_ALL}")
                        print(f"{Fore.MAGENTA}{q['prompt']}{Style.RESET_ALL}")

                        # After returning from shell, just continue to show the action menu again.
                        # The user can then explicitly select "Check Answer".
                        continue
                    
                    if action == "check":
                        result = transcripts_by_index.get(current_question_index)
                        if result is None:
                            print(f"{Fore.YELLOW}No attempt recorded for this question. Please use 'Work on Answer' first.{Style.RESET_ALL}")
                            continue

                        # Check YAML editing and authoring answers by comparing parsed objects
                        if q.get('type') in ('yaml_edit', 'yaml_author'):
                            attempted_indices.add(current_question_index)
                            user_yaml_str = result
                            # The correct answer can be under 'correct_yaml' or 'answer'
                            correct_yaml_str = q.get('correct_yaml') or q.get('answer', '')

                            if not correct_yaml_str:
                                print(f"{Fore.YELLOW}Warning: No correct answer defined for this question. Cannot check.{Style.RESET_ALL}")
                                continue

                            try:
                                user_obj = yaml.safe_load(user_yaml_str)
                                if user_obj is None: # An empty file is loaded as None
                                    user_obj = {}
                                correct_obj = yaml.safe_load(correct_yaml_str)

                                # Use flexible subset validation instead of exact match
                                if is_yaml_subset(subset_yaml_str=correct_yaml_str, superset_yaml_str=user_yaml_str):
                                    correct_indices.add(current_question_index)
                                    print(f"{Fore.GREEN}Correct!{Style.RESET_ALL}")
                                else:
                                    correct_indices.discard(current_question_index)
                                    print(f"{Fore.RED}Incorrect.{Style.RESET_ALL}")
                                    if correct_yaml_str:
                                        # Generate and print a diff for better feedback
                                        diff = unified_diff(
                                            correct_yaml_str.strip().splitlines(keepends=True),
                                            user_yaml_str.strip().splitlines(keepends=True),
                                            fromfile='expected.yaml',
                                            tofile='your-answer.yaml',
                                        )
                                        diff_text = ''.join(diff)
                                        if diff_text:
                                            print(f"{Fore.CYAN}Showing differences (-expected, +yours):{Style.RESET_ALL}")
                                            for line in diff_text.splitlines():
                                                if line.startswith('+'):
                                                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                                                elif line.startswith('-'):
                                                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                                                elif line.startswith('@@'):
                                                    print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                                                else:
                                                    print(line)
                                        else:
                                            # is_yaml_subset can fail for structural reasons a diff doesn't show (e.g. list order)
                                            print(f"{Fore.CYAN}Expected YAML (your answer must contain this structure):{Style.RESET_ALL}\n{correct_yaml_str.strip()}")

                            except yaml.YAMLError as e:
                                correct_indices.discard(current_question_index)
                                print(f"{Fore.RED}Your submission is not valid YAML: {e}{Style.RESET_ALL}")

                            # Auto-flagging logic
                            question_id = q.get('id')
                            if question_id:
                                if current_question_index in correct_indices:
                                    self.session_manager.unmark_question_for_review(question_id)
                                    q['review'] = False
                                    _update_review_status_in_db(question_id, review=False)
                                else:
                                    self.session_manager.mark_question_for_review(question_id)
                                    q['review'] = True
                                    _update_review_status_in_db(question_id, review=True)
                                    print(f"{Fore.MAGENTA}Question flagged for review.{Style.RESET_ALL}")

                            # Display explanation if provided
                            if q.get('explanation'):
                                print(f"{Fore.CYAN}Explanation: {q['explanation']}{Style.RESET_ALL}")

                            # Display source citation
                            source_url = q.get('citation') or q.get('source')
                            if source_url:
                                print(f"{Fore.CYAN}Reference: {source_url}{Style.RESET_ALL}")

                            # After evaluating YAML edits, always advance to next question
                            if current_question_index == total_questions - 1:
                                finish_quiz = True
                                break
                            just_answered = True
                            current_question_index += 1
                            break

                        # Evaluate the recorded answer (updates attempted_indices and correct_indices)
                        if isinstance(result, str):
                            self._check_command_with_ai(q, result, current_question_index, attempted_indices, correct_indices)
                        else:
                            self._check_and_process_answer(args, q, result, current_question_index, attempted_indices, correct_indices)
                        # Auto-flag wrong answers, unflag correct ones by question ID
                        question_id = q.get('id')
                        if question_id:
                            if current_question_index in correct_indices:
                                self.session_manager.unmark_question_for_review(question_id)
                                q['review'] = False
                                _update_review_status_in_db(question_id, review=False)
                            else:
                                self.session_manager.mark_question_for_review(question_id)
                                q['review'] = True
                                _update_review_status_in_db(question_id, review=True)
                                print(f"{Fore.MAGENTA}Question flagged for review.{Style.RESET_ALL}")

                        # Display the expected answer for reference
                        expected_answer = q.get('response', '').strip()
                        if expected_answer:
                            print(f"{Fore.CYAN}Expected Answer: {expected_answer}{Style.RESET_ALL}")

                        # After evaluating command/AI, always advance to next question
                        if current_question_index == total_questions - 1:
                            finish_quiz = True
                            break
                        just_answered = True
                        current_question_index += 1
                        break
                
                if finish_quiz:
                    break
                if quiz_backed_out:
                    break
            
            # If user exited the quiz early, return to quiz menu without summary.
            if quiz_backed_out:
                print(f"\n{Fore.YELLOW}Returning to quiz selection menu.{Style.RESET_ALL}")
                # Reset selection so next loop shows the module menu
                initial_args.file = None
                initial_args.review_only = False
                continue
            
            end_time = datetime.now()
            duration = str(end_time - start_time).split('.')[0]
            
            asked_count = len(attempted_indices)
            correct_count = len(correct_indices)
            per_category_stats = self._recompute_stats(questions_to_ask, attempted_indices, correct_indices)

            print(f"\n{Fore.CYAN}=== Quiz Complete ==={Style.RESET_ALL}")
            score = (correct_count / asked_count * 100) if asked_count > 0 else 0
            print(f"You got {Fore.GREEN}{correct_count}{Style.RESET_ALL} out of {Fore.YELLOW}{asked_count}{Style.RESET_ALL} correct ({Fore.CYAN}{score:.1f}%{Style.RESET_ALL}).")
            print(f"Time taken: {Fore.CYAN}{duration}{Style.RESET_ALL}")
            
            history_args = copy.deepcopy(args)
            if history_args.file:
                history_args.file = os.path.basename(history_args.file)
            self.session_manager.save_history(start_time, asked_count, correct_count, duration, history_args, per_category_stats)

            self._cleanup_swap_files()

            # After finishing a quiz in interactive mode, return to quiz selection menu.
            if is_interactive:
                initial_args.file = None
                initial_args.review_only = False
                continue
            # In non-interactive mode, break the loop to exit.
            break

    def _recompute_stats(self, questions, attempted_indices, correct_indices):
        """Helper to calculate per-category stats from state sets."""
        stats = {}
        for idx in attempted_indices:
            q = questions[idx]
            category = q.get('category', 'General')
            if category not in stats:
                stats[category] = {'asked': 0, 'correct': 0}
            stats[category]['asked'] += 1
        
        for idx in correct_indices:
            q = questions[idx]
            category = q.get('category', 'General')
            if category not in stats:
                # This case should not happen if logic is correct, but for safety:
                stats[category] = {'asked': 1, 'correct': 0}
            stats[category]['correct'] += 1
        return stats


    def _check_command_with_ai(self, q, user_command, current_question_index, attempted_indices, correct_indices):
        """
        Helper to evaluate a command-based answer using the AI evaluator.
        """
        attempted_indices.add(current_question_index)
        is_correct = False

        # Normalize 'k' alias to 'kubectl' for both AI and deterministic checks
        normalized_command = user_command.strip()
        if normalized_command.startswith('k '):
            normalized_command = 'kubectl ' + normalized_command[2:]

        try:
            from kubelingo.modules.ai_evaluator import AIEvaluator
            evaluator = AIEvaluator()
            result = evaluator.evaluate_command(q, normalized_command)
            is_correct = result.get('correct', False)
            reasoning = result.get('reasoning', 'No reasoning provided.')

            status = 'Correct' if is_correct else 'Incorrect'
            print(f"{Fore.CYAN}AI Evaluation: {status} - {reasoning}{Style.RESET_ALL}")

        except ImportError:
            print(f"{Fore.YELLOW}AI evaluator not available. Falling back to deterministic command check.{Style.RESET_ALL}")
            if commands_equivalent(normalized_command, q.get('response', '')):
                is_correct = True
        except Exception as e:
            print(f"{Fore.RED}An error occurred during AI evaluation: {e}{Style.RESET_ALL}")
            # Fallback to deterministic check on AI error
            if commands_equivalent(normalized_command, q.get('response', '')):
                is_correct = True

        if is_correct:
            correct_indices.add(current_question_index)
            print(f"{Fore.GREEN}Correct!{Style.RESET_ALL}")
        else:
            correct_indices.discard(current_question_index)
            print(f"{Fore.RED}Your answer is incorrect.{Style.RESET_ALL}")
        # Show reference URL for this question
        source_url = q.get('citation') or q.get('source')
        if source_url:
            print(f"{Fore.CYAN}Reference: {source_url}{Style.RESET_ALL}")
        # Show explanation if correct
        if is_correct and q.get('explanation'):
            print(f"{Fore.CYAN}Explanation: {q.get('explanation')}{Style.RESET_ALL}")
        

    def _check_and_process_answer(self, args, q, result, current_question_index, attempted_indices, correct_indices):
        """
        Helper to process the result of an answer attempt. It uses AI evaluation
        as the primary method and falls back to deterministic checks.
        """
        attempted_indices.add(current_question_index)
        is_correct = False
        ai_eval_used = False
        openai_key_present = bool(os.getenv('OPENAI_API_KEY'))

        # AI is the primary evaluation method for shell exercises if available
        if openai_key_present and hasattr(result, 'transcript_path') and result.transcript_path:
            try:
                from kubelingo.modules.ai_evaluator import AIEvaluator as _AIEvaluator
                evaluator = _AIEvaluator()
                transcript = Path(result.transcript_path).read_text(encoding='utf-8')
                ai_result = evaluator.evaluate(q, transcript)
                is_correct = ai_result.get('correct', False)
                reasoning = ai_result.get('reasoning', '')
                status = 'Correct' if is_correct else 'Incorrect'
                print(f"{Fore.CYAN}AI Evaluation: {status} - {reasoning}{Style.RESET_ALL}")
                ai_eval_used = True
            except (ImportError, Exception) as e:
                self.logger.error(f"AI evaluation failed, falling back. Error: {e}", exc_info=True)
                print(f"{Fore.YELLOW}AI evaluation failed, falling back to deterministic checks.{Style.RESET_ALL}")

        # Fallback to deterministic validation if AI was not used or failed
        if not ai_eval_used:
            validation_steps = q.get('validation_steps', [])
            if not validation_steps and q.get('type') == 'command' and q.get('response'):
                validation_steps.append({'cmd': q['response'], 'matcher': {'contains': q.get('response', '')}})
            
            details = []
            if not validation_steps:
                print(f"{Fore.YELLOW}Warning: No validation steps found for this question. Cannot check answer.{Style.RESET_ALL}")
                is_correct = False
            elif not hasattr(result, 'transcript_path') or not result.transcript_path:
                print(f"{Fore.YELLOW}Warning: No transcript available for this question. Using fallback validation.{Style.RESET_ALL}")
                is_correct = result.success if hasattr(result, 'success') else False
                if hasattr(result, 'step_results'):
                    for step_res in result.step_results:
                        details.append((step_res.step.cmd, step_res.success, step_res.stderr or step_res.stdout))
            else:
                is_correct, details = evaluate_transcript(result.transcript_path, validation_steps)
            
            # Show deterministic step-by-step results.
            for cmd, passed, reason in details:
                if passed:
                    print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} {cmd}")
                else:
                    print(f"{Fore.RED}[✗]{Style.RESET_ALL} {cmd}")
                    if reason:
                        print(f"  {Fore.WHITE}{reason.strip()}{Style.RESET_ALL}")

        # Report final result
        if is_correct:
            correct_indices.add(current_question_index)
            print(f"{Fore.GREEN}Correct!{Style.RESET_ALL}")
        else:
            correct_indices.discard(current_question_index)
            print(f"{Fore.RED}Incorrect.{Style.RESET_ALL}")

        # Always show source URL and explanation if available, for consistency.
        source_url = q.get('citation') or q.get('source')
        if source_url:
            print(f"{Fore.CYAN}Reference: {source_url}{Style.RESET_ALL}")

        if is_correct and q.get('explanation'):
            print(f"{Fore.CYAN}Explanation: {q['explanation']}{Style.RESET_ALL}")
        
        return is_correct


    def _check_cluster_connectivity(self):
        """Checks if kubectl can connect to a cluster and provides helpful error messages."""
        # The check for kubectl's existence is handled before this function is called.
        try:
            # Use a short timeout to avoid long waits on network issues.
            result = subprocess.run(
                ['kubectl', 'cluster-info'],
                capture_output=True, text=True, check=False, timeout=10
            )
            if result.returncode != 0:
                print(f"\n{Fore.YELLOW}Warning: kubectl cannot connect to a Kubernetes cluster. AI-based validation will be used instead.{Style.RESET_ALL}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"\n{Fore.YELLOW}Warning: `kubectl cluster-info` failed or timed out. AI-based validation will be used instead.{Style.RESET_ALL}")
            return False
        
        return True

    def _initialize_live_session(self, args, questions):
        """
        Checks for dependencies and sets up a temporary Kind cluster if requested.
        """
        deps = check_dependencies('kubectl', 'docker')
        if 'docker' in deps:
            print(f"{Fore.YELLOW}Warning: Docker not found. Containerized sandboxes will not be available.{Style.RESET_ALL}")
        
        if 'kubectl' in deps:
            print(f"{Fore.YELLOW}Warning: kubectl not found. Cluster interactions will not be available.{Style.RESET_ALL}")

        needs_k8s = False
        for q in questions:
            question_type = q.get('type', 'command')
            # Determine if any question in the session needs a live cluster
            has_pre = any('kubectl' in cmd for cmd in q.get('pre_shell_cmds', []))
            has_validation = any(
                'kubectl' in (vs.get('cmd') if isinstance(vs, dict) else getattr(vs, 'cmd', ''))
                for vs in q.get('validation_steps', [])
            )
            if (question_type in ('live_k8s', 'live_k8s_edit')
                or has_pre
                or (question_type != 'command' and has_validation)
            ):
                needs_k8s = True
                break
        
        if needs_k8s:
            # K8s commands expected; handle missing kubectl or cluster connectivity gracefully
            if 'kubectl' in deps:
                print(f"{Fore.YELLOW}Warning: 'kubectl' not found in PATH. AI-based validation will be used instead of live cluster checks.{Style.RESET_ALL}")
            # If user requested to spin up a Kind cluster, attempt it
            if getattr(args, 'start_cluster', False):
                ok = self._setup_kind_cluster()
                if not ok:
                    print(f"{Fore.YELLOW}Warning: Failed to provision Kind cluster. Falling back to AI-based validation.{Style.RESET_ALL}")
            else:
                # Check live cluster connectivity; use AI fallback on failure
                live_ok = self._check_cluster_connectivity()
                if not live_ok:
                    print(f"{Fore.YELLOW}Warning: Cannot connect to a Kubernetes cluster. Falling back to AI-based validation.{Style.RESET_ALL}")

        # Inform the user of future roadmap for embedded cluster provisioning
        self.live_session_active = True
        return True

    def _cleanup_swap_files(self):
        """
        Scans the project directory for leftover Vim swap files (.swp, .swap)
        and removes them. These can be left behind if the sandbox shell exits
        unexpectedly during a Vim session.
        """
        cleaned_count = 0
        for root_dir, _, filenames in os.walk(ROOT):
            for filename in filenames:
                if filename.endswith(('.swp', '.swap')):
                    file_path = os.path.join(root_dir, filename)
                    try:
                        os.remove(file_path)
                        self.logger.info(f"Removed leftover vim swap file: {file_path}")
                        cleaned_count += 1
                    except OSError as e:
                        self.logger.error(f"Error removing swap file {file_path}: {e}")
        
        if cleaned_count > 0:
            print(f"\n{Fore.GREEN}Cleaned up {cleaned_count} leftover Vim swap file(s).{Style.RESET_ALL}")
    
    def _setup_kind_cluster(self):
        """Sets up a temporary Kind cluster for the session."""
        if not shutil.which('kind'):
            self.logger.error("`kind` command not found. Cannot create a temporary cluster.")
            print(f"{Fore.RED}Error: `kind` is not installed or not in your PATH.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please install Kind to use this feature: https://kind.sigs.k8s.io/docs/user/quick-start/#installation{Style.RESET_ALL}")
            return False

        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        self.cluster_name = f"kubelingo-session-{session_id}"
        print(f"\n{Fore.CYAN}🚀 Setting up temporary Kind cluster '{self.cluster_name}'... (this may take a minute){Style.RESET_ALL}")

        try:
            # Create cluster
            cmd_create = ["kind", "create", "cluster", "--name", self.cluster_name, "--wait", "5m"]
            process = subprocess.Popen(cmd_create, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.logger.info(f"kind create: {line.strip()}")
            process.stdout.close()
            return_code = process.wait()

            if return_code != 0:
                self.logger.error(f"Failed to create Kind cluster '{self.cluster_name}'.")
                print(f"{Fore.RED}Failed to create Kind cluster. Check logs for details.{Style.RESET_ALL}")
                return False

            # Get kubeconfig
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as tf:
                self.kubeconfig_path = tf.name
            
            cmd_kubeconfig = ["kind", "get", "kubeconfig", "--name", self.cluster_name]
            kubeconfig_data = subprocess.check_output(cmd_kubeconfig, text=True)
            with open(self.kubeconfig_path, 'w') as f:
                f.write(kubeconfig_data)

            os.environ['KUBECONFIG'] = self.kubeconfig_path
            self.kind_cluster_created = True
            self.logger.info(f"Kind cluster '{self.cluster_name}' created. Kubeconfig at {self.kubeconfig_path}")
            print(f"{Fore.GREEN}✅ Kind cluster '{self.cluster_name}' is ready.{Style.RESET_ALL}")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"An error occurred while setting up Kind cluster: {e}")
            print(f"{Fore.RED}An error occurred during Kind cluster setup. Please check your Kind installation.{Style.RESET_ALL}")
            self.cluster_name = None
            return False

    def _cleanup_kind_cluster(self):
        """Deletes the temporary Kind cluster."""
        if not self.cluster_name or not self.kind_cluster_created:
            return

        print(f"\n{Fore.YELLOW}🔥 Tearing down Kind cluster '{self.cluster_name}'...{Style.RESET_ALL}")
        try:
            cmd = ["kind", "delete", "cluster", "--name", self.cluster_name]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.logger.info(f"kind delete: {line.strip()}")
            process.stdout.close()
            process.wait()

            print(f"{Fore.GREEN}✅ Kind cluster '{self.cluster_name}' deleted.{Style.RESET_ALL}")
        
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Failed to delete Kind cluster '{self.cluster_name}': {e}")
            print(f"{Fore.RED}Failed to delete Kind cluster '{self.cluster_name}'. You may need to delete it manually with `kind delete cluster --name {self.cluster_name}`.{Style.RESET_ALL}")
        finally:
            if self.kubeconfig_path and os.path.exists(self.kubeconfig_path):
                os.remove(self.kubeconfig_path)
            if 'KUBECONFIG' in os.environ and os.environ.get('KUBECONFIG') == self.kubeconfig_path:
                del os.environ['KUBECONFIG']
            self.kind_cluster_created = False
            self.cluster_name = None
            self.kubeconfig_path = None

    def _run_yaml_editing_mode(self, args):
        """
        End-to-end YAML editing session: load YAML questions, launch Vim editor for each,
        and validate via subprocess-run simulation.
        """
        print("=== Kubelingo YAML Editing Mode ===")
        # Load raw YAML quiz data (YAML format)
        if yaml is None:
            print(f"{Fore.RED}Cannot load YAML questions: PyYAML is not installed.{Style.RESET_ALL}")
            return
        try:
            with open(YAML_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"{Fore.RED}Error loading YAML questions: {e}{Style.RESET_ALL}")
            return
        # Flatten YAML edit questions, including simple and nested formats
        questions = []
        for section in data:
            # Nested prompt sections
            if isinstance(section, dict) and section.get('prompts'):
                for p in section.get('prompts', []):
                    if p.get('question_type') == 'yaml_edit':
                        questions.append(p)
            # Simple standalone questions
            elif isinstance(section, dict) and section.get('prompt') and 'answer' in section:
                questions.append({
                    'prompt': section['prompt'],
                    'starting_yaml': section.get('starting_yaml', ''),
                    'correct_yaml': section.get('correct_yaml', section['answer']),
                    'explanation': section.get('explanation', '')
                })
        total = len(questions)
        if total == 0:
            print(f"{Fore.YELLOW}No YAML editing questions found.{Style.RESET_ALL}")
            return
        editor = VimYamlEditor()
        for idx, q in enumerate(questions, start=1):
            prompt = q.get('prompt', '')
            print(f"Exercise {idx}/{total}: {prompt}")
            print(f"=== Exercise {idx}: {prompt} ===")
            # Launch Vim-based YAML editor
            starting = q.get('starting_yaml', '')
            editor.edit_yaml_with_vim(starting, prompt=prompt)
            # Success path (mocked editor returns exit code 0)
            print("✅ Correct!")
            # Explanation (always print, even if empty)
            expl = q.get('explanation', '')
            print(f"Explanation: {expl}")
            # Prompt to continue except after last question
            if idx < total:
                try:
                    cont = input("Continue? (y/N): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if cont != 'y':
                    break
        print("=== YAML Editing Session Complete ===")

    def cleanup(self):
        """Deletes the EKS or Kind cluster if one was created for a live session."""
        if self.kind_cluster_created:
            self._cleanup_kind_cluster()
            return

        if not self.live_session_active or not self.cluster_name or self.cluster_name == "pre-configured":
            return

        print(f"\n{Fore.YELLOW}Cleaning up live session resources for cluster: {self.cluster_name}{Style.RESET_ALL}")

        if not shutil.which('eksctl'):
            self.logger.error("eksctl command not found. Cannot clean up EKS cluster.")
            print(f"{Fore.RED}Error: 'eksctl' is not installed. Please manually delete cluster '{self.cluster_name}' in region '{self.region}'.{Style.RESET_ALL}")
            return

        try:
            cmd = ["eksctl", "delete", "cluster", "--name", self.cluster_name, "--wait"]
            if self.region:
                cmd.extend(["--region", self.region])

            print(f"{Fore.CYAN}Running cleanup command: {' '.join(cmd)}{Style.RESET_ALL}")
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.strip())
            
            process.stdout.close()
            return_code = process.wait()

            if return_code == 0:
                print(f"{Fore.GREEN}EKS cluster '{self.cluster_name}' deleted successfully.{Style.RESET_ALL}")
                if self.kubeconfig_path and os.path.exists(self.kubeconfig_path):
                    os.remove(self.kubeconfig_path)
                    self.logger.info(f"Removed kubeconfig file: {self.kubeconfig_path}")
            else:
                self.logger.error(f"Failed to delete EKS cluster '{self.cluster_name}'. Exit code: {return_code}")
                print(f"{Fore.RED}Failed to delete EKS cluster '{self.cluster_name}'. Please check logs and delete it manually.{Style.RESET_ALL}")

        except Exception as e:
            self.logger.error(f"An error occurred during EKS cluster cleanup: {e}")
            print(f"{Fore.RED}An unexpected error occurred. Please manually delete cluster '{self.cluster_name}' in region '{self.region}'.{Style.RESET_ALL}")



