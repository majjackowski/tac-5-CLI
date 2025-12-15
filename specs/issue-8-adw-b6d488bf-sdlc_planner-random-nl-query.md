# Feature: Random Natural Language Query Generator

## Feature Description
This feature adds a "Generate Random Query" button to the Natural Language SQL Interface that automatically generates interesting natural language queries based on the existing database schema and table structures. When clicked, the button uses the LLM processor to create contextually relevant queries (limited to two sentences) and populates them directly into the query input field, overwriting any existing content. This enables users to discover query possibilities and learn how to interact with their data through concrete examples.

## User Story
As a user of the Natural Language SQL Interface
I want to click a button that generates interesting example queries based on my uploaded tables
So that I can discover what kinds of questions I can ask about my data and execute them with a single click

## Problem Statement
Users may not know what kinds of questions they can ask about their data or may lack inspiration for queries. Currently, users must come up with their own natural language queries, which can be challenging when first exploring a new dataset. There is no guided discovery mechanism to help users understand the capabilities of the natural language query interface or to provide query examples based on their specific data structure.

## Solution Statement
Add a dedicated "Generate Random Query" button alongside the existing primary action buttons in the query interface. This button will leverage the existing `llm_processor.py` infrastructure to analyze the current database schema and generate contextually appropriate natural language queries (maximum two sentences). The generated query will automatically populate the input field, replacing any existing text, allowing users to immediately execute it or modify it as needed. The button will be styled consistently with the "Upload Data" button and positioned with proper spacing using justify-content spacing.

## Relevant Files
Use these files to implement the feature:

- **app/server/core/llm_processor.py** (line 1-162) - Contains the LLM integration logic for both OpenAI and Anthropic. We'll add a new function `generate_random_query()` that analyzes the database schema and creates interesting natural language query suggestions.

- **app/server/server.py** (line 1-280) - The FastAPI server with all API endpoints. We'll add a new endpoint `POST /api/generate-random-query` to handle random query generation requests.

- **app/server/core/data_models.py** - Contains Pydantic models for request/response validation. We'll add `RandomQueryRequest` and `RandomQueryResponse` models.

- **app/server/core/sql_processor.py** (line 1-162) - Contains the `get_database_schema()` function which provides schema information needed for query generation.

- **app/client/index.html** (line 1-99) - The HTML structure of the application. We'll add the new "Generate Random Query" button in the query-controls section (around line 22-26).

- **app/client/src/main.ts** (line 1-423) - The main TypeScript file with all UI logic. We'll add event handlers and API calls for the random query generation feature.

- **app/client/src/api/client.ts** (line 1-79) - The API client module. We'll add a new method `generateRandomQuery()` to call the backend endpoint.

- **app/client/src/types.d.ts** (line 1-80) - TypeScript type definitions. We'll add `RandomQueryRequest` and `RandomQueryResponse` interfaces matching the backend models.

- **app/client/src/style.css** - The CSS stylesheet. We'll add styles for the new random query button to match the secondary button style (Upload Data style).

### New Files

- **app/server/tests/core/test_random_query.py** - Unit tests for the random query generation functionality, including tests for schema parsing, query generation with different table structures, error handling, and two-sentence limitation.

- **.claude/commands/e2e/test_random_query.md** - End-to-end test specification that validates the complete user flow: clicking the button, generating a query, populating the input field, and executing the generated query.

## Implementation Plan

### Phase 1: Foundation
Add the backend infrastructure to support random query generation. This includes:
- Creating new data models for the random query request/response
- Implementing the core query generation logic in `llm_processor.py` that analyzes schema and generates contextually interesting queries
- Adding comprehensive unit tests to ensure query quality and constraints (two-sentence limit)

### Phase 2: Core Implementation
Build the API endpoint and integrate it with the frontend:
- Add the FastAPI endpoint `/api/generate-random-query` to handle requests
- Create the frontend button UI with appropriate styling
- Implement the client-side API call and event handling
- Ensure the generated query properly overwrites the input field content

### Phase 3: Integration
Complete the feature with testing and polish:
- Add end-to-end tests to validate the complete user workflow
- Verify button placement and styling matches design requirements (justify spacing, Upload Data style)
- Test with various database schemas (single table, multiple tables, different column types)
- Validate error handling when no tables are available
- Run full regression test suite to ensure no breaking changes

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Backend Data Models
- Open `app/server/core/data_models.py`
- Add `RandomQueryRequest` Pydantic model with optional `table_names` field to optionally limit query generation to specific tables
- Add `RandomQueryResponse` Pydantic model with fields: `query` (str), `context` (str - brief explanation), `table_names` (List[str] - tables referenced), and optional `error` (str)
- Ensure models follow existing patterns in the file

### Step 2: Implement Random Query Generation Logic
- Open `app/server/core/llm_processor.py`
- Add a new function `generate_random_query(schema_info: Dict[str, Any], table_names: Optional[List[str]] = None) -> Dict[str, Any]`
- The function should:
  - Analyze the provided database schema to understand available tables, columns, and data types
  - Filter to specific tables if `table_names` parameter is provided
  - Use the existing OpenAI/Anthropic routing logic (similar to `generate_sql()`)
  - Create a prompt that asks the LLM to generate an interesting, realistic natural language query based on the schema
  - Include in the prompt: "Generate ONE interesting natural language query a user might ask. Limit to TWO sentences maximum. Make it specific and realistic."
  - Parse the LLM response and return a dict with: query text, context (why this query is interesting), and referenced table names
  - Handle errors gracefully with appropriate error messages
- Add helper function `generate_random_query_with_openai()` following the pattern of `generate_sql_with_openai()`
- Add helper function `generate_random_query_with_anthropic()` following the pattern of `generate_sql_with_anthropic()`

### Step 3: Write Backend Unit Tests
- Create `app/server/tests/core/test_random_query.py`
- Write test cases for:
  - `test_generate_random_query_single_table()` - Test with a single table schema
  - `test_generate_random_query_multiple_tables()` - Test with multiple tables
  - `test_generate_random_query_filters_tables()` - Test that table_names filter works correctly
  - `test_generate_random_query_two_sentence_limit()` - Verify the query respects the two-sentence limit
  - `test_generate_random_query_empty_schema()` - Test error handling when no tables exist
  - `test_generate_random_query_api_error()` - Test handling of LLM API errors
- Use pytest fixtures for mock schema data
- Mock OpenAI/Anthropic API calls to avoid real API usage during tests

### Step 4: Add Backend API Endpoint
- Open `app/server/server.py`
- Import the new data models: `RandomQueryRequest`, `RandomQueryResponse`
- Import the new function: `generate_random_query`
- Add new endpoint `@app.post("/api/generate-random-query", response_model=RandomQueryResponse)`
- Implementation should:
  - Get the current database schema using `get_database_schema()`
  - Check if schema has tables; if empty, return error response
  - Call `generate_random_query()` with schema and optional table filter
  - Return `RandomQueryResponse` with query and metadata
  - Include proper error handling and logging following existing patterns
  - Use try/except with structured logging like other endpoints

### Step 5: Add Frontend Type Definitions
- Open `app/client/src/types.d.ts`
- Add `RandomQueryRequest` interface matching the backend model
- Add `RandomQueryResponse` interface matching the backend model
- Ensure field names and types match exactly with Pydantic models

### Step 6: Add Frontend API Client Method
- Open `app/client/src/api/client.ts`
- Add new method `generateRandomQuery()` to the `api` export object
- Method should:
  - Accept optional `table_names` parameter
  - Make POST request to `/api/generate-random-query`
  - Return `Promise<RandomQueryResponse>`
  - Follow existing patterns in the file for error handling

### Step 7: Add Random Query Button to HTML
- Open `app/client/index.html`
- Locate the `query-controls` div (around line 22)
- Add a new button with id `random-query-button` and class `secondary-button`
- Button text should be "Generate Random Query"
- Position the button using flexbox with `justify-content: space-between` or similar to create spacing from primary buttons
- Ensure the button is between the Query button and Upload Data button

### Step 8: Add Button Styles
- Open `app/client/src/style.css`
- Review the existing `.secondary-button` styles (around line 89)
- Add any specific styles needed for `#random-query-button` if customization is needed
- Ensure the button matches the Upload Data button styling
- Update `.query-controls` to use `justify-content: space-between` for proper spacing between button groups

### Step 9: Implement Frontend Button Logic
- Open `app/client/src/main.ts`
- Add a new initialization function `initializeRandomQueryButton()`
- In this function:
  - Get reference to the `random-query-button` element
  - Add click event listener
  - On click, disable button and show loading state (similar to query button pattern)
  - Call `api.generateRandomQuery()`
  - On success, populate the `query-input` textarea with the generated query (overwrite existing content)
  - On error, display error message using `displayError()`
  - Re-enable button and restore original text
- Call `initializeRandomQueryButton()` in the `DOMContentLoaded` event listener

### Step 10: Create E2E Test Specification
- Create `.claude/commands/e2e/test_random_query.md`
- Follow the structure and format of `.claude/commands/e2e/test_basic_query.md`
- Include User Story section describing the random query generation feature
- Define Test Steps:
  1. Navigate to application URL
  2. Take screenshot of initial state
  3. Verify "Generate Random Query" button is present
  4. Upload sample data (users.json)
  5. Click "Generate Random Query" button
  6. Verify query input field is populated with generated query
  7. Verify generated query is non-empty and follows two-sentence limit
  8. Take screenshot of populated query
  9. Click "Query" button to execute the generated query
  10. Verify results are displayed
  11. Take screenshot of results
- Define Success Criteria:
  - Button is visible and clickable
  - Generated query appears in input field
  - Query overwrites any existing content
  - Generated query executes successfully
  - Query is limited to two sentences

### Step 11: Run Validation Commands
- Execute all commands from the Validation Commands section below
- Ensure all tests pass with zero errors
- Execute the E2E test and verify screenshots show expected behavior
- Confirm no regressions in existing functionality

## Testing Strategy

### Unit Tests
- **Query Generation Logic**: Test that `generate_random_query()` produces valid natural language queries based on schema
- **Two-Sentence Limit**: Verify queries are limited to maximum two sentences
- **Schema Analysis**: Test with various schema configurations (single table, multiple tables, different data types)
- **Error Handling**: Test behavior when schema is empty or API calls fail
- **Table Filtering**: Verify that optional table_names parameter correctly filters queries
- **LLM Provider Routing**: Test that OpenAI/Anthropic routing works correctly

### Edge Cases
- **No tables in database**: Should return helpful error message explaining no data is available
- **Single table with few columns**: Should generate meaningful query despite limited options
- **Complex multi-table schema**: Should generate queries that reference relevant tables with appropriate joins
- **Query exceeds two sentences**: LLM should be constrained by prompt, but validate response
- **API timeout or failure**: Should display user-friendly error message
- **Button spam clicking**: Disable button during API call to prevent duplicate requests
- **Empty query response**: Handle case where LLM returns empty or invalid response
- **Very long column/table names**: Ensure generated queries are still readable

## Acceptance Criteria
1. A "Generate Random Query" button is added to the UI with styling matching the "Upload Data" button
2. Button is positioned with appropriate spacing (using justify-apart or space-between) separate from primary action buttons
3. Clicking the button triggers a call to the backend `/api/generate-random-query` endpoint
4. Backend analyzes current database schema and generates contextually relevant natural language queries
5. Generated queries are limited to a maximum of two sentences
6. The generated query automatically populates the query input field, overwriting any existing content
7. Users can immediately execute the generated query by clicking the "Query" button
8. Error handling works correctly when no tables are loaded or when API calls fail
9. All existing functionality remains intact (no regressions)
10. Unit tests achieve high coverage for the new query generation logic
11. E2E test validates the complete user workflow from button click to query execution

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute your new E2E `.claude/commands/e2e/test_random_query.md` test file to validate this functionality works
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/server && uv run pytest tests/core/test_random_query.py -v` - Run specific random query tests with verbose output
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions

## Notes
- **LLM Usage**: This feature reuses the existing LLM infrastructure (`llm_processor.py`), so it will respect the same API key configuration (OpenAI priority, fallback to Anthropic)
- **Prompt Engineering**: The quality of generated queries depends heavily on the prompt design. The prompt should encourage diverse, realistic queries that demonstrate the capabilities of natural language SQL
- **Query Variety**: Consider adding randomization or context about previously generated queries to avoid repetitive suggestions
- **User Experience**: The button should be clearly labeled and positioned to be discoverable but not interfere with the primary query workflow
- **Two-Sentence Constraint**: This is enforced via the LLM prompt. Monitor in production to ensure compliance
- **Future Enhancement Ideas**:
  - Add a "shuffle" icon to the button for visual clarity
  - Store generated query history to avoid immediate repetition
  - Allow users to specify difficulty level or query type (aggregations, joins, filters, etc.)
  - Add tooltips explaining what the button does
  - Support generating multiple query suggestions at once
- **Performance**: Query generation requires an LLM API call, so there will be a 1-3 second delay. The loading state should be clear to users
- **Security**: Schema information is used in the prompt but no sensitive data is sent to the LLM (only table/column names and types)
