import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from job_hunter import JobHunter

hunter = JobHunter('profile_data.json')
jobs = hunter.scan_and_tailor(min_ats_score=65, region='morocco')

print("\n=== TOP MOROCCO JOBS FOUND (RABAT / SALE / KENITRA) ===")
morocco_count = 0
for i, j in enumerate(jobs):
    loc = j.get('location', '')
    if any(c in loc.lower() for c in ['rabat', 'salé', 'sale', 'kénitra', 'kenitra', 'maroc']):
        morocco_count += 1
        print(f"{morocco_count}. [{j.get('ats_score')}%] {j.get('title')}")
        print(f"   🏢 {j.get('company')} | 📍 {j.get('location')} | 🌐 {j.get('source')}")
        print(f"   🔗 {j.get('url')}\n")
        if morocco_count >= 8:
            break

print(f"Total Moroccan opportunities processed: {morocco_count}")
