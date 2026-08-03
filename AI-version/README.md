### Prompt 1 — bare bones

**Prompt used:**
"Build a REST API for a to-do list using FastAPI. It should support creating, reading, updating, and deleting tasks."

**What the AI produced:**
-I wanted something that had POST, GET all, GET one, PUT, DELETE, on an in-memory list, and it actually had that without being told specifically.

- Extension of the same pattern I used myself, with Pydantic models: TaskCreate, TaskUpdate
- Even though I do not require it, added its own validation on POST (empty title is 400)
  Automatically added the attribute `id` to all created objects, defaulting it to an empty string, and set the attribute `done: false` on all created objects without speculating, even if the exact rule is not specified

**What it got wrong / silently decided:**
Did not build the following routes: -- Getting rid of the `GET /` and `GET /health` altogether, which I never mentioned.

- `DELETE` returns `200` with a body (`{"message": "...", "task": ...}`) instead of the spec's `204` with an empty body
  Both title and done are required in all puts — so a partial PUT such as {"done": true} would be considered invalid, and error 422 would be returned, because it's missing the title attribute.
  No validation whatsoever on `PUT`: If a title put is whitespace only it would be silently accepted, whereas I would be adding an error message.
- Used `detail` instead of `error`: This is probably a FastAPI convention, as I did the same, but maybe there's a real bug.

**What my prompt forgot to specify:**
I never mentioned the root/health endpoints, the exact 204-no-body rule for delete, or that updates should support partial fields. The AI filled those gaps by making its own reasonable-but-different assumptions.

**Do I understand the AI's version well enough to explain it?**
Yes, the structure is nearly identical to mine (Pydantic models, in-memory list, same id-assignment logic), which made it easy to spot exactly where it diverged.

### Prompt 2 — improved, full spec

**Prompt used:**
Build a FastAPI to-do list API with in-memory storage (a Python list, no database, no files). Include these endpoints:

GET / — returns API info like {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}
GET /health — returns {"status": "ok"}
GET /tasks — returns the full list of tasks
GET /tasks/{id} — returns one task, or 404 if the id doesn't exist
POST /tasks — accepts {"title": "..."}, auto-assigns the next id and sets done: false, returns 201. If title is missing or empty/whitespace, return 400.
PUT /tasks/{id} — accepts a partial update (title and/or done, both optional), only changes fields that are provided, returns 404 if the id doesn't exist, returns 400 if title is provided but empty
DELETE /tasks/{id} — removes the task and returns 204 with an empty body, or 404 if the id doesn't exist

Each task has id (int), title (string), done (boolean). Add short one-line descriptions to each endpoint for the Swagger docs."

What got better in Prompt 1:

- Added `GET /` / `GET /health` — both previouly absent.
  With explicit `Response(status_code=204)` return, it is correct now; before, it was the wrong status code: `DELETE` returns 200 with no content.
- `@RPC` now now has support for partial updates, as in my own implementation (with Optional[str] / Optional[bool])
  The PUT method also does not accept empty/whitespace titles, this has been added to, as well as the POST method.
- Added descriptions for summary to all endpoints for Swagger docs — satisfies Stage 5 requirement
  Made use of the status constants provided by the ‘status’ module instead of using integers — I didn’t do this myself, but nice to see!

What it also missed or is different from my own work:

- tasks = [] is empty — The spec explicitly asked for 3 pre-filled example tasks and this prompt (and my own instructions) did not say that. This is my fault, I forgot to include it in the prompt and the AI didn't generate the placeholders by itself.
- Still doesn't use the error key of `"error": ...`, same issue as my own code but probably just the default that the FastAPI folks didn't bother with.
  The delete with explicit `Response(status_code=204)` has a bit more chatter, but is otherwise identical to my version's plain return.

I forgot to mention, my prompt was limited to
The example tasks already filled in — a minor detail of spec, but that could be an actual thing that people would actually do, and it wasn't a mistake by AI.

One sentence description of the changes between rounds:
Every structural gap in Prompt 1 (missing root/health endpoints, wrong delete status code, no partial updates) was addressed by specifying them explicitly in Prompt 2, but an empty starter list indicates that even a detailed prompt may leave requirements unaddressed that an AI might be able to miss.

## AI vs Me (Stage 6 — the AI rematch)

**Prompt used:**
"I have an existing FastAPI to-do list API that currently stores tasks in memory. Migrate it to use a SQLite database via plain sqlite3 (no ORM). Requirements: create the table automatically if missing, seed 3 tasks only if empty, use parameterized queries, keep all 5 endpoints with identical behavior and status codes (200/201/204/400/404)."

**Note:** The AI-generated code lives on a separate branch (`AI-version`), kept apart from the hand-built implementation on `main`.

**What the AI did well:**

- Used
