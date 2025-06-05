// Persist a unique session ID in browser localStorage for backend isolation
const sessionId = localStorage.getItem("session_id") || crypto.randomUUID();
localStorage.setItem("session_id", sessionId);

console.log("Session ID:", sessionId);

// Fetch and populate the document sidebar
async function refreshSidebar() {
  // Pass session_id to backend to scope file operations
  const res = await fetch(`/list?session_id=${sessionId}`);

  // Rate Limiting
  if (res.status === 429 || res.redirected) {
    window.location.href = "/static/rate_limit.html";
    return;
  }



  const data = await res.json();
  const sidebar = document.getElementById("doc-sidebar");
  const selected = {};
  document.querySelectorAll('.doc-check').forEach(cb => {
    selected[cb.getAttribute("data-fname")] = cb.checked;
  });


  sidebar.innerHTML = "";


  for (const name of data.documents) {
    const isChecked = selected[name] ?? true;
    const div = document.createElement("div");
    div.className = "doc-item";
    div.innerHTML = `
    <label>
      <input type="checkbox" class="doc-check" data-fname="${name}" ${isChecked ? "checked" : ""} />
      ${name}
    </label>
    <button onclick="deleteDocument('${name}')">&#10060;</button>`;
    sidebar.appendChild(div);
  }
}

// Delete a document and refresh the sidebar
async function deleteDocument(filename) {
  // Pass session_id to backend to scope file operations
  const res = await fetch(`/delete?session_id=${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename }),
  });

  // Rate Limiting
  if (res.status === 429 || res.redirected) {
    window.location.href = "/static/rate_limit.html";
    return;
  }

  refreshSidebar();
}

const input = document.getElementById("file-input");
const fileListDiv = document.getElementById("selected-files");
const uploadStatus = document.getElementById("upload-status");

// Display selected file names
input.addEventListener("change", () => {
  const files = [...input.files].map((f) => f.name).join(", ");
  fileListDiv.textContent = files ? `Selected: ${files}` : "";
});

// Handle file upload form submission
document.getElementById("upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  // Check if any file is selected
  if (!input.files.length) {
    uploadStatus.style.color = "red";
    uploadStatus.textContent = "⚠️ Please choose files to upload.";
    setTimeout(() => {
      uploadStatus.textContent = "";
    }, 1000);
    return;
  }

  const formData = new FormData();
  for (const file of input.files) {
    formData.append("files", file);
  }

  // Pass session_id to backend to scope file operations
  const res = await fetch(`/upload?session_id=${sessionId}`, {
    method: "POST",
    body: formData,
  });

  // Rate Limiting
  if (res.status === 429 || res.redirected) {
    window.location.href = "/static/rate_limit.html";
    return;
  }

  refreshSidebar();

  uploadStatus.style.color = "green";
  uploadStatus.textContent = "✅ Files uploaded successfully!";

  setTimeout(() => {
    uploadStatus.textContent = "";
    fileListDiv.textContent = "";
  }, 1000);

  // Allow re-upload of same files
  input.value = null;
});

// Handle user query submission
document.getElementById("query-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = document.getElementById("user-question").value;
  const selectedFiles = [
    ...document.querySelectorAll(".doc-check:checked"),
  ].map((cb) => cb.getAttribute("data-fname"));
  const questionStatus = document.getElementById("question-status");
  const sidebar = document.getElementById("doc-sidebar");
  const analyzeBtn = document.getElementById("analyzeBtn");

  const tbody = document.querySelector("#answers-table tbody");
  const themesBox = document.getElementById("themes");

  // Check if a question is entered
  if (!q.trim()) {
    questionStatus.style.color = "red";
    questionStatus.textContent = "⚠️ Please enter a question.";
    setTimeout(() => {
      questionStatus.textContent = "";
    }, 1000);
    tbody.innerHTML = `
      <tr>
        <td colspan="3" style="text-align:center; color: #777;">
        No question asked for analysis
        </td>
      </tr>`;

    themesBox.textContent = "No question asked for analysis";
    return;
  }

  // Check if documents are present
  if (sidebar.innerHTML === "") {
    tbody.innerHTML = `
      <tr>
        <td colspan="3" style="text-align:center; color: #777;">
        No documents provided for analysis
        </td>
      </tr>`;

    themesBox.textContent = "No documents provided for analysis";
    return;
  }

  // Check if documents are selected
  if (!selectedFiles.length) {
    questionStatus.style.color = "red";
    questionStatus.textContent = "⚠️ Please select at least one document.";
    setTimeout(() => {
      questionStatus.textContent = "";
    }, 1000);
    tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color: #777;">No document selected for analysis</td></tr>`;
    themesBox.textContent = "No document selected for analysis";
    return;
  }

  // Disabale the analyze button, once clicked
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";

  tbody.innerHTML = `
    <tr>
      <td colspan="3" style="text-align:center; color:#555; padding:1rem;">
        ⏳ Loading answers...
      </td>
    </tr>`;
  themesBox.textContent = "⏳ Analyzing themes...";

  // Pass session_id to backend to scope file operations
  const res = await fetch(`/run-pipeline?session_id=${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: q, selected_files: selectedFiles }),
  });

  // Rate Limiting
  if (res.status === 429 || res.redirected) {
    window.location.href = "/static/rate_limit.html";
    return;
  }

  const data = await res.json();

  // Populate answers table
  tbody.innerHTML = "";

  for (const ans of data.answers) {
    const row = `<tr><td>${ans.doc_id}</td><td>${ans.answer}</td><td>${ans.citation}</td></tr>`;
    tbody.innerHTML += row;
  }

  // Show extracted themes
  themesBox.textContent = data.themes;

  // Enable the analysis button again
  analyzeBtn.textContent = "Analysis Completed";
  setTimeout(() => {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Run Analysis";
  }, 2000);
});

// Initial sidebar load
refreshSidebar();
