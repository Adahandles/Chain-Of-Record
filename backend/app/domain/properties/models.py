# Property domain models
from sqlalchemy import Column, BigInteger, String, Text, DateTime, Numeric, Date, Index, func
from app.core.db import Base


class Property(Base):
    """
    Property model for real estate parcels from county property appraiser data.
    """
    __tablename__ = "properties"

    id = Column(BigInteger, primary_key=True, index=True)
    parcel_id = Column(String, nullable=False, index=True)  # County parcel identifier
    county = Column(String, nullable=False, index=True)     # County name
    jurisdiction = Column(String, index=True)               # State/jurisdiction (e.g., 'FL')
    situs_address_id = Column(BigInteger, index=True)       # FK to addresses table
    appraiser_url = Column(Text)                           # Link to county appraiser page
    land_use_code = Column(String, index=True)             # Property use classification
    acreage = Column(Numeric(10, 4))                       # Property size in acres
    last_sale_date = Column(Date)                          # Most recent sale date
    last_sale_price = Column(Numeric(12, 2))               # Most recent sale price
    market_value = Column(Numeric(12, 2))                  # Current assessed market value
    assessed_value = Column(Numeric(12, 2))                # Current assessed value for taxes
    homestead_exempt = Column(String)                      # Homestead exemption status
    tax_year = Column(String)                              # Most recent tax year
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_property_county_parcel', 'county', 'parcel_id'),
        Index('idx_property_land_use', 'county', 'land_use_code'),
        Index('idx_property_sale_date', 'last_sale_date'),
        Index('idx_property_sale_price', 'last_sale_price'),
    )

    def __repr__(self) -> str:
        return f"<Property(id={self.id}, parcel='{self.parcel_id}', county='{self.county}')>"