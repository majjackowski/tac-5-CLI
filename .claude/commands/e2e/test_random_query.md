# E2E Test: Random Query Generation

Test random query generation functionality in the Natural Language SQL Interface application.

## User Story

As a user
I want to click a button that generates interesting example queries based on my uploaded tables
So that I can discover what kinds of questions I can ask about my data and execute them with a single click

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** core UI elements are present:
   - Query input textbox
   - Query button
   - Generate Random Query button
   - Upload Data button
   - Available Tables section

5. Upload sample data (users.json)
6. **Verify** the "Available Tables" section shows the uploaded table
7. Take a screenshot after data upload

8. Click the "Generate Random Query" button
9. **Verify** the button shows a loading state briefly
10. **Verify** the query input field is populated with generated query text
11. **Verify** the generated query is non-empty
12. **Verify** the generated query contains at most 2 sentences (count periods/question marks)
13. Take a screenshot of the populated query

14. Click the "Query" button to execute the generated query
15. **Verify** the query executes successfully
16. **Verify** results are displayed
17. Take a screenshot of the query results

18. Click "Generate Random Query" button again
19. **Verify** a different query is generated (compare with previous query)
20. **Verify** the new query overwrites the previous content in the input field
21. Take a screenshot of the new query

## Success Criteria
- "Generate Random Query" button is visible and clickable
- Button shows loading state during API call
- Generated query appears in input field
- Query overwrites any existing content
- Generated query is limited to two sentences maximum
- Generated query executes successfully when Query button is clicked
- Multiple clicks generate different queries
- 4 screenshots are taken
