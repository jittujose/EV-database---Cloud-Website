# EV Database Cloud Website

This project is a web application for managing and comparing electric vehicles (EVs). It utilizes **Firebase Authentication** for login/logout functionality, **Firestore** for storing and querying EV data, and provides various features for managing and comparing EVs. 

## Features

- **Login/Logout Service**: Implements Firebase authentication for secure login and logout. The login system is set up using `firebase-login.js` as specified.
- **Firestore Collection**: Represents EVs with attributes: `name`, `manufacturer`, `year`, `battery size (Kwh)`, `WLTP range (Km)`, `cost`, and `power (Kw)`. No composite index is used.
- **Add EV Page**: A separate page for adding new EVs to the Firestore database.
- **Search Form**: Users (both guests and logged-in) can search for EVs by querying single attributes. The search supports:
  - **String Attributes**: Single input string.
  - **Numerical Attributes**: Range with upper and lower limits.
  - Displays a list of EVs that match the query with hyperlinks.
  - If fields are blank, all EVs are returned.

- **EV Information Page**: Clicking on an EV hyperlink leads to a detailed information page for that EV.
- **Edit EV**: Logged-in users can edit the EV details from the information page.
- **Delete EV**: Logged-in users can delete an EV from the information page.
- **EV Comparison**: A form allows selecting two EVs for comparison, with results displayed on a separate page.

- **Comparison Highlights**: On the comparison page:
  - Highest values are highlighted in green.
  - Lowest values are highlighted in red (opposite for cost).
- **Hyperlinks in Comparison**: EV names on the comparison page are hyperlinks to their respective information pages.
- **EV Reviews**: Users can submit reviews (up to 1,000 characters) and rate from 0 to 10.
  - Reviews are visible on the EV information page for both users and guests.

- **Average Review Score**: The EV information page shows the average review score of all reviews.
- **Review Order**: Reviews are displayed in reverse chronological order.
- **Comparison Average Score**: Average scores are included on the comparison page, highlighted in green if highest and red if lowest.
- **UI Design**: Well-designed, intuitive, and user-friendly UI.

## Technologies Used

- **Firebase Authentication** for login/logout
- **Firestore** for data storage
- **HTML/CSS/JavaScript** for frontend development
- **Firebase SDK** for database interactions
