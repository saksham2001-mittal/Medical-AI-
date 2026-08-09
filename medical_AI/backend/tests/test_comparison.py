from backend.database import SessionLocal
from backend.database.models import Patient
from backend.history.history_builder import PatientHistoryService
from backend.qa.comparison_engine import ComparisonEngine


def main():

    db = SessionLocal()

    try:

        patient = (
            db.query(Patient)
            .order_by(
                Patient.patient_id.desc()
            )
            .first()
        )

        if patient is None:
            print("No patient found.")
            return

        history_service = PatientHistoryService(db)

        patient_history = history_service.build(
            patient.patient_id
        )

        reports = patient_history["reports"]

        engine = ComparisonEngine()
        test_name="Vitamin D Total-25 Hydroxy"
        print("\n" + "=" * 70)
        print("COMPARISON ENGINE DEBUG")
        print("=" * 70)

        print("Requested test:", test_name)
        print("Number of reports:", len(reports))

        for i, report in enumerate(reports, start=1):

            print(f"\n--- REPORT {i} ---")

            print("Report type:", type(report))
            print("Report date:", report.get("report_date"))

            tests = report.get("tests", [])

            print("Tests count:", len(tests))

            for test in tests:

                print(
                    "TEST:",
                    test.get("test_name"),
                    "| RESULT:",
                    test.get("result")
                )
        result = engine.compare_test(
            reports=reports,
            test_name=test_name,
        )

        print("=" * 70)
        print("COMPARISON ENGINE TEST")
        print("=" * 70)

        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()