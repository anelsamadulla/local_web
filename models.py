"""
SQLAlchemy Models of the app.
"""
from sqlalchemy.orm import mapped_column, Mapped

from database import db


class TenantProfile(db.Model):
    __tablename__ = 'tenant_profiles'
    
    id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    

class Tenant(db.Model):
    __tablename__ = 'tenants'
    
    id: Mapped[str] = mapped_column(primary_key=True, unique=True)


class TenantAdmin(db.Model):
    __tablename__ = 'tenant_admins'
    
    id: Mapped[str] = mapped_column(primary_key=True, unique=True)