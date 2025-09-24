import os
import json
import argparse
import google.generativeai as genai

# Konfigurasi API Key dari environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY secret not found!")
genai.configure(api_key=api_key)

def read_json_file(file_path):
    """Membaca file JSON dan mengembalikan isinya, atau None jika gagal."""
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None
    return None

def main():
    parser = argparse.ArgumentParser(description="Analyze security reports with an LLM.")
    parser.add_argument("--gitleaks", help="Path to Gitleaks report JSON")
    parser.add_argument("--bandit", help="Path to Bandit report JSON")
    parser.add_argument("--trivy", help="Path to Trivy container report JSON")
    # Tambahkan argumen untuk laporan lain di sini
    args = parser.parse_args()

    # Baca semua laporan
    gitleaks_data = read_json_file(args.gitleaks)
    bandit_data = read_json_file(args.bandit)
    trivy_data = read_json_file(args.trivy)

    # Buat prompt yang sangat deskriptif untuk LLM
    prompt = """
    Anda adalah seorang ahli DevSecOps senior. Tugas Anda adalah menganalisis hasil pemindaian keamanan dari beberapa alat.
    Berikan ringkasan eksekutif, identifikasi 3 risiko paling kritis, dan berikan rekomendasi perbaikan kode yang spesifik untuk setiap temuan kritis.
    Gunakan format Markdown.

    Berikut adalah data laporannya:
    """

    if gitleaks_data:
        prompt += f"\n\n--- Gitleaks Secret Scan ---\nTemuan: {json.dumps(gitleaks_data, indent=2)}"
    if bandit_data and bandit_data.get("results"):
        prompt += f"\n\n--- Bandit SAST Scan ---\nTemuan: {json.dumps(bandit_data['results'], indent=2)}"
    if trivy_data and trivy_data.get("Results"):
        prompt += f"\n\n--- Trivy Container Scan ---\nTemuan: {json.dumps(trivy_data['Results'], indent=2)}"
    
    if not gitleaks_data and not (bandit_data and bandit_data.get("results")) and not (trivy_data and trivy_data.get("Results")):
        print("Tidak ada temuan keamanan yang signifikan. Kerja bagus! ✅")
        return

    # Kirim prompt ke Gemini API
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    # Cetak respons dari AI ke stdout agar bisa ditangkap oleh GitHub Actions
    print(response.text)

if __name__ == "__main__":
    main()