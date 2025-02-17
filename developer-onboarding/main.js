// Wait for the page to load
document.addEventListener("DOMContentLoaded", function () {
    const accountForm = document.getElementById("account-form");
    const onboardingForm = document.getElementById("onboarding-form");
    const recommendationsSection = document.getElementById("recommendations");
    const resourceList = document.getElementById("resource-list");
    const onboardingSection = document.getElementById("onboarding");
    const accountCreationSection = document.getElementById("account-creation");
    const languageFilter = document.getElementById("language-filter");
    const languageSelect = document.getElementById("languages");

    // Handle account creation
    accountForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reload
        const email = document.getElementById("email").value;
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        // Simulate account creation and store user details (you will connect to backend here)
        localStorage.setItem("user", JSON.stringify({ email, username, password }));

        // After account creation, show the onboarding form
        accountCreationSection.style.display = "none";
        onboardingSection.style.display = "block";
    });

    // Handle onboarding form submission
    onboardingForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reload
        const experience = document.getElementById("experience").value;
        const languages = Array.from(languageSelect.selectedOptions).map(option => option.value);

        // Simulate sending onboarding data (you can send this to backend via API)
        localStorage.setItem("onboardingData", JSON.stringify({ experience, languages }));

        // Show recommendations based on the inputs
        const resources = getRecommendedResources(languages, experience);
        displayResources(resources);

        // Show the recommendations section
        onboardingSection.style.display = "none";
        recommendationsSection.style.display = "block";
    });

    // Function to filter programming languages dynamically
    languageFilter.addEventListener("input", function () {
        let filter = this.value.toLowerCase();
        let options = languageSelect.options;

        for (let option of options) {
            let text = option.textContent.toLowerCase();
            option.style.display = text.includes(filter) ? "block" : "none";
        }
    });

    // Function to simulate resource recommendations based on experience and languages
    function getRecommendedResources(languages, experience) {
        let resources = [];
        if (languages.includes("Python")) {
            if (experience === "beginner") {
                resources.push("Python for Beginners: Introduction");
            } else if (experience === "intermediate") {
                resources.push("Intermediate Python: Data Structures");
            } else {
                resources.push("Advanced Python: Machine Learning with Python");
            }
        }
        if (languages.includes("JavaScript")) {
            if (experience === "beginner") {
                resources.push("JavaScript for Beginners: Basics");
            } else if (experience === "intermediate") {
                resources.push("Intermediate JavaScript: Asynchronous Programming");
            } else {
                resources.push("Advanced JavaScript: Web Development");
            }
        }
        return resources;
    }

    // Function to display resources dynamically
    function displayResources(resources) {
        resourceList.innerHTML = ''; // Clear any previous resources
        resources.forEach(resource => {
            const li = document.createElement("li");
            li.textContent = resource;
            resourceList.appendChild(li);
        });
    }
});
