# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
Implement an LLM-powered alternative in extract_action_items_llm(), using Ollama Python library to connect to the local llama3.1:8b model. Ask the model to perform action item extraction.
```

Generated Code Snippets:
```
week2/app/services/extract.py: lines 68-95
- Added ActionItems Pydantic model for structured JSON output (lines 68-69)
- Added extract_action_items_llm() function that calls Ollama chat API
  with llama3.1:8b model and parses structured output (lines 72-95)
- Added pydantic BaseModel import (line 8)
```

### Exercise 2: Add Unit Tests
Prompt 1:
```
Write unit tests for extract_action_items_llm() covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, random text with a mix of alphabets, numbers and special characters, words with typos). Also think about edge cases (e.g., empty input).
```

Prompt 2:
```
The function name of the generated test cases should include the full name of the function being tested.
```

Prompt 3:
```
The assertions in the test cases could be more stricter as we capture structured output from the LLM in extract_action_items_llm()
```

Prompt 4:
```
As per my testing, the LLM is likely to echo back the task items from the input. Instead of doing `assert "migrate" in joined or "database" in joined or "postgresql" in joined`, you can directly match the keyword(s) with json element in the LLM output. Apply the same principle to the other test cases.
```

Generated Code Snippets:
```
week2/tests/test_extract.py: lines 22-121
- Added import for extract_action_items_llm (line 4)
- test_extract_action_items_llm_empty_input: empty/whitespace input returns [] (lines 25-29)
- test_extract_action_items_llm_bullet_list: dash-prefixed bullet items (lines 32-44)
- test_extract_action_items_llm_keyword_prefixed: TODO/ACTION/NEXT prefixed lines (lines 47-59)
- test_extract_action_items_llm_mixed_text: narrative mixed with actionable sentences (lines 62-73)
- test_extract_action_items_llm_special_characters_and_numbers: input with #, !, @, &, numbers (lines 76-88)
- test_extract_action_items_llm_typos_in_input: misspelled words still extracted (lines 91-103)
- test_extract_action_items_llm_no_action_items: purely narrative text returns empty list (lines 106-110)
- test_extract_action_items_llm_returns_list_of_strings: return type validation (lines 113-120)
```

### Exercise 3: Refactor Existing Code for Clarity

Prompt 1 (input validation):
```
I want to refactor the exisiting codebase of week2 web applcation.
To start with, improve the input validation using well-defined API schemas. Consider leveraging Pydantic library for the implementation.
```

Prompt 2 (database layer cleanup):
```
Let's proceed with data persistence layer cleanup.
```

Prompt 3 (database layer cleanup — follow-up):
```
It's much better to set up connection as a context manager using with syntax, so we benefit from automatic commit/rollback.
```

Prompt 4 (database layer cleanup — follow-up):
```
Put get_connection() in the with block.
```

Prompt 5 (app lifecycle & config management):
```
Can we do better in terms of application lifecycle management and configuration?
```

Prompt 6 (error handling — planning):
```
What can we do for the error handling?
```

Prompt 7 (cleanup):
```
As the last step, clean up unused imports for week2 web app.
```

Generated/Modified Code Snippets:
```
week2/app/config.py: lines 1-12 (new file)
- Centralized configuration with environment variable overrides for
  DATA_DIR, DB_PATH, and OLLAMA_MODEL

week2/app/db.py: lines 1-112
- Imports DATA_DIR, DB_PATH from config instead of hardcoding paths (line 6)
- Singleton connection with lazy initialization via get_connection() (lines 11-18)
- mark_action_item_done() returns cursor.rowcount instead of None (lines 97-104)

week2/app/main.py: lines 1-49
- Replaced @app.on_event startup/shutdown with lifespan context manager (lines 17-21)
- Removed unused imports: Any, Dict, Optional, HTTPException, db (lines 1-13)
- Added global exception handler for OllamaServiceError → 503 (lines 37-39)
- Added global exception handler for Exception → 500 with logging (lines 42-45)

week2/app/services/extract.py: lines 1-136
- Added logging, RequestError, ResponseError, ValidationError imports (lines 3, 7-8)
- Read OLLAMA_MODEL from config module instead of hardcoding (line 10)
- Defined OllamaServiceError custom exception (lines 15-16)
- Wrapped chat() call in try/except for RequestError and ResponseError (lines 83-105)
- Wrapped model_validate_json() in try/except for ValidationError (lines 107-111)

week2/app/routers/action_items.py: lines 1-86
- Added Pydantic request/response models: ExtractRequest, MarkDoneRequest,
  ActionItemOut, ExtractResponse, ActionItemDetail, MarkDoneResponse (lines 13-43)
- Added HTTPException import (line 5)
- mark_done checks rows_affected == 0 → raises 404 (lines 82-84)

week2/app/routers/notes.py: lines 1-41
- Added Pydantic request/response models: CreateNoteRequest, NoteOut (lines 10-18)

week2/tests/test_extract.py: lines 130-157
- test_extract_action_items_llm_ollama_unreachable: mocks chat to raise
  RequestError, asserts OllamaServiceError (lines 133-138)
- test_extract_action_items_llm_ollama_model_error: mocks chat to raise
  ResponseError, asserts OllamaServiceError (lines 141-146)
- test_extract_action_items_llm_malformed_response: mocks chat to return
  invalid JSON, asserts OllamaServiceError (lines 149-156)

week2/tests/test_error_handling.py: lines 1-76 (new file)
- test_mark_done_nonexistent_item_returns_404 (lines 39-46)
- test_get_nonexistent_note_returns_404 (lines 49-56)
- test_extract_empty_text_returns_422 (lines 59-62)
- test_db_error_returns_500 (lines 65-75)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task

Prompt 1 (planning):
```
**Context

We have implemented LLM-powered action items extraction for week2 web app in extract_action_items_llm().

**Task

- Integrate the LLM-powered extraction a new endpoint
- Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction via the new endpoint
- Expose one more endpoint to retrieve all notes from the SQLite database
- Update the frontend to include a "List Notes" button that, when clicked, fetches and displays all the notes using the new endpoint from the previous step
```

Prompt 2 (debugging — initial report):
```
I launched the week2 web app and typed in the following text as Notes:

Had a great team lunch. The weather was sunny.
We need to migrate the database to PostgreSQL by Friday.
John should update the API docs. The office plant looks healthy."
With the Save as note option selected, I got a "Error extracting items" message from the page.

Debug and fix the issue.
```

Prompt 3 (debugging — clarification):
```
With the quoted content, extract_action_items_llm() should return 2 action items instead of an empty list.
```

Prompt 4 (debugging — additional error report):
```
The same error occurs when I click the 'Extract LLM' button.
```

Prompt 5 (debugging — stack trace):
```
Launched the server again and entered the same text as notes and hit the button 'Extract LLM', got the following stack trace from the server:

sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 8263176064 and this is thread id 6111424512
```

Prompt 6 (debugging — second stack trace):
```
[Provided TypeError stack trace from db.insert_action_items showing cursor.lastrowid is None after executemany]
```

Prompt 7 (frontend validation):
```
When I launched the server, left the notes block empty and clicked on either 'Extract' or 'Extract LLM' button, I got an error message 'Error extracting item' on the UI. Why?
```

Prompt 8 (frontend fix):
```
fix the frontend to show a user-friendly message for empty text
```

Generated Code Snippets:
```
week2/app/routers/action_items.py: lines 9, 65-82
- Added imports for extract_action_items_llm and OllamaServiceError (line 9)
- Added POST /action-items/extract-llm endpoint that mirrors /extract but
  uses LLM extraction, catches OllamaServiceError → HTTP 503 (lines 65-82)

week2/app/routers/notes.py: lines 35-41
- Added GET /notes endpoint that calls db.list_notes() and returns
  list[NoteOut] (lines 35-41)

week2/frontend/index.html: lines 27, 32-35, 42-47, 81-82, 84-101
- Added "Extract LLM" button next to existing "Extract" button (line 27)
- Added "List Notes" button and #notes container (lines 32-35)
- Refactored extract logic into shared doExtract(endpoint) function (lines 42-79)
- Added client-side empty text validation with user-friendly message (lines 43-47)
- Added click handlers for Extract LLM and List Notes buttons (lines 81-82, 84-101)

week2/app/db.py: lines 15, 70-82
- Added check_same_thread=False to sqlite3.connect() to fix threading error
  with FastAPI's threadpool-based sync handler dispatch (line 15)
- Added early return for empty items list in insert_action_items() (lines 71-72)
- Replaced executemany with individual execute calls to reliably capture
  lastrowid for each inserted action item (lines 74-82)
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 