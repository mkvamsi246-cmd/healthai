import os
import sys
import unittest
import json
from io import BytesIO
from datetime import datetime

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test environment variables before importing app components
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-testing-purposes-only"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["UPLOAD_DIR"] = "test_uploads"
os.environ["REPORTS_DIR"] = "test_generated_reports"

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.report import Report
from app.models.medical_values import MedicalValues
from app.models.prediction import Prediction
from app.services.ocr_service import ocr_service
from app.services.pdf_service import pdf_service
from app.utils.jwt_utils import get_password_hash

# Create SQLite file-based engine for unit testing
engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply Dependency Override
app.dependency_overrides[get_db] = override_get_db


class TestHealthInsightBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create all tables in SQLite file database
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)
        # Clean up test files if generated
        import shutil
        if os.path.exists("test_uploads"):
            shutil.rmtree("test_uploads")
        if os.path.exists("test_generated_reports"):
            shutil.rmtree("test_generated_reports")
        if os.path.exists("test.db"):
            try:
                os.remove("test.db")
            except Exception:
                pass

    def setUp(self):
        # Insert a default test user
        self.db = TestingSessionLocal()
        self.db.query(User).delete()
        self.db.query(Report).delete()
        self.db.query(MedicalValues).delete()
        self.db.query(Prediction).delete()
        
        self.test_user = User(
            email="patient@test.com",
            hashed_password=get_password_hash("secure123"),
            full_name="John Doe",
            age=45,
            gender="Male"
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)
        self.db.close()

    def get_token(self):
        # Helper to get auth header token
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "patient@test.com", "password": "secure123"}
        )
        data = response.json()
        return data["access_token"]

    def test_01_auth_register_duplicate(self):
        # Try to register same email
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": "patient@test.com",
                "password": "newpassword123",
                "full_name": "Duplicate User",
                "age": 30,
                "gender": "Male"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("exists", response.json()["error"]["message"])

    def test_02_auth_register_success(self):
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": "new_patient@test.com",
                "password": "password321",
                "full_name": "Jane Smith",
                "age": 28,
                "gender": "Female"
            }
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["email"], "new_patient@test.com")
        self.assertEqual(data["full_name"], "Jane Smith")

    def test_03_auth_login_fail(self):
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "patient@test.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 401)

    def test_04_auth_login_success(self):
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "patient@test.com", "password": "secure123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertIn("refresh_token", response.json())

    def test_05_profile_access_protected(self):
        response = self.client.get("/api/v1/auth/profile")
        self.assertEqual(response.status_code, 401)

    def test_06_profile_update(self):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = self.client.put(
            "/api/v1/auth/profile",
            headers=headers,
            json={"full_name": "John Updated", "age": 46}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["full_name"], "John Updated")
        self.assertEqual(data["user"]["age"], 46)

    def test_07_ocr_extract_mock_and_pipeline(self):
        # We mock OCR text extraction to avoid running EasyOCR during unit testing
        original_extract = ocr_service.extract_text
        ocr_service.extract_text = lambda path, ext: """
        Patient Health Report
        Name: John Doe
        Age: 45
        Gender: Male
        Fasting Glucose: 110 mg/dL
        HbA1c: 6.2 %
        Blood Pressure: 135/85 mmHg
        Heart Rate: 72 bpm
        SpO2: 98 %
        HDL: 45 mg/dL
        LDL: 140 mg/dL
        Triglycerides: 160 mg/dL
        Total Cholesterol: 217 mg/dL
        Creatinine: 0.9 mg/dL
        Hemoglobin: 14.5 g/dL
        Weight: 80.0 kg
        BMI: 26.5
        """
        
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make a mock PDF file upload
        pdf_bytes = b"%PDF-1.4 test pdf content mock"
        response = self.client.post(
            "/api/v1/reports/analyze",
            headers=headers,
            files={"file": ("report.pdf", pdf_bytes, "application/pdf")}
        )
        
        # Reset OCR service
        ocr_service.extract_text = original_extract
        
        self.assertEqual(response.status_code, 201)
        res_data = response.json()
        self.assertTrue(res_data["success"])
        report = res_data["report"]
        self.assertEqual(report["status"], "COMPLETED")
        self.assertEqual(report["file_type"], "PDF")
        
        # Verify clinical extraction
        mv = report["medical_values"]
        self.assertEqual(mv["blood_sugar"], 110.0)
        self.assertEqual(mv["hba1c"], 6.2)
        self.assertEqual(mv["systolic_bp"], 135)
        self.assertEqual(mv["diastolic_bp"], 85)
        self.assertEqual(mv["ldl"], 140.0)
        
        # Verify predictions
        pred = report["prediction"]
        self.assertIn(pred["diabetes_risk"], ["HIGH", "BORDERLINE"]) # Allow both heuristic (HIGH) and model (BORDERLINE) classifications
        self.assertIn(pred["heart_disease_risk"], ["LOW", "BORDERLINE"]) # Allow both model (LOW) and heuristic (BORDERLINE) classifications
        self.assertLess(pred["health_score"], 100)

    def test_08_compare_reports(self):
        # Setup two reports manually in SQLite database to compare
        db = TestingSessionLocal()
        user = db.query(User).filter(User.email == "patient@test.com").first()
        
        # Baseline report (older)
        r1 = Report(user_id=user.id, file_name="rep1.pdf", file_path="test_rep1.pdf", file_type="PDF", file_size=100, status="COMPLETED")
        db.add(r1)
        db.commit()
        
        mv1 = MedicalValues(
            report_id=r1.id, user_id=user.id, age=45, gender="Male",
            blood_sugar=140.0, hba1c=7.0, systolic_bp=145, diastolic_bp=95,
            heart_rate=80, spo2=95.0, hdl=35.0, ldl=160.0, weight=85.0, bmi=28.0
        )
        pred1 = Prediction(
            report_id=r1.id, user_id=user.id, heart_disease_risk="HIGH",
            diabetes_risk="HIGH", kidney_disease_risk="LOW", stroke_risk="HIGH", health_score=60
        )
        db.add(mv1)
        db.add(pred1)
        
        # Current report (newer - improved parameters)
        r2 = Report(user_id=user.id, file_name="rep2.pdf", file_path="test_rep2.pdf", file_type="PDF", file_size=100, status="COMPLETED")
        db.add(r2)
        db.commit()
        
        mv2 = MedicalValues(
            report_id=r2.id, user_id=user.id, age=45, gender="Male",
            blood_sugar=105.0, hba1c=5.9, systolic_bp=125, diastolic_bp=82,
            heart_rate=72, spo2=98.0, hdl=45.0, ldl=120.0, weight=78.0, bmi=25.0
        )
        pred2 = Prediction(
            report_id=r2.id, user_id=user.id, heart_disease_risk="BORDERLINE",
            diabetes_risk="BORDERLINE", kidney_disease_risk="LOW", stroke_risk="BORDERLINE", health_score=85
        )
        db.add(mv2)
        db.add(pred2)
        db.commit()
        r1_id = r1.id
        r2_id = r2.id
        db.close()
        
        # Run API Comparison
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = self.client.post(
            "/api/v1/reports/compare",
            headers=headers,
            json={
                "base_report_id": r1_id,
                "compare_report_id": r2_id
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        comp = data["comparison"]
        self.assertEqual(comp["base_report_id"], r1.id)
        self.assertEqual(comp["compare_report_id"], r2.id)
        self.assertGreater(comp["overall_improvement_percentage"], 0.0)
        
        # Check specific parameter comparisons
        comp_data = comp["comparison_data"]
        self.assertEqual(comp_data["blood_sugar"]["status"], "Improved") # 140 -> 105 is improved
        self.assertEqual(comp_data["hdl"]["status"], "Improved") # 35 -> 45 (higher HDL is better)
        self.assertEqual(comp_data["weight"]["status"], "Improved") # 85 -> 78 is improved
        
        # Verify AI summary generated mentions improvement
        self.assertIn("improvement", comp["ai_summary"].lower())

    def test_09_dashboard_api(self):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        response = self.client.get("/api/v1/dashboard", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        
        summary = data["data"]
        self.assertIn("current_health_score", summary)
        self.assertIn("health_trends", summary)
        self.assertIn("recent_reports", summary)
        self.assertIn("comparison_history", summary)

    def test_10_download_pdf_report_fail_not_found(self):
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/v1/reports/9999/download", headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_11_generate_pdf_canvas_bytes(self):
        # Set up test objects
        db = TestingSessionLocal()
        user = db.query(User).filter(User.email == "patient@test.com").first()
        r = Report(user_id=user.id, file_name="pdf_test.pdf", file_path="test_pdf.pdf", file_type="PDF", file_size=100, status="COMPLETED")
        db.add(r)
        db.commit()
        
        mv = MedicalValues(
            report_id=r.id, user_id=user.id, age=45, gender="Male",
            blood_sugar=110.0, hba1c=6.0, systolic_bp=130, diastolic_bp=85,
            heart_rate=75, spo2=98.0, hdl=45.0, ldl=130.0, weight=80.0, bmi=26.5
        )
        pred = Prediction(
            report_id=r.id, user_id=user.id, heart_disease_risk="BORDERLINE",
            diabetes_risk="BORDERLINE", kidney_disease_risk="LOW", stroke_risk="BORDERLINE", health_score=75
        )
        db.add(mv)
        db.add(pred)
        db.commit()
        
        # Test ReportLab PDF generation bytes
        pdf_bytes = pdf_service.generate_report_pdf(user, r)
        db.close()
        
        self.assertGreater(len(pdf_bytes), 0)
        # Verify first 4 bytes of PDF matches "%PDF"
        self.assertEqual(pdf_bytes[:4], b"%PDF")


if __name__ == "__main__":
    unittest.main()
