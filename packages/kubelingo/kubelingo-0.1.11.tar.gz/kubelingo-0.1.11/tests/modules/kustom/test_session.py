import pytest
from unittest.mock import MagicMock, patch
import json
import os
from kubelingo.modules.custom.session import NewSession, AIProcessor

@pytest.fixture
def custom_session():
    """Fixture to create a NewSession instance with a mock logger."""
    logger = MagicMock()
    return NewSession(logger=logger)

def test_ai_processor_stub():
    """Test the AIProcessor stub's basic functionality."""
    processor = AIProcessor()
    raw_data = [
        {'prompt': 'What is your name?', 'response': 'Sir Lancelot of Camelot.'},
        {'prompt': 'What is your quest?', 'response': 'To seek the Holy Grail.'}
    ]
    formatted = processor.format_questions(raw_data)
    assert len(formatted) == 2
    assert formatted[0]['prompt'] == 'What is your name?'
    assert formatted[0]['type'] == 'command'
    assert formatted[0]['category'] == 'custom'

def test_ai_processor_empty_data():
    """Test AIProcessor with empty raw data."""
    processor = AIProcessor()
    formatted = processor.format_questions([])
    assert formatted == []

def test_ai_processor_missing_keys():
    """Test AIProcessor with data missing required keys."""
    processor = AIProcessor()
    raw_data = [
        {'prompt': 'This one is okay', 'response': 'yes'},
        {'prompt': 'This one has no response'},
        {'response': 'This one has no prompt'}
    ]
    formatted = processor.format_questions(raw_data)
    assert len(formatted) == 1
    assert formatted[0]['prompt'] == 'This one is okay'

def test_ai_processor_with_explanation():
    """Test AIProcessor correctly handles an explanation field."""
    processor = AIProcessor()
    raw_data = [
        {'prompt': 'p', 'response': 'r', 'explanation': 'e'}
    ]
    formatted = processor.format_questions(raw_data)
    assert len(formatted) == 1
    assert formatted[0]['explanation'] == 'e'

def test_initialize_success(custom_session, tmp_path):
    """Test successful initialization with a valid file path."""
    questions_file = tmp_path / "questions.json"
    questions_file.touch()
    
    with patch('builtins.input', return_value=str(questions_file)):
        assert custom_session.initialize() is True
    assert custom_session.custom_questions_file == str(questions_file)

def test_initialize_file_not_found(custom_session):
    """Test initialization failure when file does not exist."""
    with patch('builtins.input', return_value="nonexistent_file.json"):
        assert custom_session.initialize() is False
    assert custom_session.custom_questions_file is None

def test_initialize_user_cancellation(custom_session):
    """Test initialization is cancelled gracefully on KeyboardInterrupt."""
    with patch('builtins.input', side_effect=KeyboardInterrupt):
        with patch('builtins.print') as mock_print:
            assert custom_session.initialize() is False
            mock_print.assert_called_with("\nInitialization cancelled.")

def test_run_exercises(custom_session, tmp_path):
    """Test running exercises with a valid custom questions file."""
    questions_data = [
        {'prompt': 'list pods', 'response': 'kubectl get pods'}
    ]
    questions_file = tmp_path / "my_questions.json"
    with open(questions_file, 'w') as f:
        json.dump(questions_data, f)
    
    custom_session.custom_questions_file = str(questions_file)
    
    # Mock AIProcessor to return predictable data
    mock_processor = MagicMock()
    mock_processor.format_questions.return_value = [
        {'category': 'custom', 'type': 'command', 'prompt': 'list pods', 'response': 'kubectl get pods', 'explanation': ''}
    ]
    custom_session.ai_processor = mock_processor

    # The 'exercises' argument is ignored by this implementation
    custom_session.run_exercises([])
    
    # Check that questions were processed and stored
    assert len(custom_session.questions) == 1
    assert custom_session.questions[0]['prompt'] == 'list pods'
    mock_processor.format_questions.assert_called_once_with(questions_data)

def test_run_exercises_no_file(custom_session):
    """Test that run_exercises does nothing if no file is set."""
    with patch('builtins.print') as mock_print:
        custom_session.run_exercises([])
        mock_print.assert_called_with("Cannot run exercises, no questions file provided.")

def test_run_exercises_empty_file(custom_session, tmp_path):
    """Test running exercises with an empty but valid questions file."""
    questions_file = tmp_path / "empty.json"
    questions_file.write_text("[]")
    
    custom_session.custom_questions_file = str(questions_file)

    with patch('builtins.print') as mock_print:
        custom_session.run_exercises([])
        mock_print.assert_any_call("No valid questions found in the provided file.")
    assert custom_session.questions == []

def test_run_exercises_malformed_json(custom_session, tmp_path):
    """Test running exercises with a malformed JSON file."""
    questions_file = tmp_path / "malformed.json"
    questions_file.write_text('{"not": "valid json",}') # trailing comma
    
    custom_session.custom_questions_file = str(questions_file)

    with patch('builtins.print') as mock_print:
        custom_session.run_exercises([])
        # Check that an error message was printed, without being too specific
        # about the JSON decoder's error message, which can vary.
        found = False
        for call in mock_print.call_args_list:
            if "Error reading or parsing questions file" in call.args[0]:
                found = True
                break
        assert found, "Expected error message for malformed JSON was not printed."

def test_run_exercises_no_valid_questions_in_file(custom_session, tmp_path):
    """Test a file with valid JSON but no usable question data."""
    questions_data = [
        {'wrong_key': 'foo'},
        {'another_bad': 'bar'}
    ]
    questions_file = tmp_path / "no_questions.json"
    with open(questions_file, 'w') as f:
        json.dump(questions_data, f)
    
    custom_session.custom_questions_file = str(questions_file)

    with patch('builtins.print') as mock_print:
        custom_session.run_exercises([])
        mock_print.assert_any_call("No valid questions found in the provided file.")
    assert custom_session.questions == []

def test_cleanup_runs(custom_session):
    """Test that cleanup method can be called without error."""
    try:
        custom_session.cleanup()
    except Exception as e:
        pytest.fail(f"cleanup() raised an exception: {e}")
