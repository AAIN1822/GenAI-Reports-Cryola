# 🔐 FastAPI Authentication Service (JWT + OTP + SSO)

A production-ready authentication backend built with **FastAPI + SQLAlchemy**, featuring:

- ✅ User Registration & Login
- ✅ JWT Authentication (Access + Refresh Tokens)
- ✅ Single Sign-On (SSO) login (Azure AD / Google based on ID Token)
- ✅ Password Reset via OTP (Email-based)
- ✅ Role Management
- ✅ User Activity tracking (login/logout timestamps)
- ✅ Test suite using pytest + FastAPI TestClient

---

## 📂 Project Structure

app/
┣ api/
┃ ┗ v1/routes/auth.py 
┣ db/
┃ ┣ models/ 
┃ ┗ session.py 
┣ schemas/ 
┣ services/ 
┣ utils/ 
┗ main.py 
tests/
┗ test_auth.py 

## To run the application
uvicorn app.main:app --reload


## API will now be available at:
➡️ http://127.0.0.1:8000
➡️ Swagger docs: http://127.0.0.1:8000/docs


## Running tests:
pytest -v