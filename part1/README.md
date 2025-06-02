# ⭕ HBNB – Part 1 Technical Documentation

Welcome to the **technical documentation** for Part 1 of the **HBnB Project**, a simplified clone of Airbnb. This project is designed using a layered architecture with clear separation between the API, core logic, and data layers. This file explains the structure, diagrams, and system flow we built step-by-step to form a solid foundation for future implementation phases.

---

# 🚩 Task 0: High-Level Architecture – Package Diagram

The system follows a **three-layered architecture** using **package diagrams** for structure and the **Facade Pattern** for clean communication across layers.

---

## 🔶 Presentation Layer

### 📌 Purpose:
The entry point of the system. Handles user/API requests and responses.

### ⚙️ Components:
- `UserAPI`
- `PlaceAPI`
- `ReviewAPI`
- `AmenityAPI`

These APIs do **not** include logic. They receive HTTP requests (e.g., `POST /users`, `GET /places`) and delegate all processing to the Business Logic Layer via the **FacadeService**.

---

## 🟦 Business Logic Layer

### 📌 Purpose:
Contains the actual logic for handling business rules, processing data, and managing relationships between objects.

### ⚙️ Components:
- `User`
- `Place`
- `Review`
- `Amenity`
- `FacadeService`

Each class handles its entity's logic (e.g., `User` validates emails, `Place` calculates pricing logic). `FacadeService` unifies access to this logic, so API routes can call it directly without dealing with all individual models.

---

## 🟢 Persistence Layer

### 📌 Purpose:
Handles **storing and retrieving** data from the database or file system.

### ⚙️ Components:
- `DatabaseAccess`
  - `saveData()`
  - `retrieveData()`

This abstraction layer ensures the system can switch between storage engines (like FileStorage or DBStorage) without changing core logic.

---

## 🖼️ Package Diagram

🖱️ Click to view: **[UML/Package_Diagram.svg](./UML/Package_Diagram.svg)**

---

# 🧩 Task 1: Business Logic Class Diagram

This diagram illustrates the internal structure of the Business Logic Layer and how entities are related.

## 📌 Main Entities

- **User**
  - Attributes: `id`, `first_name`, `last_name`, `email`, `password`, `is_admin`, `created_at`, `updated_at`
  - Relationships: Can create Places and submit Reviews

- **Place**
  - Attributes: `id`, `title`, `description`, `price`, `latitude`, `longitude`, `created_at`, `updated_at`
  - Relationships: Belongs to a User, has many Amenities and Reviews

- **Amenity**
  - Attributes: `id`, `name`, `description`, `created_at`, `updated_at`
  - Relationships: Can belong to many Places

- **Review**
  - Attributes: `id`, `text`, `rating`, `created_at`, `updated_at`
  - Relationships: Linked to a User and a Place
 
---

## 🖼️ Class Diagram 

🖱️ Click to view: **[UML/Class_Diagram.svg](./UML/Class_Diagram.svg)**

---

## 🖼️ Source Code

🖱️ Click to view: **[Code/Class_Diagram.mmd](../code/Class_Diagram.mmd)**

---

# 🔁 Task 2: API Sequence Diagrams

This diagrams shows how API calls interact with all layers.

---

## 🖼️ Sequence Diagram for Login

🖱️ Click to view: **[UML/Login_Sequence_Diagram.svg](.UML/Login_Sequence_Diagram.svg)**

---

## 🔗 Source Code for login

🖱️ Click to view: **[code/Login_Sequence_Diagram.mmd](..code/Login_Sequence_Diagram.mmd)**

---

## 🖼️ Sequence Diagram for Submit Review 

🖱️ Click to view: **[UML/Submit_Review_Sequence_Diagram.svg](.UML/Submit_Review_Sequence_Diagram.svg)**

---

## 🔗 Source Code for Submit Review 

🖱️ Click to view: **[code/Submit_Review_Sequence_Diagram.mmd](..code/Submit_Review_Sequence_Diagram.mmd)**


---

# ✅ Summary

- Built using **Layered Architecture**
- Applied the **Facade Pattern** for clarity and modularity
- Created **UML Diagrams** to guide implementation

---

📁 Directory Layout

```
part1/
├── README.md
├── UML/
│   └── Package_Diagram.svg
│   └── Class_Diagram.svg
│   └── Login_Sequence_Diagram.svg
│   └── Submit_Review_Sequence_Diagram.svg
├── Code/
│   ├── Class_Diagram.mmd
│   ├── Sequence_Login.mmd
│   └── Sequence_Submit_Review.mmd
```

© 2025 – Holberton School & Tuwaiq Academy
