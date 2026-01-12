# PRRA - Quick Start Tutorial

## First Time Setup

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/Cansaoking/PRRA.git
cd PRRA

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

**Note**: This installation may take 10-30 minutes as it downloads PyTorch and other large libraries.

### 2. Verify Installation

```bash
# Test core modules (no GUI required)
python test_modules.py
```

You should see:
```
✅ All core module tests passed!
```

## Running the Application

### Launch PRRA

```bash
python main.py
```

or

```bash
python prra.py  # Legacy entry point
```

The main window will open with 4 tabs.

## Step-by-Step Usage

### Step 1: Load Manuscript (📄 Manuscript Tab)

1. Click **"📂 Open Manuscript"**
2. Select your manuscript file:
   - PDF (`.pdf`)
   - Word (`.docx`, `.doc`)
   - Rich Text (`.rtf`)
   - Plain Text (`.txt`)
3. Preview appears automatically

**Example**: `my_research_paper.pdf`

### Step 2: Configure Settings (⚙️ Configuration Tab)

#### Key Phrase Extraction
- **Number of key phrases**: 3-10 (default: 5)
  - More phrases = broader search
  - Fewer phrases = more focused

#### PubMed Search
- **Articles per search**: 5-50 (default: 20)
  - More articles = more reference data
  - Takes longer to process

#### AI Model
Select from dropdown:
- **Qwen/Qwen2.5-7B-Instruct** (recommended, balanced)
- **deepseek-ai/deepseek-coder-7b-instruct-v1.5** (code-focused)
- **microsoft/Phi-3-mini-4k-instruct** (fast, smaller)
- **meta-llama/Llama-2-7b-chat-hf** (general purpose)

**First time**: Model downloads automatically (1-5 minutes, 4-14 GB)

#### Output Format
- **PDF**: Professional, fixed layout
- **DOCX**: Editable in Word

#### Options
- ☑️ **Manual mode**: Pause at each step for confirmation
- ☐ **Auto mode**: Run completely automatically (recommended)

### Step 3: Customize Prompts (💬 Prompts Tab) - Optional

The prompts tell the AI what to do. Edit if you want custom evaluation criteria.

**Default prompts work well for most cases - skip this step if unsure!**

#### To Customize:
1. Edit JSON directly in the text editor
2. Use placeholders: `{num}`, `{text}`, `{abstracts}`, `{type}`
3. Click **"💾 Save to File"** to save custom prompts
4. Click **"📂 Load from File"** to load saved prompts
5. Click **"Reset to Default"** to restore original prompts

**Tip**: Save different prompt sets for different manuscript types!

### Step 4: Start Review (▶ Start Review Button)

1. Click **"▶ Start Review"**
2. Switch to **"📊 Progress"** tab automatically
3. Watch real-time progress:
   - Progress bar (0-100%)
   - Detailed log messages
   - Emoji indicators for each step

#### What Happens:

```
📄 Extracting text from manuscript...
✓ Extracted 45,234 characters

🔍 Detecting article type...
✓ Article type: Research Article

🤖 Loading AI model: Qwen/Qwen2.5-7B-Instruct...
⏳ This may take a few minutes the first time...
✓ Model loaded successfully

🔑 Extracting 5 key phrases...
✓ Extracted key phrases:
  • machine learning algorithms
  • predictive model performance
  • clinical decision support
  • patient outcome prediction
  • healthcare data analysis

🔬 Searching PubMed database...
✓ Found 87 articles:
  • 'machine learning algorithms': 18 articles
  • 'predictive model performance': 21 articles
  • 'clinical decision support': 15 articles
  • 'patient outcome prediction': 19 articles
  • 'healthcare data analysis': 14 articles

📊 Analyzing manuscript with AI...
⏳ This may take several minutes...
✓ Analysis completed
  • Major points: 3
  • Minor points: 7
  • Other points: 4
  • Suggestions: 8

📝 Generating reports...
✓ Author report: /path/to/manuscript_Author_Report.pdf
✓ Auditor report: /path/to/manuscript_Auditor_Report.pdf

✅ Review completed successfully!
```

**Total time**: ~2-8 minutes

### Step 5: Review Reports

Two reports are generated in the same directory as your manuscript:

#### 1. Author Report (`*_Author_Report.pdf/docx`)
**For**: Manuscript authors
**Contains**:
- Major Points (critical issues)
- Minor Points (improvements needed)
- Other Points (optional suggestions)
- Suggestions for Improvement

**Clean format, no internal details**

#### 2. Auditor Report (`*_Auditor_Report.pdf/docx`)
**For**: Internal verification and auditing
**Contains**:
- All author report content
- Manuscript information (type, length)
- Key phrases extracted
- PubMed search results (article list)
- Full article metadata

**Detailed format for verification**

## Tips & Tricks

### Getting Better Results

1. **Use clear manuscripts**: Well-formatted documents give better results
2. **Choose appropriate model**: 
   - Research papers → Qwen (general)
   - Code/technical → DeepSeek (specialized)
   - Fast processing → Phi-3 (smaller)
3. **Adjust article count**: More PubMed articles = more context (but slower)
4. **Review prompts**: Customize evaluation criteria for your field
5. **Use GPU**: 10-50x faster than CPU

### Troubleshooting

#### "No file selected" error
→ Load a manuscript in the 📄 Manuscript tab first

#### "Invalid JSON format in prompts"
→ Fix JSON syntax in 💬 Prompts tab or click "Reset to Default"

#### Progress stuck at "Loading AI model..."
→ First time only: Wait 1-5 minutes for model download

#### "No articles found in PubMed"
→ Check internet connection
→ Try broader key phrases
→ Manuscript topic might be too specific

#### Out of memory error
→ Use smaller model (Phi-3)
→ Reduce text excerpt length
→ Close other applications
→ Use system with more RAM

### Performance Optimization

#### Faster Processing
- Use GPU (CUDA) if available
- Choose Phi-3 model (smallest, fastest)
- Reduce number of articles to 10-15
- Process shorter manuscripts

#### Better Analysis
- Use Qwen or Llama models (larger)
- Increase articles to 25-30
- Customize prompts for your field
- Review manuscript before submitting

## Advanced Usage

### Batch Processing (Future Feature)

Currently: Process one manuscript at a time
Future: Batch mode for multiple manuscripts

### Custom Evaluation Criteria

Edit `example_prompts.json` and load in application:

```json
{
    "keyphrases": "Extract {num} key phrases focusing on [YOUR FOCUS]...",
    "analysis": "Evaluate specifically for [YOUR CRITERIA]..."
}
```

### Integration with Workflow

1. Receive manuscript
2. Run PRRA analysis
3. Review auditor report
4. Edit/verify evaluation
5. Send author report to author

## Examples

### Example 1: Research Article in Medicine

**Input**: `diabetes_treatment_study.pdf` (8,500 words)
**Settings**: 5 key phrases, 20 articles, Qwen model, PDF output
**Time**: ~4 minutes
**Output**: 
- `diabetes_treatment_study_Author_Report.pdf`
- `diabetes_treatment_study_Auditor_Report.pdf`

**Key phrases extracted**:
- glucose level monitoring
- insulin resistance mechanisms
- type 2 diabetes treatment
- metabolic syndrome factors
- glycemic control strategies

**PubMed articles**: 95 found
**Evaluation**: 3 major, 5 minor, 2 other points, 7 suggestions

### Example 2: Computer Science Review Paper

**Input**: `ml_healthcare_review.docx` (12,000 words)
**Settings**: 7 key phrases, 30 articles, DeepSeek model, DOCX output
**Time**: ~6 minutes
**Output**: Word documents for easy editing

**Result**: Comprehensive evaluation with suggestions for:
- Updating recent references (2024-2025)
- Improving method comparison section
- Adding quantitative metrics
- Restructuring introduction

## FAQ

**Q: Do I need an API key for PubMed?**
A: No, PRRA uses public Entrez API (free, no key required)

**Q: Is my manuscript sent to the internet?**
A: No, only PubMed searches are online. Manuscript stays local.

**Q: Can I use it offline?**
A: Partially. After model download, only PubMed search needs internet.

**Q: How much does it cost?**
A: Free and open source! Only cost is your hardware/electricity.

**Q: Can I process manuscripts in other languages?**
A: Yes, but optimized for English. Other languages may work with custom prompts.

**Q: How accurate is the evaluation?**
A: AI-assisted, not perfect. Always review auditor report and verify suggestions.

**Q: Can I edit the generated reports?**
A: Yes, especially DOCX format. Use as a starting point for your review.

**Q: What if I disagree with the AI evaluation?**
A: The AI is a tool, not replacement. Use your expert judgment.

## Getting Help

- Read `README.md` for overview
- Read `DEVELOPMENT.md` for technical details
- Check `IMPLEMENTATION_SUMMARY.md` for complete feature list
- Open GitHub issue for bugs or questions

## Next Steps

After completing this tutorial:
1. Try with your own manuscripts
2. Experiment with different models
3. Customize prompts for your field
4. Share feedback and suggestions

Happy reviewing! 🎉
