"""
FastAPI User Management API
============================

A production-ready CRUD API for user management, built with FastAPI,
SQLAlchemy, and Pydantic.

This package contains the full application:
    - config.py          Application settings (env-driven)
    - database.py         SQLAlchemy engine/session setup
    - models.py           ORM models                (Part 2)
    - schemas.py           Pydantic schemas           (Part 2)
    - crud.py              Database access layer      (Part 2)
    - routers/             API route definitions      (Part 2/3)
    - services/            Business logic layer       (Part 2)
    - utils/                Helpers, logging, validators (Part 3)
    - middleware/           Custom middleware          (Part 3)
"""

__version__ = "1.0.0"
