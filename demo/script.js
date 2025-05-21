// Fetch and populate the document sidebar
async function refreshSidebar() {
  const res = await fetch("/list");
  const data = await res.json();
  const sidebar = document.getElementById("doc-sidebar");
  sidebar.innerHTML = "";
  for (const name of data.documents) {
    const div = document.createElement("div");
    div.className = "doc-item";
    div.innerHTML = `${name} <button onclick="deleteDocument('${name}')">&#10060;</button>`;
    sidebar.appendChild(div);
  }
}

// Delete a document and refresh the sidebar
async function deleteDocument(filename) {
  await fetch(`/delete/${filename}`, { method: "DELETE" });
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
    }, 3000);
    return;
  }

  const formData = new FormData();
  for (const file of input.files) {
    formData.append("files", file);
  }

  await fetch("/upload", { method: "POST", body: formData });
  refreshSidebar();

  uploadStatus.style.color = "green";
  uploadStatus.textContent = "✅ Files uploaded successfully!";

  setTimeout(() => {
    uploadStatus.textContent = "";
    fileListDiv.textContent = "";
  }, 3000);

  // Allow re-upload of same files
  input.value = null;
});

// Handle user query submission
document.getElementById("query-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = document.getElementById("user-question").value;
  const questionStatus = document.getElementById("question-status");

  // Check if a question is entered
  if (!q.trim()) {
    questionStatus.style.color = "red";
    questionStatus.textContent = "⚠️ Please enter a question.";
    setTimeout(() => {
      questionStatus.textContent = "";
    }, 3000);
  }

  const tbody = document.querySelector("#answers-table tbody");
  const themesBox = document.getElementById("themes");

  tbody.innerHTML = `
    <tr>
      <td colspan="3" style="text-align:center; color:#555; padding:1rem;">
        ⏳ Loading answers...
      </td>
    </tr>`;
  themesBox.textContent = "⏳ Analyzing themes...";

  const res = await fetch("/run-pipeline", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: q }),
  });

  const data = await res.json();

  // Populate answers table
  tbody.innerHTML = "";

  // No question entered or No files for Preprocessing
  if (data.answers.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="3" style="text-align:center; color: #777;">
        ${data.themes}
        </td>
      </tr>`;

    themesBox.textContent = data.themes;
    return;
  }

  for (const ans of data.answers) {
    const row = `<tr><td>${ans.doc_id}</td><td>${ans.answer}</td><td>${ans.citation}</td></tr>`;
    tbody.innerHTML += row;
  }

  // Show extracted themes
  themesBox.textContent = data.themes;
});

// Initial sidebar load
refreshSidebar();
