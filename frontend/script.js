// ==========================================
// BACKEND API URL
// ==========================================

const API_URL = "http://localhost:8000";


// ==========================================
// STUDENT PAGE
// POST /match-single
// ==========================================

async function calculateMatch() {

    const fileInput = document.getElementById("resumeFile");
    const jobDescription =
        document.getElementById("jobDescription").value.trim();

    const button =
        document.getElementById("matchButton");

    const loading =
        document.getElementById("loading");

    const result =
        document.getElementById("result");

    const error =
        document.getElementById("errorMessage");

    const score =
        document.getElementById("matchScore");


    // ------------------------------------------
    // Clear previous messages
    // ------------------------------------------

    error.classList.add("hidden");
    result.classList.add("hidden");


    // ------------------------------------------
    // Validate resume
    // ------------------------------------------

    if (fileInput.files.length === 0) {

        showError(
            error,
            "Please upload a resume"
        );

        return;
    }


    const file = fileInput.files[0];


    // ------------------------------------------
    // Validate PDF
    // ------------------------------------------

    if (
        file.type !== "application/pdf" &&
        !file.name.toLowerCase().endsWith(".pdf")
    ) {

        showError(
            error,
            "Please upload PDF file only"
        );

        return;
    }


    // ------------------------------------------
    // Validate job description
    // ------------------------------------------

    if (!jobDescription) {

        showError(
            error,
            "Please paste job description"
        );

        return;
    }


    // ------------------------------------------
    // Create FormData
    // ------------------------------------------

    const formData = new FormData();


    // IMPORTANT:
    // These names MUST match backend.

    formData.append(
        "resume_file",
        file
    );

    formData.append(
        "job_description",
        jobDescription
    );


    // ------------------------------------------
    // Show loading
    // ------------------------------------------

    button.disabled = true;

    loading.classList.remove("hidden");


    try {

        // --------------------------------------
        // Call backend
        // --------------------------------------

        const response = await fetch(
            `${API_URL}/match-single`,
            {
                method: "POST",
                body: formData
            }
        );


        // --------------------------------------
        // Check response
        // --------------------------------------

        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        // --------------------------------------
        // Convert response to JSON
        // --------------------------------------

        const data = await response.json();


        console.log("Student API Response:", data);


        // --------------------------------------
        // Get match score
        // Expected:
        // { "match_score": 78 }
        // --------------------------------------

        if (data.match_score === undefined) {

            throw new Error(
                "Invalid response from backend"
            );
        }


        // --------------------------------------
        // Display score
        // --------------------------------------

        score.textContent =
            `${data.match_score}%`;

        result.classList.remove("hidden");


    } catch (err) {

        console.error(err);

        showError(
            error,
            "Something went wrong. Try again."
        );


    } finally {

        // --------------------------------------
        // Hide loading
        // --------------------------------------

        loading.classList.add("hidden");

        button.disabled = false;
    }
}


// ==========================================
// RECRUITER PAGE
// POST /match-bulk
// ==========================================

async function rankCandidates() {

    const fileInput =
        document.getElementById("resumeFiles");

    const jobDescription =
        document
            .getElementById("recruiterJobDescription")
            .value
            .trim();

    const button =
        document.getElementById("rankButton");

    const loading =
        document.getElementById("recruiterLoading");

    const result =
        document.getElementById("recruiterResult");

    const error =
        document.getElementById("recruiterError");

    const table =
        document.getElementById("resultsTable");


    // ------------------------------------------
    // Clear previous results
    // ------------------------------------------

    error.classList.add("hidden");

    result.classList.add("hidden");

    table.innerHTML = "";


    // ------------------------------------------
    // Validate files
    // ------------------------------------------

    if (fileInput.files.length === 0) {

        showError(
            error,
            "Please upload at least one resume"
        );

        return;
    }


    // ------------------------------------------
    // Validate PDF files
    // ------------------------------------------

    for (let file of fileInput.files) {

        if (
            file.type !== "application/pdf" &&
            !file.name.toLowerCase().endsWith(".pdf")
        ) {

            showError(
                error,
                "Please upload PDF files only"
            );

            return;
        }
    }


    // ------------------------------------------
    // Validate job description
    // ------------------------------------------

    if (!jobDescription) {

        showError(
            error,
            "Please paste job description"
        );

        return;
    }


    // ------------------------------------------
    // Create FormData
    // ------------------------------------------

    const formData = new FormData();


    // IMPORTANT:
    // Backend expects "resume_files"
    // plural.

    for (let file of fileInput.files) {

        formData.append(
            "resume_files",
            file
        );
    }


    formData.append(
        "job_description",
        jobDescription
    );


    // ------------------------------------------
    // Show loading
    // ------------------------------------------

    button.disabled = true;

    loading.classList.remove("hidden");


    try {

        // --------------------------------------
        // Call backend
        // --------------------------------------

        const response = await fetch(
            `${API_URL}/match-bulk`,
            {
                method: "POST",
                body: formData
            }
        );


        // --------------------------------------
        // Check response
        // --------------------------------------

        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        // --------------------------------------
        // Convert response to JSON
        // --------------------------------------

        const data = await response.json();


        console.log(
            "Recruiter API Response:",
            data
        );


        // --------------------------------------
        // Validate response
        // --------------------------------------

        if (!data.results) {

            throw new Error(
                "Invalid response from backend"
            );
        }


        // --------------------------------------
        // Sort results by score
        // Highest score first
        // --------------------------------------

        const results =
            [...data.results].sort(
                (a, b) => b.score - a.score
            );


        // --------------------------------------
        // Create table rows
        // --------------------------------------

        results.forEach(
            (candidate, index) => {

                const row =
                    document.createElement("tr");


                row.innerHTML = `
                    <td>${index + 1}</td>

                    <td>
                        ${escapeHTML(candidate.filename)}
                    </td>

                    <td>
                        <strong>
                            ${candidate.score}%
                        </strong>
                    </td>
                `;


                table.appendChild(row);
            }
        );


        // --------------------------------------
        // Display results
        // --------------------------------------

        result.classList.remove("hidden");


    } catch (err) {

        console.error(err);

        showError(
            error,
            "Something went wrong. Try again."
        );


    } finally {

        // --------------------------------------
        // Hide loading
        // --------------------------------------

        loading.classList.add("hidden");

        button.disabled = false;
    }
}


// ==========================================
// SHOW ERROR
// ==========================================

function showError(element, message) {

    element.textContent = message;

    element.classList.remove("hidden");
}


// ==========================================
// DISPLAY SELECTED STUDENT FILE
// ==========================================

const studentFileInput =
    document.getElementById("resumeFile");

if (studentFileInput) {

    studentFileInput.addEventListener(
        "change",
        function () {

            const fileName =
                document.getElementById("fileName");

            if (this.files.length > 0) {

                fileName.textContent =
                    `Selected: ${this.files[0].name}`;

            } else {

                fileName.textContent = "";
            }
        }
    );
}


// ==========================================
// DISPLAY SELECTED RECRUITER FILES
// ==========================================

const recruiterFileInput =
    document.getElementById("resumeFiles");

if (recruiterFileInput) {

    recruiterFileInput.addEventListener(
        "change",
        function () {

            const selectedFiles =
                document.getElementById("selectedFiles");


            if (this.files.length === 0) {

                selectedFiles.textContent =
                    "No files selected";

                return;
            }


            selectedFiles.textContent =
                `${this.files.length} resume(s) selected`;
        }
    );
}


// ==========================================
// BASIC HTML ESCAPING
// ==========================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}