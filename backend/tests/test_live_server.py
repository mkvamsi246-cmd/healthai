import os
import sys
import time
import requests
from io import BytesIO

BASE_URL = "http://127.0.0.1:8000"

def test_live_pipeline():
    print("==================================================")
    print("STARTING END-TO-END LIVE BACKEND DIAGNOSTICS")
    print("==================================================")
    
    # 1. Test health check
    try:
        health_resp = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Health Check Status: {health_resp.status_code}")
        print(f"Health Check Response: {health_resp.json()}")
        if health_resp.status_code != 200:
            print("ERROR: Health check failed. Make sure server is running.")
            return
    except Exception as e:
        print(f"ERROR: Could not connect to server at {BASE_URL}: {e}")
        return

    # 2. Register test user
    email = f"live_test_{int(time.time())}@health.com"
    reg_payload = {
        "email": email,
        "password": "SecurePassword123",
        "full_name": "Diagnostic Tester",
        "age": 42,
        "gender": "Male"
    }
    reg_resp = requests.post(f"{BASE_URL}/api/v1/auth/register", json=reg_payload)
    print(f"\nUser Registration Status: {reg_resp.status_code}")
    print(f"User Registration Response: {reg_resp.json()}")
    if reg_resp.status_code != 201:
        print("ERROR: Registration failed.")
        return

    # 3. Login
    login_payload = {
        "email": email,
        "password": "SecurePassword123"
    }
    login_resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_payload)
    print(f"\nUser Login Status: {login_resp.status_code}")
    token_data = login_resp.json()
    token = token_data.get("access_token")
    print(f"Access Token Retrieved: {token[:25]}...")
    
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Upload Report 1 (Elevated Baseline)
    # We create mock report text. Since our ocr_service uses pdfplumber for digital PDFs, 
    # we can generate a simple text PDF using reportlab or we can write a text file or image.
    # Wait, let's write a simple image using Pillow since Pillow doesn't require complex layout, 
    # or just write a basic reportlab PDF! Since we have reportlab installed, we can generate a real PDF!
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    print("\nGenerating baseline PDF file (elevated biomarkers)...")
    pdf_buffer1 = BytesIO()
    doc1 = SimpleDocTemplate(pdf_buffer1, pagesize=letter)
    styles = getSampleStyleSheet()
    story1 = [
        Paragraph("Patient Medical Baseline Assessment", styles["Heading1"]),
        Spacer(1, 10),
        Paragraph("Patient: Diagnostic Tester", styles["Normal"]),
        Paragraph("Age: 42 Years   Gender: Male", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("Fasting Glucose: 135 mg/dL", styles["Normal"]),
        Paragraph("HbA1c: 6.8 %", styles["Normal"]),
        Paragraph("Blood Pressure: 145/95 mmHg", styles["Normal"]),
        Paragraph("Heart Rate: 82 bpm", styles["Normal"]),
        Paragraph("SpO2: 95 %", styles["Normal"]),
        Paragraph("HDL: 32 mg/dL", styles["Normal"]),
        Paragraph("LDL: 165 mg/dL", styles["Normal"]),
        Paragraph("Triglycerides: 240 mg/dL", styles["Normal"]),
        Paragraph("Creatinine: 1.4 mg/dL", styles["Normal"]),
        Paragraph("Hemoglobin: 11.2 g/dL", styles["Normal"]),
        Paragraph("Weight: 88.5 kg", styles["Normal"]),
        Paragraph("BMI: 29.5", styles["Normal"]),
    ]
    doc1.build(story1)
    pdf_bytes1 = pdf_buffer1.getvalue()
    
    print("Uploading baseline PDF to /api/v1/reports/analyze...")
    upload_resp1 = requests.post(
        f"{BASE_URL}/api/v1/reports/analyze",
        headers=headers,
        files={"file": ("baseline_report.pdf", pdf_bytes1, "application/pdf")}
    )
    print(f"Upload 1 Status: {upload_resp1.status_code}")
    report1_data = upload_resp1.json()
    if upload_resp1.status_code != 201:
        print(f"ERROR: Upload 1 failed: {report1_data}")
        return
        
    report1_id = report1_data["report"]["id"]
    pred1 = report1_data["report"]["prediction"]
    mv1 = report1_data["report"]["medical_values"]
    print(f"Report 1 ID: {report1_id}")
    print(f"Report 1 Health Score: {pred1['health_score']}")
    print(f"Report 1 Risks: Diabetes={pred1['diabetes_risk']}, Heart={pred1['heart_disease_risk']}, Kidney={pred1['kidney_disease_risk']}")

    # 5. Upload Report 2 (Improved Vitals)
    print("\nGenerating improved follow-up PDF file...")
    pdf_buffer2 = BytesIO()
    doc2 = SimpleDocTemplate(pdf_buffer2, pagesize=letter)
    story2 = [
        Paragraph("Patient Medical Followup Assessment", styles["Heading1"]),
        Spacer(1, 10),
        Paragraph("Patient: Diagnostic Tester", styles["Normal"]),
        Paragraph("Age: 42 Years   Gender: Male", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("Fasting Glucose: 92 mg/dL", styles["Normal"]),
        Paragraph("HbA1c: 5.2 %", styles["Normal"]),
        Paragraph("Blood Pressure: 118/78 mmHg", styles["Normal"]),
        Paragraph("Heart Rate: 70 bpm", styles["Normal"]),
        Paragraph("SpO2: 99 %", styles["Normal"]),
        Paragraph("HDL: 52 mg/dL", styles["Normal"]),
        Paragraph("LDL: 95 mg/dL", styles["Normal"]),
        Paragraph("Triglycerides: 115 mg/dL", styles["Normal"]),
        Paragraph("Creatinine: 0.85 mg/dL", styles["Normal"]),
        Paragraph("Hemoglobin: 14.8 g/dL", styles["Normal"]),
        Paragraph("Weight: 76.2 kg", styles["Normal"]),
        Paragraph("BMI: 24.3", styles["Normal"]),
    ]
    doc2.build(story2)
    pdf_bytes2 = pdf_buffer2.getvalue()
    
    print("Uploading follow-up PDF to /api/v1/reports/analyze...")
    upload_resp2 = requests.post(
        f"{BASE_URL}/api/v1/reports/analyze",
        headers=headers,
        files={"file": ("followup_report.pdf", pdf_bytes2, "application/pdf")}
    )
    print(f"Upload 2 Status: {upload_resp2.status_code}")
    report2_data = upload_resp2.json()
    if upload_resp2.status_code != 201:
        print(f"ERROR: Upload 2 failed: {report2_data}")
        return
        
    report2_id = report2_data["report"]["id"]
    pred2 = report2_data["report"]["prediction"]
    print(f"Report 2 ID: {report2_id}")
    print(f"Report 2 Health Score: {pred2['health_score']}")
    print(f"Report 2 Risks: Diabetes={pred2['diabetes_risk']}, Heart={pred2['heart_disease_risk']}, Kidney={pred2['kidney_disease_risk']}")

    # 6. Compare Reports
    print("\nComparing Report 1 vs Report 2...")
    compare_payload = {
        "base_report_id": report1_id,
        "compare_report_id": report2_id
    }
    compare_resp = requests.post(
        f"{BASE_URL}/api/v1/reports/compare",
        headers=headers,
        json=compare_payload
    )
    print(f"Comparison Status: {compare_resp.status_code}")
    comp_data = compare_resp.json()
    comparison = comp_data["comparison"]
    print(f"Overall Improvement Score: {comparison['overall_improvement_percentage']}%")
    print(f"AI Comparison Summary: {comparison['ai_summary']}")

    # 7. Query Dashboard
    print("\nFetching user dashboard analytics...")
    dash_resp = requests.get(f"{BASE_URL}/api/v1/dashboard", headers=headers)
    print(f"Dashboard Status: {dash_resp.status_code}")
    dash_data = dash_resp.json()["data"]
    print(f"Dashboard Health Score: {dash_data['current_health_score']}")
    print(f"History reports count: {len(dash_data['recent_reports'])}")
    print(f"Trends data points count: {len(dash_data['health_trends'])}")

    # 8. Download generated clinical PDF report
    print(f"\nDownloading finalized PDF report for ID {report2_id}...")
    pdf_resp = requests.get(f"{BASE_URL}/api/v1/reports/{report2_id}/download", headers=headers)
    print(f"PDF Download Status: {pdf_resp.status_code}")
    print(f"Response Content Type: {pdf_resp.headers.get('Content-Type')}")
    pdf_bytes = pdf_resp.content
    print(f"Downloaded PDF Bytes size: {len(pdf_bytes)} bytes")
    if pdf_bytes[:4] == b"%PDF":
        print("SUCCESS: Downloaded file is a valid PDF document!")
    else:
        print("ERROR: Downloaded file headers do not match %PDF.")
        return

    print("\n==================================================")
    print("ALL LIVE END-TO-END PIPELINES VERIFIED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_live_pipeline()
