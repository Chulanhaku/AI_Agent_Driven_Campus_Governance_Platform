# AI_Agent_Driven_Campus_Governance_Platform

An AI Agent-based comprehensive campus administration and governance system.

This project currently consists of:
- `agent_server`: Backend services based on FastAPI and SQLAlchemy.
- `frontend`: Frontend web interface.

---

## 2. Environment Requirements

### 2.1 Backend
- **Python**: `3.12.8`
- **PostgreSQL**: `16.13.1`
- **SQL Migration**: `Alembic`

### 2.2 Frontend
- **Node.js**: (LTS version recommended)
- **npm**: Package manager

---

## 3. Project Structure

```text
AI_Agent_Driven_Campus_Governance_Platform/
├─ agent_server/   # Backend source code
└─ frontend/       # Frontend source code

```

## 4. Backend Setup
- 4.1 Navigate to the backend directory
cd agent_server
- 4.2 Create a virtual environment
python -m venv .venv
- 4.3 Activate the virtual environment
Windows PowerShell
.\.venv\Scripts\activate

- 4.4 Install dependencies
pip install -r requirements.txt
- 4.5 Database Configuration & Migration
alembic upgrade head

- 4.6 Seed Data 
Execute all test data scripts located under database/seed. You may also populate the database manually as needed.

## 5.Frontend Setup

- 5.1 Navigate to the frontend directory
Open a new terminal and run:
cd frontend
- 5.2 Install dependencies
npm install
- 5.3 Start the development server
npm run dev

Note: If this command fails, please check the scripts section in frontend/package.json to verify the defined startup command and execute accordingly.