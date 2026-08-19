"""Bulk CSV import tests (partial-success isolation, RBAC)."""
import io


def _csv_file(content: str, filename: str = "import.csv"):
    return {"file": (filename, io.BytesIO(content.encode()), "text/csv")}


def test_employee_import_partial_success(client, admin_headers):
    csv_content = (
        "first_name,last_name,email\n"
        "Alice,Import,alice.csvtest@ams-platform.com\n"
        ",MissingFirstName,missing.first@ams-platform.com\n"
        "Bob,Import,bob.csvtest@ams-platform.com\n"
    )
    response = client.post(
        "/api/v1/employees/import", files=_csv_file(csv_content), headers=admin_headers
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["created"] == 2
    assert body["skipped"] == 1
    assert body["errors"][0]["row"] == 3  # header is row 1, blank-first-name row is row 3


def test_employee_import_duplicate_email_in_same_batch(client, admin_headers):
    csv_content = (
        "first_name,last_name,email\n"
        "First,Copy,dup.csvtest@ams-platform.com\n"
        "Second,Copy,dup.csvtest@ams-platform.com\n"
    )
    response = client.post(
        "/api/v1/employees/import", files=_csv_file(csv_content), headers=admin_headers
    )
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 1
    assert "already exists" in body["errors"][0]["message"]
    # The critical assertion: no raw SQL/parameter dump leaked into the message.
    assert "INSERT INTO" not in body["errors"][0]["message"]


def test_employee_import_requires_admin_or_hr(client, it_headers):
    csv_content = "first_name,last_name,email\nA,B,ab@ams-platform.com\n"
    response = client.post(
        "/api/v1/employees/import", files=_csv_file(csv_content), headers=it_headers
    )
    assert response.status_code == 403


def test_asset_import_partial_success(client, admin_headers, sample_asset_type):
    csv_content = (
        "asset_type_id,manufacturer,serial_number\n"
        f"{sample_asset_type['id']},Dell,SN-CSVTEST-001\n"
        ",NoType,SN-CSVTEST-002\n"
    )
    response = client.post(
        "/api/v1/assets/import", files=_csv_file(csv_content), headers=admin_headers
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 1


def test_asset_import_duplicate_serial_clean_message(client, admin_headers, sample_asset_type):
    csv_content = (
        "asset_type_id,serial_number\n"
        f"{sample_asset_type['id']},SN-CSVDUP-001\n"
        f"{sample_asset_type['id']},SN-CSVDUP-001\n"
    )
    response = client.post(
        "/api/v1/assets/import", files=_csv_file(csv_content), headers=admin_headers
    )
    body = response.json()
    assert body["created"] == 1
    assert body["skipped"] == 1
    assert "already exists" in body["errors"][0]["message"]
    assert "INSERT INTO" not in body["errors"][0]["message"]
