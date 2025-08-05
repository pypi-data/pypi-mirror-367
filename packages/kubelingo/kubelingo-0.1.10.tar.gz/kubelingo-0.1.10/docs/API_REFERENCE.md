# API Reference

This document provides the API specification for the kubelingo project, including core session management, cloud integration, and extensions.

## Session Manager API

### CKADStudySession Class

The main orchestrator for CKAD study sessions with cloud resources.

#### Constructor
```python
CKADStudySession(session_id: str = None, config: SessionConfig = None)
```
- `session_id` (optional): Unique identifier for the session. Auto-generated if not provided.  
- `config` (optional): Custom `SessionConfig`; uses defaults if not supplied.

#### Methods

```python
initialize_session() -> None
```
Initializes AWS credentials, EKS cluster, namespaces, and monitoring.  
Raises exceptions on credential or cluster errors.

```python
get_status() -> Dict[str, Any]
```
Returns session metadata, including IDs, times, cluster status, costs, and exercise counts.

```python
extend_session(minutes: int = 30) -> bool
```
Attempts to extend the session expiration by `minutes`. Returns True if successful.

```python
cleanup_session() -> None
```
Cleans up all cloud resources and marks session terminated.

```python
start_kubelingo(exercise_filter: str = None) -> None
```
Launches the kubelingo CLI quiz, optionally filtering by category.

### SessionConfig Class

```python
SessionConfig(
    session_duration: timedelta = timedelta(hours=4),
    cluster_config: Dict[str, Any] = None,
    namespaces: List[str] = None,
    monitoring_enabled: bool = True,
    auto_cleanup: bool = True
)
```
Holds configuration parameters for the study session.

## gosandbox Core API

*Under development — cloud credential automation and browser automation modules.*

## Cloud Integration API

*Under development — see `kubelingo/cloud_env.py` (planned) for EKS cluster creation,
namespace & workload setup, and cloud-specific exercise generation.*

## kubelingo Extensions API

### Exercise Generation

```python
generate_aws_exercises() -> List[Exercise]
```
Generates AWS-specific CKAD exercises.

```python
validate_exercise_solution(exercise_id: str, student_yaml: str) -> ValidationResult
```
Validates student YAML against expected solution and cloud context.

### Quiz Integration

```python
start_cloud_quiz(categories: List[str] = None, difficulty: str = None, time_limit: int = None) -> QuizSession
```
Interactive quiz session for cloud-specific questions.

### VimYamlEditor Class

```python
VimYamlEditor()
```
Interactive YAML editing engine using Vim (or your `$EDITOR`).

Methods:
- `create_yaml_exercise(exercise_type: str, template_data: dict = None) -> dict`
  Generate a Kubernetes YAML template for common resources (`pod`, `configmap`, `deployment`, `service`).
- `edit_yaml_with_vim(yaml_content: Union[str, dict], filename: str = "exercise.yaml") -> dict | None`
  Opens a temp YAML file in `$EDITOR`, then parses and returns the edited content.
- `validate_yaml(yaml_content: dict, expected_fields: list[str] = None) -> tuple[bool, str]`
  Checks for syntax and required fields (`apiVersion`, `kind`, `metadata`), returning (is_valid, message).
- `run_yaml_edit_question(question: dict, index: int = None) -> bool`
  Runs a single YAML editing exercise: opens Vim, validates, and compares against `correct_yaml`.

### vim_commands_quiz Function

```python
vim_commands_quiz() -> float
```
CLI quiz of essential Vim commands (insert mode, save & quit, delete line, etc.), returns accuracy percentage.

## Monitoring API

*Under development — cluster resource usage monitoring will be integrated.*