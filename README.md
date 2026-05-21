# Oracle Reports Cyrillic & Greek Font Subsetting Workaround
### A production-grade workaround to bypass hardcoded Base14 PDF Font subsetting blocks in Oracle Reports (10g / E-Business Suite R12.2)

Developed & maintained by [tagtuner](https://github.com/tagtuner)

---

## 🌟 The Challenge
When generating PDF reports in Oracle E-Business Suite containing **Cyrillic (Russian), Greek, or custom Eastern European character sets**, characters often render as boxes, question marks (`?`), or blank characters. 

Standard Oracle support recommends adding TrueType mappings to `uifont.ali` directly. However, in Linux/Unix middle-tiers, **this fails out of the box** due to two severe core architectural restrictions:
1. **X11 Toolkit Failures:** The Oracle Motif Toolkit (`Tk2Motif`) fails to resolve the Arial font because it is not installed in the OS-level X11 font catalog. The engine silently falls back to standard **Courier** (or defaults to the `Symbol` font).
2. **The Base14 Font Subsetting Block:** By the time the instructions reach the PDF driver, the font is registered as Courier. Courier is a **Base14 standard font**, and the Oracle PDF driver has hardcoded instructions that completely **block subsetting or embedding of Base14 fonts** to optimize file size.

---

## 🚀 The Solution (The Base14 Bypass)
This repository contains a simple, production-proven workaround that fools the PDF rendering driver:
1. **Global Metric Mapping:** We map `Arial = courier` globally. This instructs `Tk2Motif` to calculate Arial text layouts using Courier character metrics.
2. **Subset Overriding:** We override the Courier font definition within the `[ PDF:Subset ]` block, mapping all variants of Courier directly to physical **Arial TrueType (`.ttf`) files**!
3. **Environment Isolation:** We enforce standard AutoConfig-safe variables (`TK_ADMIN`, `REPORTS_ENHANCED_SUBSET=YES`, `REPORTS_PATH`) to activate the TrueType subsetting engine.

The PDF driver compiles the metrics as Courier (bypassing layout panics) but **embeds the true Arial TrueType font vectors into the PDF binary**, enabling crisp, gorgeous Cyrillic character renderings with zero visual distortion!

---

## 📂 Repository Contents
* `manual.md`: Detailed technical engineering, diagnostic, and database locking resolution manual.
* `clean_uifont.py`: A Python utility script to comments out duplicate headers inside `uifont.ali` templates and inject subset rules.
* `uifont_template.ali`: A raw template showing the Global and PDF:Subset configuration blocks.
* `custom_ebs_env.env`: An AutoConfig-safe shell script profile extension template.

---

## 🛠️ Step-by-Step Deployment Playbook

### Step 1: Install OS-Level X11 Fonts (Root Access)
The Oracle Reports toolkit needs X11 dpi catalogs registered on the server to measure font layouts.
```bash
# On RHEL / CentOS / Oracle Linux
sudo yum install -y xorg-x11-fonts-75dpi xorg-x11-fonts-100dpi xorg-x11-fonts-misc
xset fp rehash
```

### Step 2: Deploy TrueType Font Files
Upload standard, lowercase Arial font files to your `$ORACLE_HOME/guicommon/tk/admin/` directory:
* `arial.ttf` (Arial Regular)
* `arialbd.ttf` (Arial Bold)
* `ariali.ttf` (Arial Italic)
* `arialbi.ttf` (Arial Bold Italic)

Set permissions to read-only for security:
```bash
chmod 644 $ORACLE_HOME/guicommon/tk/admin/arial*.ttf
```

### Step 3: Run the `uifont.ali` Patches
Oracle Reports often contains duplicate `[ PDF:Subset ]` headers in its configurations due to template updates, which neutralizes rules. Execute our Python utility to clean and patch both the `admin` and `mesg` folders:
```bash
export ORACLE_HOME=/your/middleware/10.1.2/home
python clean_uifont.py
```

### Step 4: Inject AutoConfig-Safe Environment Variables
To ensure the changes survive AutoConfig runs, save the environment variables in a custom shell profile script named `custom<CONTEXT_NAME>.env` inside `$INST_TOP/appl/admin/`:
```bash
export TK_ADMIN=$ORACLE_HOME/guicommon/tk/admin
export REPORTS_ENHANCED_SUBSET=YES
export REPORTS_PATH=$TK_ADMIN:$REPORTS_PATH
```
Set executable permissions:
```bash
chmod 755 $INST_TOP/appl/admin/custom*.env
```

### Step 5: Restart Middleware & Services
Sourcing the new environment, restart your Concurrent Managers and HTTP/OPMN services:
```bash
adcmctl.sh stop
adopmnctl.sh stop
adopmnctl.sh start
adcmctl.sh start
```

---

## 📊 Verification of Success
Submit your PDF reports. If successfully subsetted, the output PDF size will grow to **~11 KB** (instead of standard ~990 bytes) and the binary PDF structure will contain:
```text
/BaseFont /AAATCB+ArialBold
/Encoding /Identity-H
```
* `/Identity-H` indicates 2-byte Unicode encoding is active, which guarantees proper rendering for Cyrillic and Greek layouts.

---
*Contributions, suggestions, and PRs are highly welcome! Made with ❤️ by [tagtuner](https://github.com/tagtuner).*
