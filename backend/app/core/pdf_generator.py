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

def build_header_section(elements, candidate_name, role_title, score_total, score_label, generated_at):
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=PRIMARY,
        alignment=TA_LEFT,
        spaceAfter=10
    )
    
    elements.append(Paragraph("ATS Resume Analysis Report", title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=20))
    
    header_data = [
        [
            Paragraph(f"<b>{candidate_name.upper()}</b>", ParagraphStyle('Name', fontSize=18, textColor=PRIMARY)),
            Paragraph(f"<b>Score: {int(score_total)}/100</b>", ParagraphStyle('Score', fontSize=22, textColor=get_score_color(score_total), alignment=TA_RIGHT))
        ],
        [
            Paragraph(f"Role: {role_title}", ParagraphStyle('Role', fontSize=12, textColor=TEXT_SECONDARY)),
            Paragraph(f"{score_label}", ParagraphStyle('Label', fontSize=14, textColor=get_score_color(score_total), alignment=TA_RIGHT))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"Generated on: {generated_at}", ParagraphStyle('Date', fontSize=8, textColor=TEXT_SECONDARY)))
    elements.append(Spacer(1, 1*cm))

def build_score_breakdown_section(elements, score_breakdown):
    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>Score Breakdown</b>", styles['Heading2']))
    
    data = [["Component", "Score", "Visual"]]
    for key, val in score_breakdown.items():
        if key == "total": continue
        label = key.replace("_", " ").title()
        score = int(val)
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        data.append([label, f"{score}/100", bar])
        
    table = Table(data, colWidths=[2*inch, 1*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('TEXTCOLOR', (0,0), (-1,0), PRIMARY),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('FONTSIZE', (2,1), (2,-1), 12),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 1*cm))

def build_skills_section(elements, matched_skills):
    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>Skills Analysis</b>", styles['Heading2']))
    
    data = [
        [Paragraph("<b>Matched Skills ✓</b>", ParagraphStyle('M', textColor=SUCCESS)), 
         Paragraph("<b>Missing Skills ✗</b>", ParagraphStyle('Miss', textColor=DANGER))]
    ]
    
    req_matched = matched_skills.get("required_matched", [])
    req_missing = matched_skills.get("required_missing", [])
    
    max_len = max(len(req_matched), len(req_missing))
    for i in range(max_len):
        m = req_matched[i] if i < len(req_matched) else ""
        miss = req_missing[i] if i < len(req_missing) else ""
        data.append([f"• {m}" if m else "", f"• {miss}" if miss else ""])
        
    table = Table(data, colWidths=[3.1*inch, 3.1*inch])
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
    ]))
    elements.append(table)
    
    # Preferred Skills
    elements.append(Spacer(1, 0.5*cm))
    pref_m = ", ".join(matched_skills.get("preferred_matched", []))
    pref_miss = ", ".join(matched_skills.get("preferred_missing", []))
    
    elements.append(Paragraph(f"<b>Preferred Matched:</b> <font color='#10B981'>{pref_m if pref_m else 'None'}</font>", styles['BodyText']))
    elements.append(Paragraph(f"<b>Preferred Missing:</b> <font color='#F59E0B'>{pref_miss if pref_miss else 'None'}</font>", styles['BodyText']))
    elements.append(Spacer(1, 1*cm))

def build_gaps_section(elements, gaps):
    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>Gap Analysis</b>", styles['Heading2']))
    
    exp_gap = gaps.get("experience_gap", {})
    if exp_gap.get("has_gap"):
        text = f"Experience Gap Detected: {exp_gap.get('gap_months')} months missing."
        elements.append(Paragraph(text, ParagraphStyle('Gap', backColor=WARNING, borderPadding=5, textColor=white)))
    else:
        elements.append(Paragraph("Experience requirement met ✓", ParagraphStyle('NoGap', backColor=SUCCESS, borderPadding=5, textColor=white)))
    
    elements.append(Spacer(1, 0.5*cm))
    weak_bullets = gaps.get("weak_bullets", [])
    if not weak_bullets:
        elements.append(Paragraph("No weak bullets detected ✓", ParagraphStyle('S', textColor=SUCCESS)))
    else:
        elements.append(Paragraph(f"Detected {len(weak_bullets)} weak bullets:", styles['BodyText']))
        for wb in weak_bullets:
            elements.append(Paragraph(f"• <i>{wb['bullet']}</i>", styles['Italic']))
            elements.append(Paragraph(f"  Issue: {', '.join(wb['issues'])}", ParagraphStyle('I', fontSize=9, textColor=DANGER)))
            
    elements.append(Spacer(1, 1*cm))

def build_enhancements_section(elements, enhancements):
    if not enhancements: return
    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>Resume Enhancements</b>", styles['Heading2']))
    
    for enh in enhancements:
        elements.append(Paragraph("<b>BEFORE:</b>", ParagraphStyle('B', textColor=DANGER, fontSize=10)))
        elements.append(Paragraph(enh['original'], styles['BodyText']))
        elements.append(Paragraph("<b>AFTER:</b>", ParagraphStyle('A', textColor=SUCCESS, fontSize=10)))
        elements.append(Paragraph(enh['enhanced'], styles['BodyText']))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=5, spaceAfter=5))
        
    elements.append(Spacer(1, 1*cm))

def build_learning_path_section(elements, learning_path):
    if not learning_path: return
    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>Learning Roadmap</b>", styles['Heading2']))
    elements.append(Paragraph(f"<i>{learning_path.get('summary', '')}</i>", styles['BodyText']))
    
    order = " → ".join(learning_path.get('recommended_order', []))
    if order:
        elements.append(Paragraph(f"Recommended order: {order}", styles['BodyText']))
        
    elements.append(Spacer(1, 0.5*cm))
    for skill_data in learning_path.get("priority_skills", []):
        elements.append(Paragraph(f"<b>{skill_data['skill']}</b> ({skill_data['estimated_weeks']} weeks)", styles['Heading3']))
        for res in skill_data.get('resources', [])[:2]:
            elements.append(Paragraph(f"• {res['name']} ({res['platform']}) - {res['url']}", ParagraphStyle('Link', fontSize=9, textColor=ACCENT)))
            
    elements.append(Spacer(1, 1*cm))

def build_feedback_section(elements, feedback_text):
    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>Career Coach Feedback</b>", styles['Heading2']))
    
    elements.append(Paragraph(feedback_text.replace("\n", "<br/>"), 
                             ParagraphStyle('Feedback', 
                                            backColor=LIGHT_BG, 
                                            borderPadding=10, 
                                            leading=14,
                                            fontName='Helvetica-Oblique')))
    elements.append(Spacer(1, 1*cm))

def build_formatting_section(elements, formatting):
    if not formatting: return
    styles = getSampleStyleSheet()
    elements.append(Paragraph("<b>ATS Compliance</b>", styles['Heading2']))
    
    elements.append(Paragraph(f"Compliance Score: <b>{int(formatting['compliance_score'])}%</b>", 
                             ParagraphStyle('P', textColor=get_score_color(formatting['compliance_score']))))
    
    ci = formatting.get("contact_info", {})
    checklist = []
    for k, v in ci.items():
        symbol = "✓" if v else "✗"
        color = "#10B981" if v else "#EF4444"
        checklist.append(f"<font color='{color}'>{symbol} {k.title()}</font>")
    
    elements.append(Paragraph(" | ".join(checklist), styles['BodyText']))
    
    elements.append(Spacer(1, 0.5*cm))
    for issue in formatting.get("ats_issues", []):
        color = DANGER if issue['severity'] == 'high' else WARNING
        elements.append(Paragraph(f"<b>[{issue['severity'].upper()}]</b> {issue['issue']}: {issue['suggestion']}", 
                                 ParagraphStyle('Issue', fontSize=9, textColor=color)))

def generate_ats_report(analysis_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    
    # Extract data
    score = analysis_data.get("score", {})
    candidate_name = analysis_data.get("candidate_name", "Candidate")
    role_title = analysis_data.get("role_title", "Unknown Role")
    
    build_header_section(elements, candidate_name, role_title, 
                        score.get("total", 0), 
                        analysis_data.get("score_label", ""), 
                        datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    build_score_breakdown_section(elements, score)
    build_skills_section(elements, analysis_data.get("matched_skills", {}))
    build_gaps_section(elements, analysis_data.get("gaps", {}))
    build_enhancements_section(elements, analysis_data.get("enhancements", []))
    build_learning_path_section(elements, analysis_data.get("learning_path", {}))
    build_feedback_section(elements, analysis_data.get("feedback", "No feedback provided."))
    build_formatting_section(elements, analysis_data.get("formatting", {}))
    
    elements.append(Spacer(1, 1*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elements.append(Paragraph("Generated by ATS Resume Scanner", 
                             ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=8, textColor=TEXT_SECONDARY)))
    
    doc.build(elements)
    return buffer.getvalue()
