Please modify the current Streamlit career website so it is ready to be deployed as a public website that other people can visit through a public URL.

Goal:
I want this to become a public-facing BGSU student career openings website. Students can visit the public website and browse job/internship postings. Only the editor/admin can add, edit, or manage postings.

Public student-facing side:

1. The default homepage should be Browse Openings.
2. Students should not need to log in.
3. Students should only see published/active job or internship postings.
4. The Browse Openings page should show a clean list of postings as cards.
5. Each card should show only brief information:

   * Job title
   * Company / organization
   * Location
   * Remote / hybrid / onsite
   * Job type
   * Application deadline
6. Students can click “View Details” to see the full posting details.
7. The detail page should show:

   * Job title
   * Company / organization
   * Location
   * Remote / hybrid / onsite
   * Job type
   * Eligibility
   * Required skills
   * Preferred qualifications
   * Application deadline
   * Application link or contact email
   * Full description
8. Add search and filters if possible:

   * keyword search
   * company
   * location
   * job type
   * remote / hybrid / onsite
   * status or deadline

Admin / Editor side:

1. Add an Admin / Editor page in the sidebar.
2. The Admin / Editor page must be password protected.
3. Store the admin password using Streamlit secrets or environment variables, not hard-coded in the code.
4. The editor can add a new posting in two ways:

   * paste raw job/internship text
   * paste a job posting URL
5. The editor can use OpenAI API to standardize the posting into a consistent format.
6. If automatic URL extraction is difficult, create the URL input field and fallback instruction: “If URL extraction fails, paste the job posting text manually.”
7. The editor can review and edit all extracted fields before saving.
8. The editor can mark postings as Draft, Active, or Closed.
9. Only Active postings should appear on the public student-facing page.
10. The editor should be able to edit or delete existing postings.

Deployment requirements:

1. Make the project ready for Streamlit Community Cloud deployment.
2. Add a clear README section explaining how to deploy it publicly.
3. Include instructions for GitHub upload and Streamlit Cloud deployment.
4. Do not commit or expose any real API keys.
5. Use `.streamlit/secrets.toml.example` to show the required secrets:

   * OPENAI_API_KEY
   * ADMIN_PASSWORD
   * OPENAI_MODEL
6. Make sure `.streamlit/secrets.toml` and `.env` are in `.gitignore`.
7. The app should still run locally at http://localhost:8501 for testing.
8. The deployed public website should work without students needing any account.

Data storage:

1. For local prototype, keep using JSON storage.
2. But add a clear note in README that JSON storage is temporary.
3. Explain that for real public multi-user use, the next version should use a cloud database such as Supabase, Firebase, or Google Sheets.
4. Make the code structure easy to upgrade from local JSON to a cloud database later.

Please update the existing Streamlit app directly. After editing, run or restart the app locally so I can preview the updated public-facing version.
