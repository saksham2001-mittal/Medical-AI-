
import json
from pathlib import Path

from backend.database import SessionLocal
from backend.database.models import Patient
from backend.history.history_builder import PatientHistoryService


def get_latest_patient(db):
    """
    Get the most recently created patient.
    """

    return (
        db.query(Patient)
        .order_by(Patient.patient_id.desc())
        .first()
    )


def main():

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Get the latest patient
        # ---------------------------------------------------------

        patient = get_latest_patient(db)

        if patient is None:
            print("No patients found in the database.")
            return

        print("=" * 70)
        print("LATEST PATIENT")
        print("=" * 70)

        print(f"Patient Name : {patient.patient_name}")
        print(f"Patient ID   : {patient.patient_id}")

        # ---------------------------------------------------------
        # 2. Build complete patient history
        # ---------------------------------------------------------

        service = PatientHistoryService(db)

        result = service.build(patient.patient_id)

        # ---------------------------------------------------------
        # 3. Get clinical insights
        # ---------------------------------------------------------

        clinical_insights = result.get("clinical_insights", {})

        print("\n" + "=" * 70)
        print("CLINICAL INSIGHTS")
        print("=" * 70)

        clinical_insights_json = json.dumps(
            clinical_insights,
            indent=4,
            default=str
        )

        print(clinical_insights_json)

        # ---------------------------------------------------------
        # 4. Display complete patient history
        # ---------------------------------------------------------

        print("\n" + "=" * 70)
        print("COMPLETE PATIENT HISTORY")
        print("=" * 70)

        complete_history= json.dumps(
                result,
                indent=4,
                default=str
            )

        # output_file = Path("complete history.txt")
        
        # output_file.write_text(
        #             complete_history,
        #             encoding="utf-8"
        #         )
        
        # print(f"\nComplete patient history saved to: {output_file.resolve()}")

    except Exception as e:

        print("\nError while building patient history:")
        print(str(e))

        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
