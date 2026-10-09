import argparse
import sys
import os

# Ensure safe output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from engine import AutoTailorEngine

def main():
    parser = argparse.ArgumentParser(description="Auto-Tailor Engine for Abderrahmane El Idrissi Slimani")
    parser.add_argument("--job", "-j", help="Path to job description text file or raw job text", required=False)
    parser.add_argument("--company", "-c", help="Target Company name", default="")
    parser.add_argument("--role", "-r", help="Target Job Title", default="")
    parser.add_argument("--lang", "-l", help="Language: auto, fr, or en", default="auto")
    parser.add_argument("--output-dir", "-o", help="Directory to save generated CV & Cover Letter", default="output")

    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(base_dir, "profile_data.json")
    engine = AutoTailorEngine(profile_path)

    job_text = ""
    if args.job:
        if os.path.exists(args.job):
            with open(args.job, "r", encoding="utf-8") as f:
                job_text = f.read()
        else:
            job_text = args.job
    else:
        print("\n--- ⚡ Auto-Tailor Engine Interactive Mode ---")
        args.company = input("Enter Company Name (optional): ").strip()
        args.role = input("Enter Job Title (optional): ").strip()
        print("\nPaste Job Description (finish input with an empty line or Ctrl+Z/Enter):")
        lines = []
        try:
            while True:
                line = input()
                if not line and lines:
                    break
                lines.append(line)
        except EOFError:
            pass
        job_text = "\n".join(lines).strip()

    if not job_text:
        print("Error: No job description provided.")
        sys.exit(1)

    print("\n⏳ Analyzing job posting and tailoring application...")
    result = engine.tailor_application(job_text, args.company, args.role, args.lang)

    os.makedirs(args.output_dir, exist_ok=True)
    cv_md_path = os.path.join(args.output_dir, "Tailored_CV.md")
    cv_html_path = os.path.join(args.output_dir, "Tailored_CV.html")
    cover_letter_path = os.path.join(args.output_dir, "Cover_Letter.txt")

    with open(cv_md_path, "w", encoding="utf-8") as f:
        f.write(result["markdown_resume"])

    with open(cv_html_path, "w", encoding="utf-8") as f:
        f.write(result["html_resume"])

    with open(cover_letter_path, "w", encoding="utf-8") as f:
        f.write(result["cover_letter"])

    print("\n" + "="*50)
    print(f"🎯 ATS Match Score: {result['ats_score']}%")
    print(f"📌 Classified Track: {result['track'].upper()}")
    print(f"🌐 Language: {result['lang'].upper()}")
    print(f"✅ Matched Skills: {', '.join(result['matched_skills']) if result['matched_skills'] else 'None'}")
    if result['missing_skills']:
        print(f"⚠️ Mentioned Skills to Highlight: {', '.join(result['missing_skills'])}")
    print("="*50)
    print(f"📄 Tailored Resume saved to: {cv_html_path}")
    print(f"📝 Markdown Resume saved to: {cv_md_path}")
    print(f"✉️ Cover Letter saved to:    {cover_letter_path}")
    print("="*50)
    print("\nTip: Open 'Tailored_CV.html' in your browser and press Ctrl+P to save as PDF!")

if __name__ == "__main__":
    main()
