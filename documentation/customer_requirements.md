# User Requirements

Here is the design document for the user task management system with soft-delete functionality.
Please modify the design document as appropriate.

## User Task Management System (with Soft-Delete)

### Data Model (Firestore)
Firestore Collection: `tasks`
Each document represents a task with the following fields:
- id (string/Firestore doc ID): Unique task identifier (auto-generated by Firestore)
- userId (string): Owner (from JWT)
- title (string): Required
- description (string): Optional
- dueDate (timestamp): Optional
- status (enum): active, completed, deleted (default: active)
- createdAt, updatedAt (timestamps, Firestore serverTimestamp)
- completionDate (timestamp): Date when task was marked as completed
- deletionDate (timestamp): Date when task was marked as deleted
- notes (string): Free-form text field for user notes about the task
- updates (array): Array of update entries, each with { timestamp, user, updateText }, appended automatically on each edit

### AI_chats Collection
- **Collection Name:** AI_chats
- **Fields:**
  - `user_id` (string): User's ID or email
  - `inputText` (string): Text input from the AI tab
  - `createdAt` (timestamp): When the record was created
  - `updated_at` (timestamp): When the record was last updated (same as createdAt on insert)
  - `Response` (string): AI response from OpenAI (added after processing)
  - `prompt_name` (string): Name of the prompt used
  - `prompt_version` (number): Version of the prompt used

### AI_prompts Collection
- **Collection Name:** AI_prompts
- **Fields:**
  - `prompt_name` (string): Name of the prompt
  - `text` (string): Prompt text
  - `status` (enum): active, inactive (default: active)

All queries must filter by `userId` and `status` as appropriate.

### Backend Methods
Here is the description of the endpoints in a related system that interact with Firestore. Please create corresponding method calls in a separate file:
- GET /api/tasks: Query `tasks` where `userId` == req.user.id and `status` == 'active'.
- GET /api/tasks/completed: Query `tasks` where `userId` == req.user.id and `status` == 'completed'.
- GET /api/tasks/deleted: Query `tasks` where `userId` == req.user.id and `status` == 'deleted'.
- POST /api/tasks: Add new task document to `tasks` collection. Set `userId`, `createdAt`, `updatedAt`.
- PUT /api/tasks/:id: Update task document (if `userId` matches req.user.id).
- DELETE /api/tasks/:id: Set `status` to 'deleted', update `updatedAt` (soft-delete).
- PATCH /api/tasks/:id/restore: Set `status` to 'active', update `updatedAt`.
- POST /api/ai-chats: Accepts `{ inputText: string }` in request body, requires authentication (JWT), and stores a new document in Firestore `AI_chats` collection with fields: `user_id`, `inputText`, `createdAt`, `updated_at`. After saving, fetches the latest record from Firestore `AI_prompts` where `prompt_name` = "AI_Tasks" and `status` = "Active", uses the `text` field from this prompt as the system prompt for OpenAI (via Langchain), and the user's input as the human prompt. Gets the response from OpenAI, saves it in the same `AI_chats` record as `Response`, and returns it to the frontend.
- POST /api/ai-chats: Accepts `{ inputText: string }` in request body, requires authentication (JWT), and stores a new document in Firestore `AI_chats` collection with fields: `user_id`, `inputText`, `createdAt`, `updated_at`, `prompt_name`, and `prompt_version`. After saving, fetches the latest record from Firestore `AI_prompts` where `prompt_name` = "AI_Tasks" and `status` = "Active", uses the `text` field from this prompt as the system prompt for OpenAI (via Langchain), and the user's input as the human prompt. Gets the response from OpenAI, saves it in the same `AI_chats` record as `Response`, and returns it to the frontend.

All operations must check that the task's `userId` matches the authenticated user.

### Authentication
- Users authenticate via Google OAuth or Auth0.
- JWT tokens are issued and stored in local storage.
- All authenticated API requests must include the JWT in the `Authorization` header as a Bearer token (e.g., `Authorization: Bearer <JWT>`).
- API endpoints require authentication and validate the JWT token.

### Frontend
- Task List View: Active tasks
- Deleted Tasks View: Soft-deleted tasks
- Task Form: Create/Edit
- Navigation/menu to switch between views
- AI Tab:
  - Add a new tab labeled "AI" on the right of the main navigation/tab bar.
  - Tab content:
    - Single text input field
    - Submit button, disabled until input field is non-empty
    - On submit, send input to backend API
  - UI disables submit button until there is input text
  - No display of prior chats (MVP)

### Firestore Integration
- Use the official Firebase library for Python.
- Load Firestore credentials and project ID from environment variables.
- Initialize Firestore client at server startup.
- All task CRUD operations use Firestore methods.

### Security
- Firestore security rules must ensure users can only read/write their own tasks.
- Backend must verify `userId` matches authenticated user for all operations.
- Environment variables required: `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`.


### Error Handling & Logging
- Clear error messages for all Firestore operations
- Log all task CRUD operations (with userId, operation, and error details)
- Logging should be configurable by level (debug/info/warn/error)