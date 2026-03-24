# 🚀 Benchmark Catalog API

A **FastAPI + MongoDB** based backend system to manage benchmark templates with validation, version history, and soft delete functionality.

---

## 📌 Features

* ✅ Create benchmark catalog
* 🔍 Get all benchmarks with filters
* ✏️ Update & Patch benchmarks
* 🗑️ Soft delete (ARCHIVED status)
* 🧾 Version history tracking
* 🔐 JWT-based authentication (for delete)
* 🧠 Field-level validation (Pydantic v2)
* ⚡ Optimized service logic (minimal if-else)

---

## 🏗️ Tech Stack

* **Backend:** FastAPI
* **Database:** MongoDB
* **Validation:** Pydantic v2
* **Authentication:** JWT (python-jose)
* **Server:** Uvicorn

---

## 📂 Project Structure

```
benchmark_catalog_api
│
├── app
│   ├── auth
│   │   ├── jwt_handler.py
│   │   └── auth_dependency.py
│   │
│   ├── routes
│   │   └── benchmark_routes.py
│   │
│   ├── services
│   │   └── benchmark_service.py
│   │
│   ├── repositories
│   │   └── benchmark_repository.py
│   │
│   ├── schemas
│   │   └── benchmark_schema.py
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

## ⚙️ Installation

```bash
git clone <your-repo-url>
cd benchmark_catalog_api

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

## ▶️ Run Server

```bash
uvicorn main:app --reload
```

Open Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## 🔐 Authentication Flow

Currently, only **DELETE API is protected**.

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

Click **Authorize 🔓** and paste:

```
Bearer <your_token>
```

---

### 3. Use Protected API

```
DELETE /benchmark/{id}
```

---

## 📌 API Endpoints

| Method | Endpoint        | Description      | Auth |
| ------ | --------------- | ---------------- | ---- |
| POST   | /benchmark      | Create benchmark | ❌    |
| GET    | /benchmark      | Get all / filter | ❌    |
| PUT    | /benchmark/{id} | Full update      | ❌    |
| PATCH  | /benchmark/{id} | Partial update   | ❌    |
| DELETE | /benchmark/{id} | Soft delete      | 🔒   |
| POST   | /login          | Get JWT token    | ❌    |

---

## 📊 Benchmark Schema (Simplified)

```json
{
  "catalog_name": "string",
  "benchmark_name": "string",
  "benchmark_category": "string",
  "scripts": {
    "sut_teardown": "string",
    "sut_setup": "string"
  },
  "run_parameters": {},
  "metrics": ["string"],
  "visibility": "Public",
  "status": "DRAFT"
}
```

---

## 🔁 Status Workflow

```
DRAFT → PENDING-APPROVAL → APPROVED → PUBLISHED
                ↓
             REJECTED
```

Delete allowed only when:

```
DRAFT | PENDING-APPROVAL | REJECTED
```

Soft delete updates:

```
status → ARCHIVED
```

---

## 🧾 History Tracking

Every update/patch stores:

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

## 🧠 Validations Implemented

* Required fields check
* Alphabet + underscore validation
* OS validation (`windows`, `linux`)
* Run parameters key validation
* Metrics non-empty validation
* LTS mode conditional validation
* Status validation

---

## 🔒 RBAC Logic (Delete Only)

* Only **owner can delete**
* Condition:

  ```
  created_by == user_email
  ```
* Status must be:

  ```
  DRAFT | PENDING-APPROVAL | REJECTED
  ```

---

## 🛠️ Future Improvements

* Full RBAC (Admin, Reviewer roles)
* User authentication system (DB-based)
* Status transition guard
* Pagination & sorting
* Logging & monitoring

---

## 👨‍💻 Author

Tejaswi BK

---

## ⭐ If you like this project

Give it a ⭐ on GitHub!
