# database/models.py
from datetime import datetime, date
from sqlalchemy import Integer, String, Date, DateTime, Column
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_date = Column(Date, nullable=False, default=date.today)
    reference_no = Column(String(100), nullable=True)        # new
    name = Column(String(200), nullable=False, index=True)
    search_name = Column(String(400), nullable=False, index=True)  # normalized lower-case for prefix search
    referred_by = Column(String(200), nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(String(64), nullable=True)
    diet = Column(String(32), nullable=True)
    marital_status = Column(String(64), nullable=True)
    religion = Column(String(100), nullable=True)
    occupation = Column(String(200), nullable=True)
    address = Column(String(1000), nullable=True)
    contact_number = Column(String(64), nullable=True)
    whatsapp_number = Column(String(64), nullable=True)     # new
    email = Column(String(200), nullable=True)               # new
    num_children = Column(Integer, nullable=True)            # new
    num_male_children = Column(Integer, nullable=True)       # new
    num_female_children = Column(Integer, nullable=True)     # new
    children_ages = Column(String(200), nullable=True)       # new (comma-separated ages)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Patient id={self.id} name={self.name!r}>"
