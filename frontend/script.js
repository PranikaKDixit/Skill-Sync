// ==========================================
// BACKEND API URL
// ==========================================

const API_URL = "http://localhost:8000";


// ==========================================
// STUDENT PAGE — POST /match-single
// ==========================================

async function calculateMatch() {
    const fileInput = document.getElementById("resumeFile");
    const jobDescription = document.getElementById("jobDescription").value.trim();
    const button = document.getElementById("matchButton");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");
    const error = document.getElementById("errorMessage");
    const warning = document.getElementById("warningMessage");
    const score = document.getElementById("matchScore");

    // Clear previous
    error.classList.add("hidden");
    warning.classList.add("hidden");
    result.classList.add("hidden");

    // Validate
    if (fileInput.files.length === 0) {
        showError(error, "Please upload a resume");
        return;
    }

    const file = fileInput.files[0];

    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
        showError(error, "Please upload PDF file only");
        return;
    }

    // Check file size client-side
    if (file.size > 5 * 1024 * 1024) {
        showError(error, "File exceeds 5MB limit");
        return;
    }

    if (!jobDescription) {
        showError(error, "Please paste job description");
        return;
    }

    // Build request
    const formData = new FormData();
    formData.append("resume_file", file);
    formData.append("job_description", jobDescription);

    button.disabled = true;
    loading.classList.remove("hidden");

    try {
        const response = await fetch(`${API_URL}/match-single`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => null);
            throw new Error(errData?.detail || `Server returned ${response.status}`);
        }

        const data = await response.json();
        console.log("Student API Response:", data);

        if (data.match_score === undefined) {
            throw new Error("Invalid response from backend");
        }

        // Show warning if present
        if (data.warning) {
            warning.textContent = `⚠️ ${data.warning}`;
            warning.classList.remove("hidden");
        }

        // Display score
        score.textContent = `${data.match_score}%`;

        // Display breakdown
        renderBreakdown(data.breakdown);

        // Display matched skills
        renderSkillTags("matchedSection", "matchedSkills", data.matched_skills, "matched");

        // Display missing skills
        renderSkillTags("missingSection", "missingSkills", data.missing_skills, "missing");

        result.classList.remove("hidden");

    } catch (err) {
        console.error(err);
        showError(error, err.message || "Something went wrong. Try again.");
    } finally {
        loading.classList.add("hidden");
        button.disabled = false;
    }
}


// ==========================================
// RENDER SCORE BREAKDOWN BARS
// ==========================================

function renderBreakdown(breakdown) {
    const container = document.getElementById("breakdownBars");
    container.innerHTML = "";

    if (!breakdown) return;

    // Friendly names for components
    const labels = {
        keyword: "Keyword Match",
        skill: "Skill Match",
        tfidf: "TF-IDF Similarity",
        inference: "Skill Inference",
        credibility: "Credibility",
        semantic: "Semantic Match",
    };

    for (const [key, value] of Object.entries(breakdown)) {
        // Skip zero-value placeholders
        if (value === 0 && (key === "inference" || key === "credibility" || key === "semantic")) {
            continue;
        }

        const label = labels[key] || key;
        const barWidth = Math.min(value, 100);

        const barHTML = `
            <div class="breakdown-row">
                <span class="breakdown-label">${label}</span>
                <div class="breakdown-bar-bg">
                    <div class="breakdown-bar-fill" style="width: ${barWidth}%"></div>
                </div>
                <span class="breakdown-value">${value}%</span>
            </div>
        `;
        container.insertAdjacentHTML("beforeend", barHTML);
    }
}


// ==========================================
// RENDER SKILL TAGS
// ==========================================

function renderSkillTags(sectionId, containerId, skills, type) {
    const section = document.getElementById(sectionId);
    const container = document.getElementById(containerId);

    if (!skills || skills.length === 0) {
        section.classList.add("hidden");
        return;
    }

    container.innerHTML = "";

    skills.forEach(skill => {
        const tag = document.createElement("span");
        tag.className = `skill-tag ${type}`;
        tag.textContent = skill;
        container.appendChild(tag);
    });

    section.classList.remove("hidden");
}


// ==========================================
// RECRUITER PAGE — POST /match-bulk
// ==========================================

async function rankCandidates() {
    const fileInput = document.getElementById("resumeFiles");
    const jobDescription = document.getElementById("recruiterJobDescription").value.trim();
    const button = document.getElementById("rankButton");
    const loading = document.getElementById("recruiterLoading");
    const result = document.getElementById("recruiterResult");
    const error = document.getElementById("recruiterError");
    const table = document.getElementById("resultsTable");

    error.classList.add("hidden");
    result.classList.add("hidden");
    table.innerHTML = "";

    // Validate
    if (fileInput.files.length === 0) {
        showError(error, "Please upload at least one resume");
        return;
    }

    for (let file of fileInput.files) {
        if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
            showError(error, "Please upload PDF files only");
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            showError(error, `File '${file.name}' exceeds 5MB limit`);
            return;
        }
    }

    if (!jobDescription) {
        showError(error, "Please paste job description");
        return;
    }

    const formData = new FormData();
    for (let file of fileInput.files) {
        formData.append("resume_files", file);
    }
    formData.append("job_description", jobDescription);

    button.disabled = true;
    loading.classList.remove("hidden");

    try {
        const response = await fetch(`${API_URL}/match-bulk`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => null);
            throw new Error(errData?.detail || `Server returned ${response.status}`);
        }

        const data = await response.json();
        console.log("Recruiter API Response:", data);

        if (!data.results) {
            throw new Error("Invalid response from backend");
        }

        // Summary stats
        const summaryDiv = document.getElementById("summaryStats");
        summaryDiv.innerHTML = `
            <p><strong>Processed:</strong> ${data.processed} of ${data.total_resumes} resumes
            ${data.failed > 0 ? ` | <span class="error-text">${data.failed} failed</span>` : ""}</p>
        `;

        // Sort by score
        const sortedResults = [...data.results].sort((a, b) => (b.score || -1) - (a.score || -1));

        // Build table rows
        sortedResults.forEach((candidate, index) => {
            const row = document.createElement("tr");

            if (candidate.status === "failed") {
                row.innerHTML = `
                    <td>—</td>
                    <td>${escapeHTML(candidate.filename)}</td>
                    <td colspan="4" class="error-text">Failed: ${escapeHTML(candidate.error || "Unknown error")}</td>
                `;
            } else {
                const matchedPreview = (candidate.matched_skills || []).slice(0, 3).join(", ");
                const matchedMore = (candidate.matched_skills || []).length > 3
                    ? ` +${candidate.matched_skills.length - 3} more`
                    : "";

                const missingPreview = (candidate.missing_skills || []).slice(0, 3).join(", ");
                const missingMore = (candidate.missing_skills || []).length > 3
                    ? ` +${candidate.missing_skills.length - 3} more`
                    : "";

                row.innerHTML = `
                    <td><strong>${candidate.rank || index + 1}</strong></td>
                    <td>${escapeHTML(candidate.filename)}</td>
                    <td><strong>${candidate.score}%</strong></td>
                    <td class="skills-preview matched">${matchedPreview}${matchedMore}</td>
                    <td class="skills-preview missing">${missingPreview}${missingMore}</td>
                    <td>
                        <button class="btn-small" onclick="toggleBreakdown(this, ${JSON.stringify(candidate.breakdown).replace(/"/g, '&quot;')})">
                            ▶ Details
                        </button>
                    </td>
                `;
            }

            table.appendChild(row);
        });

        result.classList.remove("hidden");

    } catch (err) {
        console.error(err);
        showError(error, err.message || "Something went wrong. Try again.");
    } finally {
        loading.classList.add("hidden");
        button.disabled = false;
    }
}


// ==========================================
// TOGGLE BREAKDOWN ROW IN RECRUITER TABLE
// ==========================================

function toggleBreakdown(button, breakdown) {
    const row = button.closest("tr");
    const existingDetail = row.nextElementSibling;

    // If detail row already visible, remove it
    if (existingDetail && existingDetail.classList.contains("detail-row")) {
        existingDetail.remove();
        button.textContent = "▶ Details";
        return;
    }

    // Create detail row
    const detailRow = document.createElement("tr");
    detailRow.className = "detail-row";

    let breakdownHTML = "";
    if (breakdown) {
        const labels = {
            keyword: "Keyword",
            skill: "Skill",
            tfidf: "TF-IDF",
            inference: "Inference",
            credibility: "Credibility",
            semantic: "Semantic",
        };

        for (const [key, value] of Object.entries(breakdown)) {
            if (value === 0 && (key === "inference" || key === "credibility" || key === "semantic")) {
                continue;
            }
            breakdownHTML += `<span class="breakdown-chip">${labels[key] || key}: ${value}%</span> `;
        }
    }

    detailRow.innerHTML = `<td colspan="6" class="detail-cell">${breakdownHTML}</td>`;
    row.after(detailRow);
    button.textContent = "▼ Details";
}


// ==========================================
// UTILITIES
// ==========================================

function showError(element, message) {
    element.textContent = message;
    element.classList.remove("hidden");
}

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


// ==========================================
// FILE INPUT LISTENERS
// ==========================================

const studentFileInput = document.getElementById("resumeFile");
if (studentFileInput) {
    studentFileInput.addEventListener("change", function () {
        const fileName = document.getElementById("fileName");
        if (this.files.length > 0) {
            const size = (this.files[0].size / 1024 / 1024).toFixed(1);
            fileName.textContent = `Selected: ${this.files[0].name} (${size} MB)`;
        } else {
            fileName.textContent = "";
        }
    });
}

const recruiterFileInput = document.getElementById("resumeFiles");
if (recruiterFileInput) {
    recruiterFileInput.addEventListener("change", function () {
        const selectedFiles = document.getElementById("selectedFiles");
        if (this.files.length === 0) {
            selectedFiles.textContent = "No files selected";
            return;
        }
        const totalSize = Array.from(this.files).reduce((sum, f) => sum + f.size, 0);
        selectedFiles.textContent = `${this.files.length} resume(s) selected (${(totalSize / 1024 / 1024).toFixed(1)} MB total)`;
    });
}