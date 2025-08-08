import os
import re
try:
    import yaml
except ImportError:
    yaml = None

from kubelingo.utils.config import LOGS_DIR

# Directory to store per-question transcripts
TRANSCRIPTS_DIR = os.path.join(LOGS_DIR, 'transcripts')

def _ensure_dir():
    """Ensure base transcripts directory (with optional session subdir) exists."""
    session_id = os.getenv('KUBELINGO_SESSION_ID') or ''
    base = TRANSCRIPTS_DIR
    if session_id:
        base = os.path.join(TRANSCRIPTS_DIR, session_id)
    try:
        os.makedirs(base, exist_ok=True)
    except Exception:
        pass
    return base

def _sanitize_qid(qid: str) -> str:
    # Replace characters unsafe for filenames
    name = qid.replace('::', '__')
    # Remove any remaining non-alphanumeric or underscore
    return re.sub(r'[^A-Za-z0-9_\-\.]+', '_', name)

def save_transcript(qid: str, content: str) -> str:
    """
    Save the full transcript for a question to persistent storage.
    """
    """
    Save the full transcript for a question and return its file path.
    Transcripts are stored under logs/transcripts/<session_id>/<qid>.log
    """
    base = _ensure_dir()
    fname = _sanitize_qid(qid) + '.log'
    path = os.path.join(base, fname)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    except Exception:
        return ''

def load_transcript(qid: str) -> str:
    """
    Load transcript content for a given question id, or return empty string if not found.
    """
    session_id = os.getenv('KUBELINGO_SESSION_ID') or ''
    base = TRANSCRIPTS_DIR
    if session_id:
        base = os.path.join(TRANSCRIPTS_DIR, session_id)
    fname = _sanitize_qid(qid) + '.log'
    path = os.path.join(base, fname)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ''
    return ''

def _is_yaml_subset(subset_yaml_str: str, superset_yaml_str: str) -> bool:
    """
    Checks if one YAML object is a structural subset of another.
    It parses both YAML strings and recursively compares them.
    - All keys and values in subset must exist in superset.
    - Lists are handled specially: each item in subset list must find a matching
      item in superset list. For list of dicts, matching is done by checking if
      an item in superset is a superset of an item in subset.
    - It ignores extra keys in superset.
    """
    try:
        subset = yaml.safe_load(subset_yaml_str)
        superset = yaml.safe_load(superset_yaml_str)
    except yaml.YAMLError:
        return False

    if subset is None:
        return True

    if superset is None:
        return False

    def _compare(sub, super_):
        if isinstance(sub, dict):
            if not isinstance(super_, dict): return False
            for k, v in sub.items():
                if k not in super_ or not _compare(v, super_[k]):
                    return False
            return True
        elif isinstance(sub, list):
            if not isinstance(super_, list): return False
            
            super_copy = list(super_)
            for sub_item in sub:
                found_match = False
                for i, super_item in enumerate(super_copy):
                    if _compare(sub_item, super_item):
                        super_copy.pop(i)
                        found_match = True
                        break
                if not found_match:
                    return False
            return True
        else:
            return str(sub) == str(super_)

    return _compare(subset, superset)


def evaluate_transcript(transcript_path: str, validation_steps) -> (bool, list):
    """
    Evaluate a transcript file against a list of validation steps.
    Each step can be a dict or ValidationStep with cmd and matcher.
    Returns (all_pass, details_list).
    """
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        # Support common alias 'k' for 'kubectl' in user inputs: expand at line starts
        try:
            import re as _re
            transcript = _re.sub(r'(?m)^(\s*)k ', r'\1kubectl ', transcript)
        except Exception:
            pass
    except Exception:
        return False, [f"Unable to read transcript: {transcript_path}"]
    all_pass = True
    details = []
    for vs in validation_steps:
        if hasattr(vs, 'cmd') and hasattr(vs, 'matcher'):
            cmd, matcher = vs.cmd, vs.matcher
        else:
            cmd, matcher = vs.get('cmd', ''), vs.get('matcher', {})
        passed = False
        reason = ''
        if 'contains' in matcher:
            if matcher['contains'] in transcript:
                passed = True
            else:
                reason = f"Missing text: {matcher['contains']}"
        elif 'regex' in matcher:
            try:
                if re.search(matcher['regex'], transcript, re.MULTILINE):
                    passed = True
                else:
                    reason = f"Regex not matched: {matcher['regex']}"
            except re.error:
                reason = f"Invalid regex: {matcher.get('regex')}"
        else:
            if cmd and cmd in transcript:
                passed = True
            else:
                reason = f"Missing command: {cmd}"
        details.append((cmd, passed, reason))
        if not passed:
            all_pass = False
    return all_pass, details

def check_answer(q: dict) -> (bool, list):
    """
    Check a question's answer by inspecting its saved transcript.
    Returns (is_correct, details) where details is a list of strings.
    """
    transcript = load_transcript(q.get('id', ''))
    if not transcript:
        return False, ['No transcript found. Please start the exercise to generate a transcript.']
    # Build validation steps
    steps = []
    # Legacy: q may have 'validations' or 'validation_steps'
    raw_steps = q.get('validation_steps') or q.get('validations') or []
    # For command-type questions lacking explicit validations, match the expected response
    if not raw_steps and q.get('type') == 'command' and q.get('response'):
        raw_steps = [{'cmd': q.get('response', ''), 'matcher': {'contains': q.get('response', '')}}]
    for item in raw_steps:
        # item could be ValidationStep or dict
        if hasattr(item, 'cmd') and hasattr(item, 'matcher'):
            cmd = item.cmd
            matcher = item.matcher
        else:
            cmd = item.get('cmd', '')
            matcher = item.get('matcher', {})
        steps.append((cmd, matcher))
    # Evaluate each step
    all_pass = True
    details = []
    for cmd, matcher in steps:
        passed = False
        reason = ''
        # Default: substring match of cmd
        if 'contains' in matcher:
            expected_text = matcher['contains']
            # Heuristic to detect if we should do a flexible YAML check.
            # This is for YAML manifest questions where we want to check for a
            # structural subset, not exact string match.
            is_k8s_yaml = 'apiVersion:' in expected_text and 'kind:' in expected_text

            if is_k8s_yaml:
                if _is_yaml_subset(expected_text, transcript):
                    passed = True
                else:
                    reason = "YAML content does not match the required structure."
            else:
                if expected_text in transcript:
                    passed = True
                else:
                    reason = f"Transcript does not contain expected text: {expected_text}"
        elif 'regex' in matcher:
            try:
                if re.search(matcher['regex'], transcript, re.MULTILINE):
                    passed = True
                else:
                    reason = f"Transcript does not match regex: {matcher['regex']}"
            except re.error:
                reason = f"Invalid regex in matcher: {matcher.get('regex')}"
        else:
            # Fallback to looking for the command line; support 'k' alias for 'kubectl'
            if cmd and cmd in transcript:
                passed = True
            else:
                # Check for shorthand alias 'k' in place of 'kubectl'
                if cmd.startswith('kubectl'):
                    alias_cmd = 'k' + cmd[len('kubectl'):]
                    if alias_cmd in transcript:
                        passed = True
                    else:
                        reason = f"Transcript does not include command: {cmd}"
                else:
                    reason = f"Transcript does not include command: {cmd}"
        if passed:
            details.append(f"PASS: {cmd}")
        else:
            details.append(f"FAIL: {cmd} -> {reason}")
            all_pass = False
    return all_pass, details

