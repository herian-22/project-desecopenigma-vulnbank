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
        if file_path and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None
    return None

# --- FUNGSI BARU UNTUK MERINGKAS LAPORAN ---

def summarize_trivy(data, report_type="Container"):
    """Meringkas laporan Trivy, hanya mengambil temuan CRITICAL dan HIGH."""
    if not data or not data.get("Results"):
        return ""
    summary = f"\n\n--- Trivy {report_type} Scan Summary ---\n"
    findings_found = False
    for result in data["Results"]:
        target = result.get("Target")
        vulnerabilities = result.get("Vulnerabilities", [])
        high_critical = [v for v in vulnerabilities if v.get("Severity") in ["CRITICAL", "HIGH"]]
        if high_critical:
            findings_found = True
            summary += f"Target: {target}\n"
            for v in high_critical:
                summary += f"- ID: {v.get('VulnerabilityID')}, Severity: {v.get('Severity')}, Package: {v.get('PkgName')}\n"
    return summary if findings_found else ""

def summarize_bandit(data):
    """Meringkas laporan Bandit, hanya mengambil temuan HIGH confidence/severity."""
    if not data or not data.get("results"):
        return ""
    summary = "\n\n--- Bandit SAST Scan Summary ---\n"
    high_impact = [r for r in data["results"] if r.get("issue_severity") == "HIGH" or r.get("issue_confidence") == "HIGH"]
    if not high_impact:
        return ""
    for r in high_impact:
        summary += f"- Issue: {r.get('issue_text')}, File: {r.get('filename')}, Line: {r.get('line_number')}\n"
    return summary
    
def summarize_simple_list(data, tool_name):
    """Meringkas laporan sederhana berbentuk list seperti Gitleaks."""
    if not data or not isinstance(data, list):
        return ""
    summary = f"\n\n--- {tool_name} Scan Summary ---\n"
    for finding in data:
         summary += f"- Description: {finding.get('Description')}, File: {finding.get('File')}, Secret: {finding.get('Secret')[:10]}...\n"
    return summary

def main():
    parser = argparse.ArgumentParser(description="Analyze security reports with an LLM.")
    parser.add_argument("--gitleaks", help="Path to Gitleaks report JSON")
    parser.add_argument("--bandit", help="Path to Bandit report JSON")
    parser.add_argument("--trivy", help="Path to Trivy container report JSON")
    parser.add_argument("--misconfig", help="Path to Trivy misconfiguration report JSON")
    parser.add_argument("--dast", help="Path to ZAP DAST report JSON")
    args = parser.parse_args()

    # --- MEMBUAT PROMPT DARI RINGKASAN, BUKAN DATA MENTAH ---
    
    prompt = """
    Anda adalah seorang ahli DevSecOps senior. Analisis ringkasan temuan keamanan berikut.
    Berikan ringkasan eksekutif, identifikasi 3 risiko paling kritis, dan berikan rekomendasi perbaikan spesifik untuk setiap risiko tersebut.
    Gunakan format Markdown yang jelas.

    Berikut adalah ringkasan temuannya:
    """
    
    # Baca dan ringkas setiap laporan
    gitleaks_data = read_json_file(args.gitleaks)
    prompt += summarize_simple_list(gitleaks_data, "Gitleaks Secret")

    bandit_data = read_json_file(args.bandit)
    prompt += summarize_bandit(bandit_data)

    trivy_data = read_json_file(args.trivy)
    prompt += summarize_trivy(trivy_data, "Container")

    misconfig_data = read_json_file(args.misconfig)
    prompt += summarize_trivy(misconfig_data, "Misconfiguration") # Formatnya mirip Trivy

    # Jika tidak ada temuan sama sekali setelah diringkas
    if len(prompt.strip()) < 250:
        print("Tidak ada temuan keamanan dengan tingkat keparahan tinggi. Kerja bagus! ✅")
        return

    # Kirim prompt yang JAUH LEBIH KECIL ke Gemini API
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)

    print(response.text)

if __name__ == "__main__":
    main()