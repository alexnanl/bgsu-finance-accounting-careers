I want to build a Streamlit career website for BGSU students.

Purpose:
When I receive job or internship opening information from employers, I want to submit it through this website. The website should use the OpenAI API to rewrite and standardize the opening information into a consistent format, then display it on the website as a clean job/internship listing with detailed information.

Please create the Streamlit web app directly in this folder. I do not need to review the code line by line. I want to see the working result.

Main features:

1. A form where I can paste raw job/internship opening information from employers.
2. The app sends the raw text to the OpenAI API and reformats it into a standard structure.
3. The standardized listing should include fields such as:

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
4. The website should display all submitted openings in a clean list.
5. Add a detail view for each opening.
6. Store the submitted openings locally first, for example using a JSON file or SQLite database.
7. Use a modern, clean, professional design suitable for BGSU students.
8. Include clear setup instructions in a README file.
9. After creating the app, run it locally so I can preview the result in the browser.

Please first create the project structure, then implement the Streamlit app. If you need my OpenAI API key, Streamlit account, or GitHub account for deployment, please tell me exactly what is needed and where I should put it. Do not hard-code any API key into the code. Use environment variables or Streamlit secrets.
