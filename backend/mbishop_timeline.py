from hf_ehr.config import Event
from typing import List, Dict
patient1: List[Event] = [
    # 2019-06-10 - Drug exposure (Mirena IUD)
    Event(
        code='RxNorm/807283',
        value=None,  # Set to None to match example format
        unit=None,
        start=None,  # Set to None to match example format
        end=None,
        omop_table="drug_exposure"  # Set to None to match example format
    ),
    
    # 2023-04-15 - Drug exposure (Antihistamine)
    Event(
        code='RxNorm/161',
        value=None,
        unit=None,
        start=None,
        end=None,
        omop_table="drug_exposure"
    ),
    
    # 2025-08-23 13:00 - Observation: Dyspnea (shortness of breath)
    Event(
        code='SNOMED/267036007',
        value=None,
        unit=None,
        start=None,
        end=None,
        omop_table='observation'
    ),
    
    # 2025-08-23 13:00 - Condition: Seasonal allergic rhinitis
    Event(
        code='SNOMED/367498001',
        value=None,
        unit=None,
        start=None,
        end=None,
        omop_table='observation'
    ),
    
    # 2025-08-23 13:00 - Observation: Family history of prostate cancer
    Event(
        code='SNOMED/414205003',
        value=None,
        unit=None,
        start=None,
        end=None,
        omop_table='observation'
    ),
    
    # 2025-08-23 13:00 - Observation: No tobacco abuse
    Event(
        code='SNOMED/702979003',
        value=None,
        unit=None,
        start=None,
        end=None,
        omop_table='observation'
    ),
    
    # 2025-08-23 13:00 - Observation: Occasional drinker
    Event(
        code='SNOMED/228276006',
        value=None,
        unit=None,
        start=None,
        end=None,
        omop_table='observation'
    ),
    
    # 2025-08-23 13:15 - Measurement: Hemoglobin level
    Event(
        code='LOINC/718-7',
        value=125.0,
        unit='g/L',
        start=None,
        end=None,
        omop_table="measurement"
    ),
    
    # 2025-08-23 13:15 - Measurement: Heart rate
    Event(
        code='LOINC/8867-4',
        value=85.0,
        unit='bpm',
        start=None,
        end=None,
        omop_table="measurement"
    ),
    
    # 2025-08-23 13:15 - Measurement: Systolic blood pressure
    Event(
        code='LOINC/8480-6',
        value=118.0,
        unit='mmHg',
        start=None,
        end=None,
        omop_table="measurement"
    ),
    
    # 2025-08-23 13:15 - Measurement: Diastolic blood pressure
    Event(
        code='LOINC/8462-4',
        value=72.0,
        unit='mmHg',
        start=None,
        end=None,
        omop_table="measurement"
    ),
    
    # 2025-08-23 13:15 - Measurement: Body temperature
    Event(
        code='LOINC/8310-5',
        value=98.0,
        unit='F',
        start=None,
        end=None,
        omop_table="measurement"
    )
]