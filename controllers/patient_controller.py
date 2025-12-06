# controllers/patient_controller.py
from database.database import SessionLocal, db_exists, create_db
from database.models import Patient
from sqlalchemy import select
from typing import List
from utils.normalize import normalize_name
from datetime import date as pydate

def ensure_db(base=None):
    """Create DB if missing. Optionally pass base to create tables."""
    if not db_exists() and base is not None:
        create_db(base)

def add_patient(
    name: str,
    visit_date: pydate | None = None,
    reference_no: str | None = None,
    referred_by: str | None = None,
    age: int | None = None,
    sex: str | None = None,
    diet: str | None = None,
    marital_status: str | None = None,
    religion: str | None = None,
    occupation: str | None = None,
    address: str | None = None,
    contact_number: str | None = None,
    whatsapp_number: str | None = None,
    email: str | None = None,
    num_children: int | None = None,
    num_male_children: int | None = None,
    num_female_children: int | None = None,
    children_ages: str | None = None,
) -> Patient:
    if not db_exists():
        raise RuntimeError("database-not-found")
    with SessionLocal() as session:
        visit_date = visit_date or pydate.today()
        patient = Patient(
            name=name.strip(),
            search_name=normalize_name(name),
            visit_date=visit_date,
            reference_no=(reference_no.strip() if reference_no else None),
            referred_by=(referred_by.strip() if referred_by else None),
            age=age,
            sex=(sex.strip() if sex else None),
            diet=(diet.strip() if diet else None),
            marital_status=(marital_status.strip() if marital_status else None),
            religion=(religion.strip() if religion else None),
            occupation=(occupation.strip() if occupation else None),
            address=(address.strip() if address else None),
            contact_number=(contact_number.strip() if contact_number else None),
            whatsapp_number=(whatsapp_number.strip() if whatsapp_number else None),
            email=(email.strip() if email else None),
            num_children=(num_children if num_children is not None else None),
            num_male_children=(num_male_children if num_male_children is not None else None),
            num_female_children=(num_female_children if num_female_children is not None else None),
            children_ages=(children_ages.strip() if children_ages else None),
        )
        session.add(patient)
        session.commit()
        session.refresh(patient)
        return patient

def get_all_patients(limit: int | None = None) -> List[Patient]:
    if not db_exists():
        raise RuntimeError("database-not-found")
    with SessionLocal() as s:
        stmt = select(Patient).order_by(Patient.name)
        if limit:
            stmt = stmt.limit(limit)
        return s.execute(stmt).scalars().all()

def search_by_prefix(q: str, limit: int = 100) -> List[Patient]:
    """
    Prefix search using normalized search_name stored in DB.
    """
    if not db_exists():
        raise RuntimeError("database-not-found")
    nq = normalize_name(q)
    if not nq:
        return []
    with SessionLocal() as s:
        stmt = select(Patient).where(Patient.search_name.like(f"{nq}%")).limit(limit)
        return s.execute(stmt).scalars().all()

def get_patient_by_id(pk: int) -> Patient | None:
    if not db_exists():
        raise RuntimeError("database-not-found")
    with SessionLocal() as s:
        return s.get(Patient, pk)
