# Distributed Chat Backend with Redundancy

This project is a **Python-based backend** designed to handle message storage in a database and ensure **high availability and redundancy** through communication between multiple backend instances using message queues (RabbitMQ).

## ⚙️ Key Features

- 💬 Stores incoming chat messages in a relational database.
- 🔁 Redundancy and synchronization across multiple backend instances.
- 🕸️ Inter-process communication using RabbitMQ.
- 🔐 Horizontally scalable architecture.
- 🚀 Ready for deployment in Docker/Kubernetes environments.

---

## 🧱 High-Level Architecture

```
+-----------+       +-------------+       +-----------+
| Frontend  | <---> |  Backend A  | <---> |  Backend B |
+-----------+       +-------------+       +-----------+
                        ↑   ↓                  ↑   ↓
                      [RabbitMQ] <----------> [RabbitMQ]
                        ↑   ↓                  ↑   ↓
                      [Database]            [Database]
```

> All backend instances are synchronized via message queues, allowing for load distribution and consistency.

---

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AbelGRubio/backend-chat.git
   cd backend-chat
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the required variables (RabbitMQ, DB, etc.)

---

## ▶️ Running the App

```bash
python src
```

Or with FastAPI and Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🛠 Required Environment Variables

```env
RABBITMQ_URL=amqp://user:password@rabbitmq:5672/
DATABASE_URL=postgresql://user:password@localhost:5432/chat
INSTANCE_ID=backend-a
```

---

## ✅ Requirements

- Python 3.12+
- RabbitMQ
- PostgreSQL (or equivalent)
- Docker (optional but recommended)

---

## 📦 Useful Commands

- Generate semantic version:
  ```bash
  semantic-release version
  ```

- Run tests (if configured):
  ```bash
  pytest
  ```

---

## 🧪 Tests

_Pending integration of automatic tests using `pytest`._

---

## 🤝 Contributing

Contributions, suggestions, and issues are welcome! Feel free to open a PR or issue.

---

## 🪪 License

This project is licensed under the [MIT License](LICENSE).

---

## ✨ Author

**Abel G. Rubio**  
GitHub: [@AbelGRubio](https://github.com/AbelGRubio)