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
Prompt: 
```
TODO
``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
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