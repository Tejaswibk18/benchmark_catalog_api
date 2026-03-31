# 🚀 Benchmark Platform API

A **FastAPI + MongoDB** based backend system to manage:

* 📚 Benchmark Catalog
* ⚙️ Benchmark Execution
* 🖥️ Platform Pool

with validation, workflow orchestration, versioning, and soft delete support.

---

# 📌 Features

## 📚 Benchmark Catalog

* ✅ Create benchmark templates
* 🔍 Get benchmarks with filters
* ✏️ Update & Patch benchmarks
* 🗑️ Soft delete (ARCHIVED status)
* 🧾 Version history tracking

---

## ⚙️ Benchmark Execution

* 🚀 Execute benchmarks using workflows
* 🔗 Multi-stage workflow support
* 📊 Dynamic parameters & schema validation
* 🔄 Execution ↔ Workflow linking
* 📁 Optional workflow catalog storage
* 📥 Fetch execution with full workflow details
* ✏️ Patch execution (sync across collections)
* 🗑️ Soft delete execution

---

## 🖥️ Platform Pool

* 🧩 Manage platform resources (SUTs)
* ➕ Add / update platform entries
* 🔍 Fetch available platforms
* 🔗 Map platforms to executions
* ⚙️ Resource configuration support

---

## 🔐 Security & Validation

* 🔐 JWT-based authentication (Delete APIs)
* 🧠 Pydantic v2 field-level validation
* ✅ Regex-based input validation
* 🔄 Conditional field validation
* ⚡ Optimized service logic

---

# 🏗️ Tech Stack

* **Backend:** FastAPI
* **Database:** MongoDB
* **Validation:** Pydantic v2
* **Authentication:** JWT (python-jose)
* **Server:** Uvicorn

---

# 📂 Project Structure

```
benchmark_platform_api
│
├── app
│   ├── auth
│   │   ├── jwt_handler.py
│   │   └── auth_dependency.py
│   │
│   ├── routes
│   │   ├── benchmark_routes.py
│   │   ├── benchmark_execution_routes.py
│   │   └── platform_routes.py
│   │
│   ├── services
│   │   ├── benchmark_service.py
│   │   ├── benchmark_execution_service.py
│   │   └── platform_service.py
│   │
│   ├── repositories
│   │   ├── benchmark_repository.py
│   │   ├── benchmark_execution_repository.py
│   │   └── platform_repository.py
│   │
│   ├── schemas
│   │   ├── benchmark_schema.py
│   │   ├── benchmark_execution_schema.py
│   │   └── platform_schema.py
│   │
│   ├── database
│   │   └── connection.py
│   │
│   └── utils
│       └── response.py
│
└── main.py
```

---

# ⚙️ Installation

```bash
git clone <your-repo-url>
cd benchmark_platform_api

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

# ▶️ Run Server

```bash
uvicorn main:app --reload
```

👉 Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# 🔐 Authentication Flow

Currently, only **DELETE APIs are protected**

### 1. Get Token

```
POST /login
```

Response:

```json
{
  "token": "your_jwt_token"
}
```

---

### 2. Authorize in Swagger

Click **Authorize 🔓**

```
Bearer <your_token>
```

---

### 3. Use Protected APIs

```
DELETE /benchmark/{id}
DELETE /execution/{id}
DELETE /platform/{id}
```

---

# 📌 API Endpoints

## 📚 Benchmark Catalog

| Method | Endpoint        | Description      | Auth |
| ------ | --------------- | ---------------- | ---- |
| POST   | /benchmark      | Create benchmark | ❌    |
| GET    | /benchmark      | Get / filter     | ❌    |
| PUT    | /benchmark/{id} | Full update      | ❌    |
| PATCH  | /benchmark/{id} | Partial update   | ❌    |
| DELETE | /benchmark/{id} | Soft delete      | 🔒   |

---

## ⚙️ Benchmark Execution

| Method | Endpoint        | Description        | Auth |
| ------ | --------------- | ------------------ | ---- |
| POST   | /execution      | Create execution   | ❌    |
| GET    | /execution      | Get execution data | ❌    |
| PATCH  | /execution/{id} | Update execution   | ❌    |
| DELETE | /execution/{id} | Soft delete        | 🔒   |

---

## 🖥️ Platform Pool

| Method | Endpoint       | Description     | Auth |
| ------ | -------------- | --------------- | ---- |
| POST   | /platform      | Add platform    | ❌    |
| GET    | /platform      | Get platforms   | ❌    |
| PATCH  | /platform/{id} | Update platform | ❌    |
| DELETE | /platform/{id} | Soft delete     | 🔒   |

---

# 📊 Benchmark Execution Schema (Simplified)

```json
{
  "benchmark_name": "string",
  "catalog_name": "string",
  "environment": "string",
  "workflow": {
    "stages": [
      {
        "stage_name": "string",
        "stage_order": 1,
        "task_name": "string",
        "executor": {}
      }
    ]
  }
}
```

---

# 🔄 Workflow System

* Multi-stage execution pipeline
* Ordered execution via `stage_order`
* Dynamic executor support
* Parameter schema driven execution

---

# 🧾 History Tracking (Catalog)

```json
{
  "catalog_version": "2",
  "changed_on": "timestamp",
  "changed_by": "user",
  "change_type": "UPDATE",
  "changes": [
    {
      "path": "status",
      "old_value": "DRAFT",
      "new_value": "APPROVED"
    }
  ]
}
```

---

# 🔁 Status Workflow

```
DRAFT → PENDING-APPROVAL → APPROVED → PUBLISHED
                ↓
             REJECTED
```

---

# 🧠 Validations Implemented

* Required fields validation
* Regex validation (A-Z, 0-9, _)
* Workflow structure validation
* Parameter schema validation
* Status validation
* Conditional validation (workflow catalog save)

---

# 🔒 RBAC Logic (Delete)

* Only owner can delete

Condition:

```
created_by == user_email
```

Allowed statuses:

```
DRAFT | PENDING-APPROVAL | REJECTED
```

Soft delete updates:

```
status → ARCHIVED
```

---

# 🔗 Data Relationships

```
Benchmark Execution
        │
        ├── workflow_runs
        │
        └── workflow_catalog (optional)
```

---

# 🛠️ Future Improvements

* Full RBAC (Admin, Reviewer roles)
* DB-based authentication
* Pagination & sorting
* Logging & monitoring
* Execution status tracking (RUNNING, SUCCESS, FAILED)
* Retry & scheduling engine

---

# 👨‍💻 Author

**Tejaswi BK**

---

# ⭐ If you like this project

Give it a ⭐ on GitHub!
