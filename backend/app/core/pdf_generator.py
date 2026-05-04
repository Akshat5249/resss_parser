from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import (
    HexColor, black, white, grey
)
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime

# Professional ATS Theme Colors
PRIMARY = HexColor("#2D3748")      # Dark Navy
ACCENT = HexColor("#4F46E5")       # Indigo
SUCCESS = HexColor("#10B981")      # Green
WARNING = HexColor("#F59E0B")      # Amber
DANGER = HexColor("#EF4444")       # Red
LIGHT_BG = HexColor("#F8FAFC")     # Light Grey BG
BORDER = HexColor("#E2E8F0")       # Border Grey
TEXT_SECONDARY = HexColor("#64748B") # Muted Text

def get_score_color(score: int) -> HexColor:
    if score >= 80: return SUCCESS
    if score >= 60: return ACCENT
    if score >= 40: return WARNING
    return DANGER

def build_header_section(elements, candidate_name, role_title, score_total, score_label, generated_at, styles):
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph("ATS Resume Analysis Report", title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=20))
    
    header_data = [
        [
            Paragraph(f"<b>{candidate_name.upper()}</b>", ParagraphStyle('Name', fontSize=18, textColor=PRIMARY, fontName='Helvetica-Bold')),
            Paragraph(f"<b>Score: {int(score_total)}/100</b>", ParagraphStyle('Score', fontSize=22, textColor=get_score_color(score_total), alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        ],
        [
            Paragraph(f"Role: {role_title or 'Baseline Analysis'}", ParagraphStyle('Role', fontSize=12, textColor=TEXT_SECONDARY, fontName='Helvetica')),
            Paragraph(f"{score_label}", ParagraphStyle('Label', fontSize=14, textColor=get_score_color(score_total), alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(header_table)
    
    # PDF FIX 2E: Add baseline note if no role title
    if not role_title or role_title == "Resume Analysis":
        elements.append(Paragraph(
            "Baseline analysis — no job description provided",
            ParagraphStyle("note",
                fontSize=9,
                textColor=HexColor("#9CA3AF"),
                fontName="Helvetica-Oblique",
                alignment=TA_CENTER
            )
        ))
        elements.append(Spacer(1, 4))
        
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"Generated on: {generated_at}", ParagraphStyle('Date', fontSize=8, textColor=TEXT_SECONDARY, fontName='Helvetica')))
    elements.append(Spacer(1, 1*cm))

def build_score_breakdown_section(elements, score_breakdown, styles):
    # PDF FIX 1: Simplify to one table with ASCII bars
    score_breakdown = score_breakdown or {}
    
    def get_color(score):
        s = float(score or 0)
        if s >= 70: return HexColor("#10B981")
        if s >= 40: return HexColor("#4F46E5")
        return HexColor("#F59E0B")
    
    def get_bar(score):
        s = max(0, min(100, int(float(score or 0))))
        filled = s // 10
        # Use ASCII chars that work in Helvetica
        return "[" + "=" * filled + "-" * (10 - filled) + "]"
    
    items = [
        ("Skill Match",  "40%", score_breakdown.get("skill_match", 0) or 0),
        ("Experience",   "25%", score_breakdown.get("experience", 0) or 0),
        ("Projects",     "15%", score_breakdown.get("projects", 0) or 0),
        ("Education",    "10%", score_breakdown.get("education", 0) or 0),
        ("Formatting",   "10%", score_breakdown.get("formatting", 0) or 0),
    ]
    
    data = [["Component", "Weight", "Bar", "Score"]]
    for label, weight, score in items:
        data.append([
            label,
            weight,
            get_bar(score),
            f"{int(round(float(score)))}/100"
        ])
    
    table = Table(data, colWidths=[120, 45, 130, 65])
    
    style = TableStyle([
        # Header
        ("BACKGROUND", (0,0), (-1,0), HexColor("#F8FAFC")),
        ("TEXTCOLOR",  (0,0), (-1,0), HexColor("#64748B")),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 9),
        ("TOPPADDING", (0,0), (-1,0), 8),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        
        # Data rows
        ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,1), (-1,-1), 10),
        ("TOPPADDING", (0,1), (-1,-1), 7),
        ("BOTTOMPADDING", (0,1), (-1,-1), 7),
        
        # Grid
        ("LINEBELOW", (0,0), (-1,0), 0.5, HexColor("#E2E8F0")),
        ("LINEBELOW", (0,1), (-1,-1), 0.3, HexColor("#F1F5F9")),
        
        # Alignment
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ])
    
    # Color score column per row
    for i, (label, weight, score) in enumerate(items):
        row = i + 1
        color = get_color(score)
        style.add("TEXTCOLOR", (3,row), (3,row), color)
        style.add("FONTNAME", (3,row), (3,row), "Helvetica-Bold")
    
    table.setStyle(style)
    elements.append(Paragraph("<b>Score Breakdown</b>", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=14, spaceAfter=10)))
    elements.append(table)
    elements.append(Spacer(1, 12))

def build_skills_section(elements, matched_skills, styles):
    matched_skills = matched_skills or {}
    required_matched = matched_skills.get("required_matched", []) or []
    required_missing = matched_skills.get("required_missing", []) or []
    
    elements.append(Paragraph("<b>Skills Analysis</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold')))
    
    # PDF FIX 2A: Handle empty gracefully
    if not required_matched and not required_missing:
        elements.append(Paragraph(
            "Skills analysis available after running a JD-matched analysis.",
            styles["body_gray"]
        ))
        elements.append(Spacer(1, 1*cm))
        return
    
    data = [
        [Paragraph("<b>Matched Skills ✓</b>", ParagraphStyle('M', textColor=SUCCESS, fontName='Helvetica-Bold')), 
         Paragraph("<b>Missing Skills ✗</b>", ParagraphStyle('Miss', textColor=DANGER, fontName='Helvetica-Bold'))]
    ]
    
    max_len = max(len(required_matched), len(required_missing))
    for i in range(max_len):
        m = required_matched[i] if i < len(required_matched) else ""
        miss = required_missing[i] if i < len(required_missing) else ""
        data.append([f"• {m}" if m else "", f"• {miss}" if miss else ""])
        
    table = Table(data, colWidths=[3.1*inch, 3.1*inch])
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
    ]))
    elements.append(table)
    
    # Preferred Skills
    elements.append(Spacer(1, 0.5*cm))
    pref_m = ", ".join(matched_skills.get("preferred_matched", []) or [])
    pref_miss = ", ".join(matched_skills.get("preferred_missing", []) or [])
    
    elements.append(Paragraph(f"<b>Preferred Matched:</b> <font color='#10B981'>{pref_m if pref_m else 'None'}</font>", styles['BodyText']))
    elements.append(Paragraph(f"<b>Preferred Missing:</b> <font color='#F59E0B'>{pref_miss if pref_miss else 'None'}</font>", styles['BodyText']))
    elements.append(Spacer(1, 1*cm))

def build_gaps_section(elements, gaps, styles):
    gaps = gaps or {}
    elements.append(Paragraph("<b>Gap Analysis</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold')))
    
    exp_gap = gaps.get("experience_gap", {}) or {}
    if exp_gap.get("has_gap", False):
        text = f"Experience Gap Detected: {exp_gap.get('gap_months', 0)} months missing."
        elements.append(Paragraph(text, ParagraphStyle('Gap', backColor=WARNING, borderPadding=5, textColor=white, fontName='Helvetica-Bold')))
    else:
        elements.append(Paragraph("Experience requirement met ✓", ParagraphStyle('NoGap', backColor=SUCCESS, borderPadding=5, textColor=white, fontName='Helvetica-Bold')))
    
    elements.append(Spacer(1, 0.5*cm))
    weak_bullets = gaps.get("weak_bullets", []) or []
    if not weak_bullets:
        elements.append(Paragraph("No weak bullets detected ✓", ParagraphStyle('S', textColor=SUCCESS, fontName='Helvetica')))
    else:
        elements.append(Paragraph(f"Detected {len(weak_bullets)} weak bullets:", styles['BodyText']))
        for wb in weak_bullets:
            bullet_text = wb.get('bullet', '')
            issues = ", ".join(wb.get('issues', []))
            elements.append(Paragraph(f"• <i>{bullet_text}</i>", styles['Italic']))
            elements.append(Paragraph(f"  Issue: {issues}", ParagraphStyle('I', fontSize=9, textColor=DANGER, fontName='Helvetica')))
            
    elements.append(Spacer(1, 1*cm))

def build_enhancements_section(elements, enhancements, styles):
    enhancements = enhancements or []
    if not enhancements:
        return

    elements.append(Paragraph("<b>Resume Enhancements</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold')))
    for enh in enhancements:
        elements.append(Paragraph("<b>BEFORE:</b>", ParagraphStyle('B', textColor=DANGER, fontSize=10, fontName='Helvetica-Bold')))
        elements.append(Paragraph(enh.get('original', ''), styles['BodyText']))
        elements.append(Paragraph("<b>AFTER:</b>", ParagraphStyle('A', textColor=SUCCESS, fontSize=10, fontName='Helvetica-Bold')))
        elements.append(Paragraph(enh.get('enhanced', ''), styles['BodyText']))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=5, spaceAfter=5))
        
    elements.append(Spacer(1, 1*cm))

def build_learning_path_section(elements, learning_path, styles):
    learning_path = learning_path or {}
    priority_skills = learning_path.get("priority_skills", []) or []
    
    elements.append(Paragraph("<b>Learning Roadmap</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold')))
    
    # PDF FIX 2C: Handle empty gracefully
    if not priority_skills:
        elements.append(Paragraph(
            "Learning roadmap available after running a JD-matched analysis.",
            styles["body_gray"]
        ))
        elements.append(Spacer(1, 1*cm))
        return

    summary = learning_path.get("summary", "") or ""
    elements.append(Paragraph(f"<i>{summary}</i>", styles['BodyText']))
    
    order = " → ".join(learning_path.get('recommended_order', []) or [])
    if order:
        elements.append(Paragraph(f"Recommended order: {order}", styles['BodyText']))
        
    elements.append(Spacer(1, 0.5*cm))
    for skill_data in priority_skills:
        skill_name = skill_data.get('skill', '')
        elements.append(Paragraph(f"<b>{skill_name}</b> ({skill_data.get('estimated_weeks', 0)} weeks)", ParagraphStyle('H3', parent=styles['Heading3'], fontName='Helvetica-Bold')))
        for res in skill_data.get('resources', [])[:2]:
            url = res.get('url', '')
            name = res.get('name', '')
            platform = res.get('platform', '')
            
            if "google.com/search" in url:
                display_url = f"Search: {skill_name} tutorial on YouTube"
            else:
                display_url = url
                
            elements.append(Paragraph(f"• {name} ({platform}) - {display_url}", ParagraphStyle('Link', fontSize=9, textColor=ACCENT, fontName='Helvetica')))
            
    elements.append(Spacer(1, 1*cm))

def build_feedback_section(elements, feedback_text, styles):
    feedback_text = feedback_text or ""
    elements.append(Paragraph("<b>Career Coach Feedback</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold')))
    
    # PDF FIX 2B: Handle empty gracefully
    if not feedback_text.strip() or feedback_text == "No feedback generated.":
        elements.append(Paragraph(
            "Career coaching feedback available after running a JD-matched analysis.",
            styles["body_gray"]
        ))
        elements.append(Spacer(1, 1*cm))
        return
        
    elements.append(Paragraph(feedback_text.replace("\n", "<br/>"), 
                             ParagraphStyle('Feedback', 
                                            backColor=LIGHT_BG, 
                                            borderPadding=10, 
                                            leading=14,
                                            fontName='Helvetica-Oblique')))
    elements.append(Spacer(1, 1*cm))

def build_formatting_section(elements, formatting, styles):
    formatting = formatting or {}
    elements.append(Paragraph("<b>ATS Compliance</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold')))
    
    compliance_score = formatting.get("compliance_score", 100) or 100
    elements.append(Paragraph(f"Compliance Score: <b>{int(compliance_score)}%</b>", 
                             ParagraphStyle('P', textColor=get_score_color(compliance_score), fontName='Helvetica-Bold')))
    
    contact_info = formatting.get("contact_info", {}) or {}
    checklist = []
    for k, v in contact_info.items():
        symbol = "✓" if v else "✗"
        color = "#10B981" if v else "#EF4444"
        checklist.append(f"<font color='{color}'>{symbol} {k.title()}</font>")
    
    elements.append(Paragraph(" | ".join(checklist), styles['BodyText']))
    
    elements.append(Spacer(1, 0.5*cm))
    for issue in (formatting.get("ats_issues", []) or []):
        color = DANGER if issue.get('severity') == 'high' else WARNING
        elements.append(Paragraph(f"<b>[{issue.get('severity', 'low').upper()}]</b> {issue.get('issue', '')}: {issue.get('suggestion', '')}", 
                                 ParagraphStyle('Issue', fontSize=9, textColor=color, fontName='Helvetica')))

def generate_ats_report(analysis_data: dict) -> bytes:
    if not analysis_data:
        raise ValueError("analysis_data is None or empty")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # PDF FIX 2D: Add body_gray style
    styles.add(ParagraphStyle(
        "body_gray",
        parent=styles["Normal"],
        textColor=HexColor("#9CA3AF"),
        fontSize=10,
        fontName="Helvetica-Oblique",
        leading=16
    ))
    
    # Extract data with safe defaults
    candidate_name = analysis_data.get("candidate_name", "Candidate")
    role_title = analysis_data.get("role_title", "")
    score_total = analysis_data.get("score_total", 0) or 0
    score_label = analysis_data.get("score_label", "Scanned")
    score = analysis_data.get("score", {}) or {}
    matched_skills = analysis_data.get("matched_skills", {}) or {}
    gaps = analysis_data.get("gaps", {}) or {}
    enhancements = analysis_data.get("enhancements", []) or []
    learning_path = analysis_data.get("learning_path", {}) or {}
    feedback = analysis_data.get("feedback", "") or ""
    formatting = analysis_data.get("formatting", {}) or {}
    
    build_header_section(elements, candidate_name, role_title, 
                        score_total, score_label, 
                        datetime.now().strftime("%Y-%m-%d %H:%M"), styles)
    
    # PDF FIX 1: Ensure called exactly ONCE
    build_score_breakdown_section(elements, score, styles)
    
    build_skills_section(elements, matched_skills, styles)
    build_gaps_section(elements, gaps, styles)
    build_enhancements_section(elements, enhancements, styles)
    build_learning_path_section(elements, learning_path, styles)
    build_feedback_section(elements, feedback, styles)
    build_formatting_section(elements, formatting, styles)
    
    elements.append(Spacer(1, 1*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Paragraph("Generated by ATS Resume Scanner", 
                             ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=8, textColor=TEXT_SECONDARY, fontName='Helvetica')))
    
    doc.build(elements)
    return buffer.getvalue()
