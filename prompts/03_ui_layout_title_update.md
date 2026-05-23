Please update the current Streamlit career website UI based on the following changes.

1. Website title / branding

* Change the main page title from “BGSU Career Openings” to:
  “BGSU Finance & Accounting Career Openings”
* Change the left sidebar brand name from “BGSU Career Hub” to:
  “BGSU Finance & Accounting Career Openings”
* Keep the BGSU-style orange/brown visual theme.

2. Search and filter layout

* On the Browse Openings page, make the keyword search box take one full row by itself.
* Placeholder text should be:
  “Search title, company, skill, keyword...”
* Put the four dropdown filters on the next row:

  * Company
  * Location
  * Job type
  * Work mode
* The layout should look clean and aligned, not crowded.

3. Job posting cards

* Remove the separate “View details” button from each job posting card.
* Make the position title itself clickable.
* When students click the position title, it should open the detail view for that posting.
* The title should look like an interactive link, but still fit the professional card design.
* Keep the card showing only brief information:

  * Position title
  * Company / organization
  * Job type
  * Location
  * Work mode if available
  * Application deadline if available

4. Detail behavior

* Clicking the position title should behave exactly the same as the old “View details” button.
* The detail page should still show the full structured posting information.
* Keep non-active postings hidden from public users.

5. After making these changes

* Update the relevant app files directly.
* Restart or refresh the Streamlit app.
* Make sure the updated version works at http://localhost:8501.
