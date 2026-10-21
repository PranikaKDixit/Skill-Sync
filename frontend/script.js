// ============================================================
// SkillSync Frontend — Student + Recruiter Dashboards
// ============================================================

// Chart instances (for cleanup on re-render)
let gaugeChartInstance = null;
let breakdownChartInstance = null;
let radarChartInstance = null;
let distributionChartInstance = null;
let skillAvailChartInstance = null;

// ============================================================
// STUDENT PORTAL
// ============================================================
document.getElementById("matchForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("analyzeBtn");
    btn.textContent = "Analyzing...";
    btn.disabled = true;

    const formData = new FormData();
    formData.append("resume_file", document.getElementById("resumeFile").files[0]);
    formData.append("job_description", document.getElementById("jobDescription").value);
    formData.append("mode", "enhanced");

    try {
        const res = await fetch("/analyze", { method: "POST", body: formData });
        const data = await res.json();

        if (data.warning) {
            const w = document.getElementById("warning");
            w.textContent = "⚠️ " + data.warning;
            w.style.display = "block";
        }

        renderStudentDashboard(data);
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        btn.textContent = "Analyze Match";
        btn.disabled = false;
    }
});

function renderStudentDashboard(data) {
    document.getElementById("dashboard").style.display = "block";

    // 1. Gauge Chart
    renderGauge(data.score);

    // 2. Breakdown Bar Chart
    renderBreakdown(data.breakdown);

    // 3. Radar Chart (skill categories)
    if (data.skill_categories && Object.keys(data.skill_categories).length > 0) {
        renderRadar(data.skill_categories);
    }

    // 4. Skill Tags
    renderSkillTags("matchedSkills", data.matched_skills || [], "matched");
    renderSkillTags("missingSkills", data.missing_skills || [], "missing");

    // 5. Inferred Skills
    if (data.inferred_skills && data.inferred_skills.length > 0) {
        document.getElementById("inferredRow").style.display = "flex";
        renderInferredSkills(data.inferred_skills);
    }

    // 6. Credibility Table
    if (data.credibility && Object.keys(data.credibility).length > 0) {
        document.getElementById("credibilityRow").style.display = "flex";
        renderCredibility(data.credibility);
    }

    // 7. Recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        document.getElementById("recsRow").style.display = "flex";
        renderRecommendations(data.recommendations);
    }
}

function renderGauge(score) {
    document.getElementById("scoreValue").textContent = score + " / 100";
    const ctx = document.getElementById("gaugeChart").getContext("2d");
    if (gaugeChartInstance) gaugeChartInstance.destroy();

    const color = score >= 70 ? "#22c55e" : score >= 40 ? "#f59e0b" : "#ef4444";
    gaugeChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [color, "#e5e7eb"],
                borderWidth: 0,
            }]
        },
        options: {
            cutout: "75%",
            rotation: -90,
            circumference: 180,
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            responsive: false,
        }
    });
}

function renderBreakdown(breakdown) {
    const ctx = document.getElementById("breakdownChart").getContext("2d");
    if (breakdownChartInstance) breakdownChartInstance.destroy();

    const labels = Object.keys(breakdown).map(k =>
        k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())
    );
    const values = Object.values(breakdown);
    const colors = ["#3b82f6", "#8b5cf6", "#06b6d4", "#f59e0b", "#ef4444", "#22c55e"];

    breakdownChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Points",
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderRadius: 4,
            }]
        },
        options: {
            indexAxis: "y",
            plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, max: 30 } },
            responsive: true,
        }
    });
}

function renderRadar(categories) {
    const ctx = document.getElementById("radarChart").getContext("2d");
    if (radarChartInstance) radarChartInstance.destroy();

    const labels = Object.keys(categories);
    const coverage = labels.map(l => categories[l].coverage);

    radarChartInstance = new Chart(ctx, {
        type: "radar",
        data: {
            labels: labels.map(l => l.length > 15 ? l.slice(0, 14) + "…" : l),
            datasets: [{
                label: "Coverage %",
                data: coverage,
                backgroundColor: "rgba(59, 130, 246, 0.2)",
                borderColor: "#3b82f6",
                pointBackgroundColor: "#3b82f6",
            }]
        },
        options: {
            scales: { r: { beginAtZero: true, max: 100 } },
            plugins: { legend: { display: false } },
            responsive: true,
        }
    });
}

function renderSkillTags(containerId, skills, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    if (skills.length === 0) {
        container.innerHTML = `<span class="skill-tag ${type}">None</span>`;
        return;
    }
    skills.forEach(s => {
        const tag = document.createElement("span");
        tag.className = `skill-tag ${type}`;
        tag.textContent = s;
        container.appendChild(tag);
    });
}

function renderInferredSkills(inferred) {
    const container = document.getElementById("inferredSkills");
    container.innerHTML = "";
    inferred.forEach(item => {
        const div = document.createElement("div");
        div.className = "inferred-item";
        const confClass = item.confidence_label === "High" ? "conf-high"
            : item.confidence_label === "Medium" ? "conf-medium" : "conf-low";
        div.innerHTML = `
            <strong>${item.skill}</strong>
            <span class="conf-badge ${confClass}">${item.confidence_label} (${(item.confidence * 100).toFixed(0)}%)</span>
            <span class="evidence">Evidence: ${item.evidence.join(", ")}</span>
        `;
        container.appendChild(div);
    });
}

function renderCredibility(credibility) {
    const container = document.getElementById("credibilityTable");
    let html = `<table class="cred-table">
        <thead><tr><th>Skill</th><th>Score</th><th>Label</th><th>Source</th><th>Signals</th></tr></thead><tbody>`;
    for (const [skill, info] of Object.entries(credibility)) {
        const labelClass = info.label === "High" ? "conf-high"
            : info.label === "Medium" ? "conf-medium" : "conf-low";
        html += `<tr>
            <td><strong>${skill}</strong></td>
            <td>${(info.score * 100).toFixed(0)}%</td>
            <td><span class="conf-badge ${labelClass}">${info.label}</span></td>
            <td>${info.source}</td>
            <td>${(info.signals || []).join("; ")}</td>
        </tr>`;
    }
    html += "</tbody></table>";
    container.innerHTML = html;
}

function renderRecommendations(recs) {
    const container = document.getElementById("recommendations");
    container.innerHTML = "";
    recs.forEach(r => {
        const div = document.createElement("div");
        div.className = `rec-card priority-${r.priority}`;
        div.innerHTML = `
            <div class="rec-priority">${r.priority}</div>
            <h4>${r.title}</h4>
            <p>${r.description}</p>
            ${r.resource_url ? `<a href="${r.resource_url}" target="_blank">📚 ${r.resource_name}</a>` : ""}
        `;
        container.appendChild(div);
    });
}

// ============================================================
// RECRUITER PORTAL
// ============================================================
document.getElementById("bulkForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("screenBtn");
    btn.textContent = "Screening...";
    btn.disabled = true;

    const formData = new FormData();
    const files = document.getElementById("resumeFiles").files;
    for (let f of files) formData.append("resume_files", f);
    formData.append("job_description", document.getElementById("jobDescription").value);
    formData.append("mode", "enhanced");

    try {
        const res = await fetch("/match-bulk", { method: "POST", body: formData });
        const data = await res.json();
        renderRecruiterDashboard(data.results || []);
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        btn.textContent = "Screen Candidates";
        btn.disabled = false;
    }
});

function renderRecruiterDashboard(results) {
    if (results.length === 0) return;
    document.getElementById("results").style.display = "block";

    // Sort by score descending
    results.sort((a, b) => (b.score || 0) - (a.score || 0));

    // Distribution chart
    renderDistribution(results);

    // Rankings table
    const tbody = document.querySelector("#rankingsTable tbody");
    tbody.innerHTML = "";
    results.forEach((r, i) => {
        const tr = document.createElement("tr");
        const inferred = (r.inferred_skills || []).map(s => s.skill).join(", ") || "—";
        tr.innerHTML = `
            <td>${i + 1}</td>
            <td>${r.filename || "Unknown"}</td>
            <td><strong>${r.score || 0}</strong></td>
            <td>${(r.matched_skills || []).slice(0, 4).join(", ")}</td>
            <td>${(r.missing_skills || []).slice(0, 3).join(", ")}</td>
            <td>${inferred}</td>
        `;
        tbody.appendChild(tr);
    });

    // Skill availability
    renderSkillAvailability(results);
}

function renderDistribution(results) {
    const ctx = document.getElementById("distributionChart").getContext("2d");
    if (distributionChartInstance) distributionChartInstance.destroy();

    const labels = results.map(r => (r.filename || "?").slice(0, 15));
    const scores = results.map(r => r.score || 0);
    const colors = scores.map(s => s >= 70 ? "#22c55e" : s >= 40 ? "#f59e0b" : "#ef4444");

    distributionChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Similarity Score",
                data: scores,
                backgroundColor: colors,
                borderRadius: 4,
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, max: 100 } },
            responsive: true,
        }
    });
}

function renderSkillAvailability(results) {
    // Count how many candidates have each skill
    const skillCounts = {};
    results.forEach(r => {
        (r.matched_skills || []).forEach(s => {
            skillCounts[s] = (skillCounts[s] || 0) + 1;
        });
    });

    const topSkills = Object.entries(skillCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    if (topSkills.length === 0) return;
    document.getElementById("skillAvailRow").style.display = "flex";

    const ctx = document.getElementById("skillAvailChart").getContext("2d");
    if (skillAvailChartInstance) skillAvailChartInstance.destroy();

    skillAvailChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: topSkills.map(s => s[0]),
            datasets: [{
                label: "Candidates with skill",
                data: topSkills.map(s => s[1]),
                backgroundColor: "#8b5cf6",
                borderRadius: 4,
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
            responsive: true,
        }
    });
}