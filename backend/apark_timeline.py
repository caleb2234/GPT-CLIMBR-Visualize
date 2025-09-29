from hf_ehr.config import Event
from typing import List, Dict
patient2: List[Event] = [
    # 1990-05-10 - Condition: Hypertension
    Event(
        code='SNOMED/38341003',
        value='Hypertension',
        unit=None,
        start='1990-05-10T00:00:00.000Z',
        end=None,
        omop_table='condition_occurrence'
    ),
    
    # 1995-01-01 - Drug exposure: Hydrochlorothiazide
    Event(
        code='RxNorm/310798',
        value='Hydrochlorothiazide 25 MG Oral Tablet',
        unit=None,
        start='1995-01-01T00:00:00.000Z',
        end=None,
        omop_table='drug_exposure'
    ),
    
    # 2025-09-18 10:00 - Observation: Palpitations
    Event(
        code='SNOMED/80313002',
        value='Palpitations',
        unit=None,
        start='2025-09-18T10:00:00.000Z',
        end=None,
        omop_table='observation'
    ),
    
    # 2025-09-18 10:00 - Observation: Irregular heart beat
    Event(
        code='SNOMED/102594003',
        value='Irregular heart beat',
        unit=None,
        start='2025-09-18T10:00:00.000Z',
        end=None,
        omop_table='observation'
    ),
    
    # 2025-09-18 10:00 - Observation: Never smoked tobacco
    Event(
        code='SNOMED/702979003',
        value='Never smoked tobacco',
        unit=None,
        start='2025-09-18T10:00:00.000Z',
        end=None,
        omop_table='observation'
    ),
    
    # 2025-09-18 10:00 - Observation: No alcohol intake
    Event(
        code='SNOMED/105542008',
        value='No alcohol intake',
        unit=None,
        start='2025-09-18T10:00:00.000Z',
        end=None,
        omop_table='observation'
    ),
    
    # 2025-09-18 10:00 - Observation: Caffeine intake
    Event(
        code='SNOMED/1208604004',
        value='Caffeine intake',
        unit=None,
        start='2025-09-18T10:00:00.000Z',
        end=None,
        omop_table='observation'
    ),
    
    # 2025-09-18 10:15 - Measurement: Heart rate
    Event(
        code='LOINC/8867-4',
        value=105.0,
        unit='bpm',
        start='2025-09-18T10:15:00.000Z',
        end=None,
        omop_table='measurement'
    ),
    
    # 2025-09-18 10:15 - Measurement: Systolic blood pressure
    Event(
        code='LOINC/8480-6',
        value=148.0,
        unit='mmHg',
        start='2025-09-18T10:15:00.000Z',
        end=None,
        omop_table='measurement'
    ),
    
    # 2025-09-18 10:15 - Measurement: Diastolic blood pressure
    Event(
        code='LOINC/8462-4',
        value=92.0,
        unit='mmHg',
        start='2025-09-18T10:15:00.000Z',
        end=None,
        omop_table='measurement'
    ),
    
    # 2025-09-18 10:15 - Measurement: Body temperature
    Event(
        code='LOINC/8310-5',
        value=98.6,
        unit='F',
        start='2025-09-18T10:15:00.000Z',
        end=None,
        omop_table='measurement'
    ),
    # Event(
    #     code='CPT4/93010',
    #     value='ECG',
    #     unit=None,
    #     start='2025-09-18T10:15:00.000Z',
    #     end=None,
    #     omop_table='measurement'
    # )
]