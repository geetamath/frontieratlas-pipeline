# Final Submission Guide — GraphOne / FrontierAtlas Demo Task

**Deadline**: **12th Sep 2026, 7:00 PM IST**  
**Submission Form Link**: [Google Form (AI Engineer Internship)](https://forms.gle/8bnrg78Ki4E25RAk8)

---

## Step 1: Push Code to Your GitHub Repository

1. Open your terminal in `d:\Unstop AI Internship`:
   ```bash
   git init
   git add .
   git commit -m "feat: complete FrontierAtlas production ingestion & entity resolution pipeline"
   ```
2. Create a new public repository on [GitHub](https://github.com/new) named `frontieratlas-pipeline` (or your preferred name).
3. Link and push your code:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/frontieratlas-pipeline.git
   git push -u origin main
   ```
4. Verify your repository has:
   - `README.md` (detailed setup & architecture)
   - `architecture.pdf` (3-page technical design)
   - `src/` (complete pipeline source code)
   - `output/pipeline_output.xlsx` and CSV files

---

## Step 2: Upload Data Output to Google Sheets

The submission requires a public Google Sheet with 6 tabs:
- **Startups** (1,050 rows)
- **Products** (1,050 rows)
- **Research Papers** (1,050 rows with GitHub stars)
- **Jobs** (All 24-hr fresh AI jobs)
- **News** (All 24-hr fresh AI news)
- **Entity Mapping Log** (2,240+ rows of raw vs canonical mappings)

### Method A (Fastest — 1 Click):
1. Go to [Google Drive](https://drive.google.com).
2. Click **+ New** $\rightarrow$ **File upload** $\rightarrow$ Select `output/pipeline_output.xlsx` from this workspace.
3. Right-click the uploaded file in Google Drive $\rightarrow$ **Open with** $\rightarrow$ **Google Sheets**.
4. All 6 tabs will automatically be formatted with clean headers and column widths!
5. Click **Share** (top right) $\rightarrow$ Change **General access** to **"Anyone with the link"** with **"Viewer"** permissions.
6. Click **Copy link**.

---

## Step 3: Record Your Loom Walkthrough Video

1. Open [`loom_script.md`](loom_script.md) for the exact word-for-word timed talking points (5–8 minutes).
2. Have your 3 tabs open:
   - Your GitHub repository
   - Your Google Sheet
   - Your `architecture.pdf`
3. Record using [Loom](https://www.loom.com) or record your screen using OBS / Windows Game Bar (`Win + Alt + R`).
4. If using Google Drive: Upload the `.mp4` video to Google Drive, right-click $\rightarrow$ **Share** $\rightarrow$ **"Anyone with the link can view"** $\rightarrow$ Copy link.

---

## Step 4: Fill Out the Google Form

Open the [Google Form](https://forms.gle/8bnrg78Ki4E25RAk8) and fill in the fields:

| Form Field | Suggested Entry |
| :--- | :--- |
| **Email** | Your active email address |
| **Name** | Your full name |
| **Mobile** | Your active mobile number |
| **email Id** | Your secondary or college email address |
| **College** | Your University / College name |
| **What course are you pursuing?** | e.g. *B.Tech in Computer Science and Engineering* (or your current degree) |
| **What year are you in?** | e.g. *Final Year (2026)* or your current year |
| **City** | Your current city |
| **How many hours per day can you dedicate?** | e.g. *6–8 hours/day* (Full commitment) |
| **How soon can you start if selected?** | e.g. *Immediately* |
| **Loom video (5-10 min) explaining** | Your Loom URL or Google Drive video link (ensure public view access) |
| **Data Output (Google Sheets)** | Your public Google Sheets URL from Step 2 |
| **GitHub repository** | Your GitHub repository URL from Step 1 |

Click **Submit** before the deadline!
