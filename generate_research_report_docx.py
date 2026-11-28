import json
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUT_DOCX = Path("Cyber_Secure_Predictive_Maintenance_Research_Methodology_Report.docx")

# Palette
C_NAVY = RGBColor(0x0F, 0x29, 0x42)
C_DARK_BLUE = RGBColor(0x1E, 0x3A, 0x8A)
C_BLUE = RGBColor(0x02, 0x84, 0xC7)
C_MUTED = RGBColor(0x47, 0x55, 0x69)
C_TEXT = RGBColor(0x1E, 0x29, 0x3B)
C_AMBER = RGBColor(0xB4, 0x53, 0x09)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def set_cell_shading(cell, hex_color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_page_number_field(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls("w"))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls("w"))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def add_p(doc, text="", bold=False, italic=False, size=11, color=C_TEXT, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, space_before=0, font_name="Calibri"):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if text:
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.name = font_name
        r.font.size = Pt(size)
        r.font.color.rgb = color
    return p


def add_bullet(doc, lead, body, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if lead:
        r1 = p.add_run(lead)
        r1.bold = True
        r1.font.name = "Calibri"
        r1.font.size = Pt(size)
        r1.font.color.rgb = C_NAVY
    r2 = p.add_run(body)
    r2.font.name = "Calibri"
    r2.font.size = Pt(size)
    r2.font.color.rgb = C_TEXT
    return p


def add_h1(doc, text, page_break=True):
    if page_break:
        doc.add_page_break()
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(16)
    r.font.color.rgb = C_NAVY
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="0284C7"/></w:pBdr>')
    pPr.append(pBdr)
    return p


def add_h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.color.rgb = C_DARK_BLUE
    return p


def add_h3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(11.5)
    r.font.color.rgb = C_BLUE
    return p


def add_callout_box(doc, title, body, fill_hex="EFF6FF", border_hex="0284C7", title_rgb=C_NAVY):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.3)
    set_cell_shading(cell, fill_hex)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    rt = p.add_run(title + "\n")
    rt.bold = True
    rt.font.name = "Calibri"
    rt.font.size = Pt(10.5)
    rt.font.color.rgb = title_rgb
    rb = p.add_run(body)
    rb.font.name = "Calibri"
    rb.font.size = Pt(10)
    rb.font.color.rgb = C_TEXT
    add_p(doc, "", space_after=4)


def add_styled_table(doc, headers, rows, caption=None, col_widths=None, font_size=9.5):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)

    # Header row
    hdr_cells = tbl.rows[0].cells
    trPr = tbl.rows[0]._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    for j, h_text in enumerate(headers):
        cell = hdr_cells[j]
        if col_widths:
            cell.width = Inches(col_widths[j])
        set_cell_shading(cell, "0F2942")
        set_cell_margins(cell, top=90, bottom=90, left=110, right=110)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(font_size)
        r.font.color.rgb = C_WHITE

    # Data rows
    for i, row_data in enumerate(rows):
        row_cells = tbl.rows[i + 1].cells
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row_cells[j]
            if col_widths:
                cell.width = Inches(col_widths[j])
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=75, bottom=75, left=110, right=110)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.12
            r = p.add_run(str(val))
            r.font.name = "Calibri"
            r.font.size = Pt(font_size)
            if j == 0:
                r.bold = True
                r.font.color.rgb = C_NAVY
            else:
                r.font.color.rgb = C_TEXT

    if caption:
        p_cap = add_p(doc, caption, bold=True, italic=True, size=9.5, color=C_MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=8)
    else:
        add_p(doc, "", space_after=6)
    return tbl


def add_embedded_figure(doc, img_path, caption, width_in=6.2):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.paragraph_format.keep_with_next = True
    run = p_img.add_run()
    run.add_picture(str(img_path), width=Inches(width_in))
    add_p(doc, caption, bold=True, italic=True, size=9.5, color=C_MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)


def add_image_placeholder(doc, fig_label, title, what_belongs, steps_for_friends, compact=False):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.2)
    set_cell_shading(cell, "FFFBEB")
    pad_tb = 140 if compact else 240
    set_cell_margins(cell, top=pad_tb, bottom=pad_tb, left=200, right=200)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="dashed" w:sz="14" w:space="0" w:color="D97706"/>'
        f'<w:bottom w:val="dashed" w:sz="14" w:space="0" w:color="D97706"/>'
        f'<w:left w:val="dashed" w:sz="14" w:space="0" w:color="D97706"/>'
        f'<w:right w:val="dashed" w:sz="14" w:space="0" w:color="D97706"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15

    r_hdr = p.add_run(f"[ IMAGE PLACEHOLDER — LEAVE GAP HERE FOR TEAMMATES TO INSERT {fig_label.upper()} ]\n")
    r_hdr.bold = True
    r_hdr.font.name = "Calibri"
    r_hdr.font.size = Pt(10.5)
    r_hdr.font.color.rgb = C_AMBER

    r_w1 = p.add_run("What Image Belongs Here: ")
    r_w1.bold = True
    r_w1.font.name = "Calibri"
    r_w1.font.size = Pt(9.5)
    r_w1.font.color.rgb = C_NAVY
    r_w2 = p.add_run(what_belongs + "\n")
    r_w2.font.name = "Calibri"
    r_w2.font.size = Pt(9.5)
    r_w2.font.color.rgb = C_TEXT

    r_s1 = p.add_run("How Teammates Can Capture / Create It:\n")
    r_s1.bold = True
    r_s1.font.name = "Calibri"
    r_s1.font.size = Pt(9.5)
    r_s1.font.color.rgb = C_NAVY
    r_s2 = p.add_run(steps_for_friends)
    r_s2.font.name = "Calibri"
    r_s2.font.size = Pt(9.2)
    r_s2.font.color.rgb = C_TEXT

    if not compact:
        p_gap = cell.add_paragraph()
        p_gap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_gap.paragraph_format.space_before = Pt(10)
        p_gap.paragraph_format.space_after = Pt(4)
        rg = p_gap.add_run("<<<  PASTE IMAGE / SCREENSHOT HERE (Recommended width: 6.0 inches, 16:9 widescreen)  >>>")
        rg.bold = True
        rg.italic = True
        rg.font.name = "Calibri"
        rg.font.size = Pt(9.5)
        rg.font.color.rgb = C_AMBER

    if fig_label.lower().startswith("figure"):
        add_p(doc, f"{fig_label}: {title}", bold=True, italic=True, size=9.5, color=C_MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=10)
    else:
        add_p(doc, "", space_after=6)


def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.3)
    set_cell_shading(cell, "F1F5F9")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    set_table_borders(tbl, color="CBD5E1", sz="4")
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(code_text)
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = C_TEXT
    add_p(doc, "", space_after=6)


def build_report():
    with open("model_evaluation_summary.json", "r", encoding="utf-8") as f:
        eval_sum = json.load(f)
    with open("case_studies/case_study_summary.json", "r", encoding="utf-8") as f:
        cs_sum = json.load(f)

    doc = Document()

    # Configure page setup (Letter/A4 standard 1-inch margins)
    for sec in doc.sections:
        sec.top_margin = Inches(0.95)
        sec.bottom_margin = Inches(0.95)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        sec.different_first_page_header_footer = True

        # Header (non-cover pages)
        hdr = sec.header.paragraphs[0]
        hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rh = hdr.add_run("Cyber-Secure Predictive Maintenance for Oil & Gas Wells  |  Research Methodology Project")
        rh.font.name = "Calibri"
        rh.font.size = Pt(8.5)
        rh.font.color.rgb = C_MUTED

        # Footer with page number
        ftr = sec.footer.paragraphs[0]
        ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rf1 = ftr.add_run("B.Tech Research Methodology Project Report  |  School of Computer Science, UPES Dehradun     |     Page ")
        rf1.font.name = "Calibri"
        rf1.font.size = Pt(8.5)
        rf1.font.color.rgb = C_MUTED
        rf_pg = ftr.add_run()
        rf_pg.font.name = "Calibri"
        rf_pg.font.size = Pt(8.5)
        rf_pg.font.color.rgb = C_MUTED
        add_page_number_field(rf_pg)

    # Set default Normal style
    normal_st = doc.styles["Normal"]
    normal_st.font.name = "Calibri"
    normal_st.font.size = Pt(11)

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    add_p(doc, "UNIVERSITY OF PETROLEUM & ENERGY STUDIES", bold=True, size=15, color=C_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=2)
    add_p(doc, "School of Computer Science  |  Department of Systemics\nBidholi, Via Prem Nagar, Dehradun, Uttarakhand – 248007",
          size=10.5, color=C_MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_image_placeholder(
        doc,
        fig_label="UPES Logo",
        title="Official University Logo",
        what_belongs="Official UPES (University of Petroleum & Energy Studies) high-resolution PNG emblem.",
        steps_for_friends="1. Download the official UPES logo PNG from the UPES student portal or your previous report.\n2. Delete this box and paste the logo centered at 1.8 inches width.",
        compact=True,
    )

    add_p(doc, "CYBER-SECURE PREDICTIVE MAINTENANCE\nFOR OIL & GAS WELLS",
          bold=True, size=20, color=C_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=6)
    add_p(doc, "Integration of Petroleum Engineering Domain Knowledge, Dual-Layer Machine Learning,\nand SCADA/OT Measurement-Anomaly Detection",
          bold=True, italic=True, size=11.5, color=C_BLUE, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    add_p(doc, "A Research Methodology Project Report (7th Semester)\nsubmitted in partial fulfillment of the requirements for the award of the degree of\nBACHELOR OF TECHNOLOGY\nin Computer Science and Engineering\n(Specialization: Cybersecurity & Digital Forensics)",
          size=10.5, color=C_TEXT, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)

    add_p(doc, "Submitted By:", bold=True, size=10.5, color=C_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_styled_table(
        doc,
        ["Student Name", "SAP ID / Roll No."],
        [
            ["Rishi Kumar", "500126773"],
            ["[Teammate 2 Name]", "[SAP ID]"],
            ["[Teammate 3 Name]", "[SAP ID]"],
            ["[Teammate 4 Name]", "[SAP ID]"],
        ],
        col_widths=[3.2, 2.4],
    )

    add_p(doc, "Under the Guidance & Mentorship of:", bold=True, size=10.5, color=C_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
    add_styled_table(
        doc,
        ["Faculty / Supervisor Name", "Designation & Role"],
        [
            ["[Project Mentor / Guide Name]", "Project Guide & Research Methodology Supervisor, SoCS, UPES"],
            ["[Internal Evaluator Name]", "Internal Faculty Reviewer, School of Computer Science, UPES"],
        ],
        col_widths=[2.6, 3.6],
    )

    add_p(doc, "School of Computer Science, UPES Dehradun\nAcademic Session: 2026–2027 (7th Semester — November 2026)",
          bold=True, size=10.5, color=C_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=4)

    # =========================================================================
    # CANDIDATE'S DECLARATION & CERTIFICATE OF APPROVAL
    # =========================================================================
    add_h1(doc, "CANDIDATE'S DECLARATION", page_break=True)
    add_p(
        doc,
        'Statement of Originality: We hereby declare that the 7th Semester Research Methodology Project work entitled '
        '"Cyber-Secure Predictive Maintenance for Oil & Gas Wells: Integration of Petroleum Engineering Domain Knowledge, '
        'Dual-Layer Machine Learning, and SCADA/OT Measurement-Anomaly Detection" submitted in partial fulfillment of the '
        'requirements for the award of the Degree of Bachelor of Technology in Computer Science and Engineering '
        '(Specialization: Cybersecurity & Digital Forensics) to the School of Computer Science, University of Petroleum & '
        'Energy Studies (UPES), Dehradun, is an authentic and original record of our research and engineering work carried out '
        'during the 7th Semester academic session (2026–2027) under the continuous guidance of [Project Mentor / Guide Name].'
    )
    add_p(
        doc,
        "We affirm that the research methodology, physics-informed SCADA telemetry synthesis, dual-layer machine learning "
        "pipelines, reconstructed oil and gas case-study simulations, and custom web dashboard presented in this report are the "
        "outcome of our own investigation and implementation. All external academic papers, technical standards, and official "
        "incident investigation reports have been formally cited, and illustrative simulation parameters have been explicitly "
        "distinguished from documented historical incident facts."
    )
    add_styled_table(
        doc,
        ["Candidate Name", "SAP ID / Roll No.", "Signature"],
        [
            ["Rishi Kumar", "500126773", "_______________________"],
            ["[Teammate 2 Name]", "[SAP ID]", "_______________________"],
            ["[Teammate 3 Name]", "[SAP ID]", "_______________________"],
            ["[Teammate 4 Name]", "[SAP ID]", "_______________________"],
        ],
        col_widths=[2.4, 1.8, 2.0],
    )

    add_h1(doc, "CERTIFICATE OF APPROVAL", page_break=False)
    add_p(
        doc,
        'This is to certify that the 7th Semester Research Methodology Project Report entitled "Cyber-Secure Predictive '
        'Maintenance for Oil & Gas Wells" submitted by Rishi Kumar (500126773) and team has been reviewed and approved as a '
        'bonafide record of research methodology work carried out under academic supervision at the School of Computer Science, '
        'University of Petroleum & Energy Studies, Dehradun.'
    )
    add_styled_table(
        doc,
        ["Evaluation Committee Member", "Signature & Date"],
        [
            ["[Project Mentor / Guide Name] (Project Guide)", "___________________________"],
            ["[Internal Evaluator Name] (Internal Faculty Evaluator)", "___________________________"],
            ["[Head of Department Name] (HoD, School of Computer Science)", "___________________________"],
            ["External Examiner", "___________________________"],
        ],
        col_widths=[3.8, 2.4],
    )

    # =========================================================================
    # ACKNOWLEDGEMENTS
    # =========================================================================
    add_h1(doc, "ACKNOWLEDGEMENTS", page_break=True)
    add_p(
        doc,
        "First and foremost, we express our sincere gratitude to our Project Guide, [Project Mentor / Guide Name], for their "
        "strategic mentorship, domain guidance, and valuable suggestions—particularly on structuring the dual-layer decision "
        "priority between mechanical risk and sensor integrity, and grounding the research prototype in real-world oil and gas "
        "safety case studies."
    )
    add_p(
        doc,
        "We extend our heartfelt thanks to the Head of Department and the Dean, School of Computer Science, University of "
        "Petroleum & Energy Studies (UPES), Dehradun, for fostering an interdisciplinary research culture bridging cybersecurity, "
        "machine learning, and energy systems engineering."
    )
    add_p(
        doc,
        "We also acknowledge the public safety investigation reports published by the Oil Industry Safety Directorate (OISD), "
        "the Norwegian Ocean Industry Authority (Havtil), and Oil India Limited (OIL), as well as the open-source Python, "
        "scikit-learn, and Chart.js communities whose tools enabled rapid prototyping and transparent empirical validation."
    )
    add_p(
        doc,
        "Finally, we thank our families and peers for their encouragement, constructive feedback during dry-run reviews, "
        "and continuous support throughout this 7th Semester Research Methodology Project."
    )

    # =========================================================================
    # ABSTRACT & EXECUTIVE SUMMARY
    # =========================================================================
    add_h1(doc, "ABSTRACT & EXECUTIVE SUMMARY", page_break=True)
    add_p(
        doc,
        "Modern upstream oil and gas production relies heavily on Supervisory Control and Data Acquisition (SCADA) networks and "
        "Operational Technology (OT) telemetry to monitor Electric Submersible Pump (ESP) artificial-lift wells and surface "
        "processing equipment. While machine-learning-based Predictive Maintenance (PdM) frameworks can forecast impending "
        "equipment wear and unplanned downtime from multivariate sensor trends, conventional PdM pipelines implicitly assume that "
        "incoming sensor measurements are truthful, properly calibrated, and free from tampering. In reality, if a pressure "
        "transmitter freezes due to telemetry packet loss, drifts silently due to poor maintenance, or is altered via unauthorized "
        "Modbus register writes, a single-layer PdM model is blinded—generating costly false shutdowns or masking genuine "
        "well-control hazards."
    )
    add_p(
        doc,
        "This 7th Semester Research Methodology Project designs, implements, and empirically validates an integrated "
        "Cyber-Secure Predictive Maintenance framework that unifies petroleum engineering physics with two parallel AI layers "
        "inside a custom real-time web command console. First, a physics-informed 2-month (60-day) wellhead SCADA telemetry "
        "dataset comprising 86,400 one-minute observations and 36 columns was engineered (generate_scada_dataset.py), coupling "
        "Tubing Head Pressure (THP), Casing Head Pressure (CHP), Downhole Gauge Pressure (BHP), downhole temperature, ESP RPM, "
        "motor current, gas/water flow rates, annular water level, choke opening, Modbus function codes, and packet loss across "
        "six degradation/workover cycles and five canonical SCADA anomaly categories."
    )
    add_p(
        doc,
        "Using a strict chronological split (Days 1–42 Training = 60,479 rows; Days 43–60 Unseen Test = 25,921 rows) with "
        "train-only StandardScaler fitting to eliminate future-data leakage, Layer 1 supervised classifiers achieved strong "
        "early-warning performance: Random Forest attained 99.74% accuracy, 1.0000 precision, 0.9681 recall, 0.9838 F1-score, "
        "and 0.9986 ROC-AUC, while scikit-learn's HistGradientBoostingClassifier (XGBoost-style) achieved 99.78% accuracy, "
        "0.9865 F1-score, and 0.9973 ROC-AUC. In parallel, Layer 2 combined an unsupervised Isolation Forest (fit strictly on "
        "anomaly-free training samples) with deterministic physics-consistency and Modbus protocol rules, reaching 99.73% "
        "accuracy, 1.0000 precision, 0.9465 recall, 0.9725 F1-score, and 0.9926 ROC-AUC—dramatically outperforming a standalone "
        "One-Class SVM baseline (F1 = 0.5546) with zero false positives on unseen data."
    )
    add_p(
        doc,
        "To connect the research to industrial reality without overclaiming, an Incident Replay Lab was engineered "
        "(case_study_sim.py) reconstructing three documented oil and gas incidents: (1) the OISD Onshore Workover Rig Gas "
        "Blowout in India (Feb 2026) as the primary technical case (BLOWOUT 338.9 bbl -> CONTROLLED / 0.0 bbl SAFE), "
        "(2) Equinor's Deepsea Bollsta P&A well-control incident in Norway (Sep 2025; RELEASE 930.0 kg -> 0.0 kg SAFE), and "
        "(3) a clearly labelled hypothetical pathway for the Oil India Limited Tengakhat Tank Farm heater fire (Nov 2026; "
        "FIRE -> SAFE). Delivered through a bespoke Python REST backend and HTML5/SVG/Chart.js dashboard (server.py and "
        "dashboard.html), the prototype serves strictly as an early-warning decision-support tool that complements—and never "
        "replaces—physical well-control barriers, independent gauge calibration, and industrial safety instrumented systems."
    )

    # =========================================================================
    # TABLE OF CONTENTS, LIST OF FIGURES, LIST OF TABLES
    # =========================================================================
    add_h1(doc, "TABLE OF CONTENTS", page_break=True)
    add_styled_table(
        doc,
        ["Section", "Chapter / Title", "Key Scope"],
        [
            ["Front Matter", "Declaration, Approval, Acknowledgements & Abstract", "Academic certification & executive summary"],
            ["Chapter 1", "Introduction, Problem Formulation & Research Methodology", "7-stage research workflow, RQs, objectives & requirements"],
            ["Chapter 2", "Literature Review, OT Standards & Gap Analysis", "6 core AI/SCADA papers, NIST 800-82, IEC 62443 & OISD"],
            ["Chapter 3", "System Analysis, Dual-Layer Architecture & Design Diagrams", "End-to-end architecture, Scenario A/B/C flowchart & use cases"],
            ["Chapter 4", "Technology Stack & REST Backend Specifications", "Python 3.14, scikit-learn, ThreadingHTTPServer & Chart.js 4"],
            ["Chapter 5", "Dataset Engineering, Feature Extraction & ML Pipeline", "86,400-row SCADA dataset, 26 features & chronological split"],
            ["Chapter 6", "Experimental Results, Benchmarks & Dashboard Walkthrough", "Layer 1 & 2 metrics, confusion matrices & UI screenshot gaps"],
            ["Chapter 7", "Real-Life Case Studies & Incident Replay Simulation", "OISD blowout, Deepsea Bollsta, OIL IDBH & replay outcomes"],
            ["Chapter 8", "Claims, Research Boundaries, Limitations & Roadmap", "Scope boundaries (non-claims), limitations & future work"],
            ["Chapter 9", "Conclusion", "Synthesis of findings & research methodology takeaways"],
            ["References", "Academic Papers, Standards & Official Incident Reports", "16 verified IEEE-formatted citations"],
            ["Appendices", "Appendix A (Glossary), B (Math), C (Code), D (Team Checklist)", "Definitions, equations, excerpts & teammate gap guide"],
        ],
        col_widths=[1.1, 3.0, 2.2],
    )

    add_h2(doc, "LIST OF FIGURES")
    add_styled_table(
        doc,
        ["Figure No.", "Figure Title & Description", "Source / Type"],
        [
            ["Figure 1.1", "Structured 7-Stage Research Methodology Workflow", "Embedded Diagram (Matplotlib)"],
            ["Figure 1.2", "Conceptual ESP Artificial-Lift Well & SCADA/OT Threat Surface", "Image Gap Placeholder (Teammates)"],
            ["Figure 3.1", "End-to-End Dual-Layer System Architecture Flow Diagram", "Embedded Diagram (Matplotlib)"],
            ["Figure 3.2", "Integrated Dual-Layer Alert & Operator Decision Flowchart (Scenarios A/B/C)", "Embedded Diagram (Matplotlib)"],
            ["Figure 3.3", "System Use-Case & Actor Interaction Diagram", "Embedded Diagram (Matplotlib)"],
            ["Figure 5.1", "60-Day Multivariate Wellhead SCADA Telemetry & Dual-AI Overview", "Embedded Plot (Dataset CSV)"],
            ["Figure 6.1", "Layer 1 Predictive Maintenance Model Benchmark & Top-10 Features", "Embedded Plot (Eval JSON)"],
            ["Figure 6.2", "Layer 1 & Layer 2 Confusion Matrices and 5-Anomaly Recall Rates", "Embedded Plot (Eval JSON)"],
            ["Figure 6.3", "Live Well Monitor (Tab 1) — Scenarios A, B, and C Comparison", "Image Gap Placeholder (Teammates)"],
            ["Figure 6.4", "Interactive Well Anatomy & Component Repair Simulator (Tab 2)", "Image Gap Placeholder (Teammates)"],
            ["Figure 7.1", "Case-Study Reconstructed Time-Series (As Happened vs With Fixes)", "Embedded Plot (Case CSVs)"],
            ["Figure 7.2", "Incident Replay Lab (Tab 3) — OISD Workover Blowout Replay", "Image Gap Placeholder (Teammates)"],
            ["Figure 7.3", "Incident Replay Lab (Tab 3) — Deepsea Bollsta & Oil India IDBH Replays", "Image Gap Placeholder (Teammates)"],
        ],
        col_widths=[1.0, 3.6, 1.7],
        font_size=9.0,
    )

    add_h2(doc, "LIST OF TABLES")
    add_styled_table(
        doc,
        ["Table No.", "Table Title", "Chapter"],
        [
            ["Table 1.1", "Functional and Non-Functional Engineering Requirements Matrix", "Chapter 1"],
            ["Table 2.1", "Literature Survey Synthesis (Predictive Maintenance & SCADA Security)", "Chapter 2"],
            ["Table 2.2", "Comparative Analysis: Traditional Well Monitoring vs Proposed Framework", "Chapter 2"],
            ["Table 3.1", "Five-Tier Integrated Alert Structure and Operator Action Matrix", "Chapter 3"],
            ["Table 4.1", "Development and Runtime Hardware / OS Environment Specifications", "Chapter 4"],
            ["Table 4.2", "Software Stack, Python Libraries, and Web Visualization Toolchain", "Chapter 4"],
            ["Table 4.3", "Custom REST API Endpoints Exposed by server.py", "Chapter 4"],
            ["Table 5.1", "Primary Wellhead, Downhole, and SCADA Protocol Telemetry Schema", "Chapter 5"],
            ["Table 5.2", "Engineered Petroleum and Temporal Rolling Features (26 Inputs)", "Chapter 5"],
            ["Table 5.3", "Layer 1 Operational / Maintenance Class Distribution (86,400 Rows)", "Chapter 5"],
            ["Table 5.4", "Layer 2 Cyber / Measurement Anomaly Distribution (5 Canonical Classes)", "Chapter 5"],
            ["Table 6.1", "Layer 1 Predictive Maintenance Model Evaluation (Days 43–60 Test Set)", "Chapter 6"],
            ["Table 6.2", "Layer 2 Cyber Anomaly Detector Comparison (Isolation Forest vs OC-SVM)", "Chapter 6"],
            ["Table 6.3", "Per-Anomaly-Category Test Recall & Mean Anomaly Scores", "Chapter 6"],
            ["Table 6.4", "60-Day Integrated Dual-Layer Alert Distribution", "Chapter 6"],
            ["Table 7.1", "Cross-Case Comparative Matrix (OISD, Deepsea Bollsta, Oil India)", "Chapter 7"],
            ["Table 7.2", "Single-Fix & All-Fixes Replay Validation Matrix Across All 3 Case Studies", "Chapter 7"],
            ["Table 8.1", "Claims vs. Operational Boundaries (Preventing Overclaiming)", "Chapter 8"],
            ["Table A.1", "Technical Keywords and Definitions", "Appendix A"],
        ],
        col_widths=[1.0, 4.1, 1.2],
        font_size=9.0,
    )

    # =========================================================================
    # CHAPTER 1
    # =========================================================================
    add_h1(doc, "CHAPTER 1: INTRODUCTION, PROBLEM FORMULATION & RESEARCH METHODOLOGY", page_break=True)

    add_h2(doc, "1.1 Evolution of Digital Oilfields, Artificial-Lift Systems & SCADA Telemetry")
    add_p(
        doc,
        "Upstream oil and gas operations have increasingly transitioned from periodic manual wellhead gauging to continuous "
        "digital oilfield instrumentation. Artificial-lift production wells—especially Electric Submersible Pump (ESP) wells—are "
        "monitored round-the-clock via downhole pressure/temperature gauges, surface Tubing Head Pressure (THP) and Casing Head "
        "Pressure (CHP) transmitters, multiphase flow meters, and Variable Speed Drive (VSD) motor current monitors. Remote "
        "Terminal Units (RTUs) and Programmable Logic Controllers (PLCs) poll these field instruments over industrial protocols "
        "such as Modbus TCP/RTU and transmit time-series streams into central Supervisory Control and Data Acquisition (SCADA) "
        "historians."
    )
    add_p(
        doc,
        "In parallel, Machine Learning (ML)-based Predictive Maintenance (PdM) has emerged as a cornerstone of modern reliability "
        "engineering. By analyzing subtle multivariate shifts—such as rising ESP motor current coupled with declining tubing "
        "pressure and gas flow rate—PdM algorithms can estimate failure or downtime risk hours before a catastrophic pump trip "
        "or unplanned workover event."
    )

    add_h2(doc, "1.2 Problem Statement & The Cyber-Physical Measurement Paradox")
    add_p(
        doc,
        "Despite rapid adoption of predictive analytics, most oilfield PdM implementations exhibit a critical blind spot: they "
        "assume incoming SCADA sensor telemetry is accurate, calibrated, and uncorrupted. Similarly, traditional IT/OT perimeter "
        "defenses (firewalls, VPNs, encrypted tunnels) verify packet transport but do not inspect whether the physical numbers "
        "inside telemetry payloads remain consistent with petroleum engineering physics."
    )
    add_callout_box(
        doc,
        "CORE RESEARCH PROBLEM: THE CYBER-PHYSICAL MEASUREMENT PARADOX",
        "If a wellhead pressure sensor freezes due to a telemetry link stall, drifts silently due to overdue calibration, or is "
        "spoofed through an unauthorized Modbus register write, a standalone Predictive Maintenance model cannot tell whether a "
        "sudden pressure drop reflects real wellbore wear or corrupted data. Conversely, if a real pump failure occurs simultaneously "
        "with a compromised sensor, blindly acting on unverified telemetry risks catastrophic well-control or equipment decisions.",
        fill_hex="EFF6FF",
        border_hex="0284C7",
    )

    add_h2(doc, "1.3 Research Questions & Hypotheses")
    add_bullet(doc, "RQ1 (Petroleum Feature Sensitivity): ", "Can domain-engineered differential pressures (ΔP = BHP - THP, THP - CHP) and 15-minute rolling variance/rate-of-change descriptors detect ESP pre-failure degradation earlier and more reliably than raw static thresholds?")
    add_bullet(doc, "RQ2 (Temporal Validation Rigor): ", "How accurately do interpretable and ensemble classifiers generalize to unseen future operating weeks when trained under strict chronological splitting (Days 1–42 train, Days 43–60 test) without data leakage?")
    add_bullet(doc, "RQ3 (Physics-Informed Cyber/Sensor Integrity): ", "Can an unsupervised Isolation Forest augmented with Modbus protocol checks, zero-variance freeze detection, and physical coupling rules isolate all five canonical SCADA anomalies without raising false alarms during genuine mechanical wear?")
    add_bullet(doc, "RQ4 (Incident Grounding & Decision Priority): ", "How does an integrated dual-layer alert framework map onto documented oil and gas incidents (OISD, Deepsea Bollsta, Oil India) while maintaining strict, non-overclaiming engineering boundaries?")

    add_h2(doc, "1.4 Primary & Sub-Objectives")
    add_p(doc, "Aligned with the 7th Semester Research Methodology roadmap, the project addresses four core objectives:")
    add_bullet(doc, "Objective 1 — Well Data Synthesis & Petroleum Feature Analysis: ", "Construct and preprocess a 2-month (60-day, 86,400-minute) multivariate ESP wellhead SCADA dataset incorporating physical reservoir depletion, diurnal cycles, six degradation/workover events, and engineered ΔP, rolling, and rate-of-change features.")
    add_bullet(doc, "Objective 2 — Supervised Predictive Maintenance Modeling: ", "Train, benchmark, and validate four classifiers (Logistic Regression, Decision Tree, Random Forest, and HistGradientBoostingClassifier) on a strict chronological test split using Precision, Recall, F1-score, ROC-AUC, and feature attribution.")
    add_bullet(doc, "Objective 3 — Hybrid Cyber & Measurement Anomaly Detection: ", "Develop an unsupervised Isolation Forest + physics-consistency layer capable of scoring and flagging Sensor Spikes, Slow Drift, Sensor Freezing, False-Data Injection, and Physical Inconsistency.")
    add_bullet(doc, "Objective 4 — Integrated Monitoring Console & Incident Replay Lab: ", "Build a custom real-time web application uniting both AI layers into a 5-tier alert system, an interactive well-anatomy fault/repair simulator, and physics-based replays of three real-world oil and gas case studies.")

    add_h2(doc, "1.5 Research Methodology Design & Workflow")
    add_p(
        doc,
        "Following formal engineering research methodology principles, the study progressed iteratively across seven structured "
        "stages: (1) problem formulation, (2) academic and standards literature synthesis, (3) physics-coupled SCADA data synthesis, "
        "(4) domain feature extraction, (5) leakage-free chronological dual-layer model training, (6) historical case-study physics "
        "reconstruction, and (7) web dashboard validation with explicit boundary auditing. Figure 1.1 illustrates the complete workflow."
    )
    add_embedded_figure(
        doc,
        "report_figures/fig_1_1_research_methodology_flow.png",
        "Figure 1.1: Structured 7-Stage Research Methodology Workflow for Cyber-Secure Predictive Maintenance",
        width_in=6.3,
    )

    add_image_placeholder(
        doc,
        fig_label="Figure 1.2",
        title="Conceptual Illustration of an ESP Artificial-Lift Oil Well & SCADA/OT Cyber-Physical Threat Surface",
        what_belongs="A clean conceptual diagram showing (Left) an ESP artificial-lift wellbore with BHP, ESP motor, CHP, and THP sensors, (Center) the Modbus TCP RTU link under 5 potential sensor/cyber threats (Spike, Drift, Freeze, FDI, Physical Mismatch), and (Right) the Dual-AI Command Console.",
        steps_for_friends=(
            "1. Open Canva or Draw.io (app.diagrams.net) and create a 16:9 canvas (1920x1080).\n"
            "2. Left panel: Draw an oil well cross-section labelled BHP (1250 psi), ESP (3200 RPM / 58 A), CHP (150 psi), THP (280 psi).\n"
            "3. Center arrow: Label 'Modbus TCP (Func 03 Poll)' with 5 small red/purple warning icons for Spike, Drift, Freeze, FDI (Func 16), and Physical Mismatch.\n"
            "4. Right panel: Add two boxes ('Layer 1: Failure Prediction' + 'Layer 2: Cyber/Sensor Integrity') feeding into 'Operator Decision'. Export as PNG and paste above."
        ),
    )

    add_h2(doc, "1.6 Requirement Analysis")
    add_styled_table(
        doc,
        ["Requirement ID", "Category", "Specification & Engineering Criterion"],
        [
            ["FR-01", "Functional", "Generate and ingest 1-minute multivariate wellhead telemetry (THP, CHP, BHP, Temp, RPM, Current, Gas/Water Flow, Water Level, Choke %, Modbus, Packet Loss)."],
            ["FR-02", "Functional", "Compute physics-informed derived features including ΔP_wellbore, ΔP_surface, 15-min rolling mean/std, and 15-min ROC."],
            ["FR-03", "Functional", "Predict equipment failure risk (0–100%) and rank top contributing parameters using supervised ML models."],
            ["FR-04", "Functional", "Detect and classify 5 sensor/cyber anomaly types using unsupervised Isolation Forest + protocol/physics rules."],
            ["FR-05", "Functional", "Fuse both layers into a 5-tier alert system distinguishing Scenario A (Mechanical), Scenario B (Sensor), and Scenario C (Dual)."],
            ["FR-06", "Functional", "Provide an interactive Fault & Repair Simulator and a Case-Study Incident Replay Lab (OISD, Bollsta, OIL)."],
            ["NFR-01", "Non-Functional (Leakage-Free)", "Enforce strict chronological train/test splitting (Days 1–42 / Days 43–60) before fitting feature scalers."],
            ["NFR-02", "Non-Functional (Latency)", "Serve live ML inference via POST /api/simulate in under 50 ms for smooth interactive slider response."],
            ["NFR-03", "Non-Functional (Safety Rigor)", "Display explicit safety disclaimers stating the prototype supports early warning and never replaces BOP, LOTO, or calibration."],
        ],
        caption="Table 1.1: Functional and Non-Functional Engineering Requirements Matrix",
        col_widths=[1.1, 1.5, 3.7],
        font_size=9.0,
    )

    # =========================================================================
    # CHAPTER 2
    # =========================================================================
    add_h1(doc, "CHAPTER 2: LITERATURE REVIEW, INDUSTRIAL STANDARDS & RESEARCH GAP ANALYSIS", page_break=True)

    add_h2(doc, "2.1 Machine Learning for Predictive Maintenance & Well Integrity in Oil & Gas")
    add_p(
        doc,
        "Supervised machine learning has gained substantial traction in upstream petroleum reliability and artificial-lift "
        "diagnostics. Salem, Yakoot, and Mahmoud [1] benchmarked 11 single and ensemble classifiers across 9,000 data arrays "
        "and 23 features for autonomous diagnosis of well-integrity failures in artificial-lift systems, demonstrating that "
        "tree-based ensembles (Random Forest and gradient boosting) capture non-linear pressure-flow interactions effectively "
        "and allow feature-importance ranking for HSE prioritization. In downstream and process facilities, Arena et al. [2] "
        "addressed messy historical maintenance records by combining structured fault categorization with predictive failure "
        "modeling in an oil and gas refinery case study."
    )
    add_p(
        doc,
        "More recently, Wang et al. [3] demonstrated in the Journal of Petroleum Exploration and Production Technology (2025) "
        "that standalone models suffer when field sensor telemetry is noisy; integrating ensemble learning with domain rules "
        "improved F1-scores by 9–25% on Shengli Oilfield well data. Foundational Random Forest bagging theory by Breiman [12] "
        "explains this robustness through variance reduction across decorrelated decision trees."
    )

    add_h2(doc, "2.2 Measurement-Based & Unsupervised Anomaly Detection in ICS / SCADA")
    add_p(
        doc,
        "Conventional network Intrusion Detection Systems (IDS) inspect packet headers and TCP/IP signatures, yet stealthy "
        "false-data injection (FDI) attacks can ride inside syntactically valid Modbus frames. Mokhtari et al. [4] introduced a "
        "Measurement Intrusion Detection System (MIDS) validated on a Hardware-in-the-Loop (HIL) testbed, proving that monitoring "
        "physical SCADA process measurements catches stealthy anomalies invisible to network packet filters, with Random Forest "
        "and physical descriptors excelling."
    )
    add_p(
        doc,
        "Because authentic labeled cyberattack traces for industrial facilities are scarce and attackers continuously devise "
        "zero-day perturbations, Altaha and Hong [5] proposed unsupervised anomaly detection paired with protocol function-code "
        "analysis in SCADA networks. Unsupervised isolation algorithms such as Isolation Forest (Liu et al. [13]) and One-Class "
        "SVM (Schölkopf et al. [14]) learn normal multivariate operational envelopes without needing exhaustive attack labels—making "
        "them ideal for flagging sudden spikes, frozen flatlines, and physically inconsistent sensor states."
    )

    add_h2(doc, "2.3 Industrial OT Cybersecurity & Well-Control Standards")
    add_p(
        doc,
        "The architectural design of this project aligns with three authoritative industrial and safety standards:"
    )
    add_bullet(doc, "NIST SP 800-82 Rev. 3 (Stouffer et al., 2023) [6]: ", "Guide to Operational Technology (OT) Security, which emphasizes defense-in-depth, anomaly monitoring of physical process variables, and protocol command auditing (such as Modbus function-code inspection) across SCADA/ICS environments.")
    add_bullet(doc, "ISA/IEC 62443-4-2 [10] & Modbus Application Protocol V1.1b3 [11]: ", "Mandate continuous behavioral monitoring, auditability, and separation between read telemetry polling (Modbus Function Code 03) and state-altering coil/register writes (Function Codes 05, 06, 16).")
    add_bullet(doc, "OISD-STD-174 (Well Control) [16]: ", "Oil Industry Safety Directorate guidelines governing well-control readiness during workover and perforation, including continuous trip-tank fluid-volume monitoring and appropriate BOP shear-ram availability.")

    add_h2(doc, "2.4 Synthesis of Research Gap")
    add_p(
        doc,
        "Synthesizing the literature reveals three critical gaps that motivate this Research Methodology Project:"
    )
    add_bullet(doc, "Gap 1 — Siloed Maintenance vs. Security: ", "Predictive maintenance models [1]–[3] assume clean sensor inputs, whereas SCADA security tools [4]–[5] flag anomalies without estimating downstream equipment failure risk or guiding maintenance priority.")
    add_bullet(doc, "Gap 2 — Lack of Physics Cross-Checking for Sensor Faults vs. Attacks: ", "Real industrial incidents (such as Equinor Deepsea Bollsta [9]) show that uncalibrated tools or ignored differential pressures (ΔP) cause bad operational decisions just as cyber spoofing does.")
    add_bullet(doc, "Gap 3 — Disconnected Incident Validation: ", "Academic prototypes rarely demonstrate how their dashboard outputs translate onto documented oil and gas accidents while explicitly stating prototype limitations.")

    add_h2(doc, "2.5 Comparative Literature & System Capability Matrices")
    add_styled_table(
        doc,
        ["Ref", "Authors & Year", "Domain Focus", "ML / Security Method", "Limitation Addressed by Our Work"],
        [
            ["[1]", "Salem, Yakoot & Mahmoud (2022)", "Artificial-lift well integrity", "Supervised ensembles (RF, XGBoost, CatBoost)", "Assumes trustworthy sensors; no SCADA anomaly layer"],
            ["[2]", "Arena et al. (2022)", "Oil & gas failure management", "NLP + clustering + failure prediction", "Offline refinery logs; no live cyber/sensor checks"],
            ["[3]", "Wang et al. (2025)", "Oil & gas equipment PdM", "Ensemble learning + expert rules", "Focused solely on RUL/health; no OT protocol audit"],
            ["[4]", "Mokhtari et al. (2021)", "ICS measurement IDS", "HIL testbed + measurement-data ML", "No equipment downtime/workover prediction layer"],
            ["[5]", "Altaha & Hong (2022)", "SCADA protocol security", "Unsupervised ML + function-code analysis", "Applied to power DNP3; no petroleum ΔP physics"],
            ["[6]", "NIST SP 800-82 Rev. 3 (2023)", "OT/ICS cybersecurity guide", "Reference architecture & defense-in-depth", "High-level standard; requires domain implementation"],
        ],
        caption="Table 2.1: Literature Survey Synthesis Across Predictive Maintenance and OT/SCADA Security",
        col_widths=[0.45, 1.45, 1.3, 1.5, 1.6],
        font_size=8.6,
    )

    add_styled_table(
        doc,
        ["Capability / Dimension", "Traditional Oilfield Monitoring", "Proposed Dual-Layer Cyber-Secure Framework"],
        [
            ["Failure Prediction", "Static high/low threshold alarms or reactive trip", "Trained Random Forest / HistGBM predicting Pre-Failure Risk (0–100%)"],
            ["Sensor Integrity Check", "None (raw telemetry blindly trusted)", "Hybrid Isolation Forest + zero-std freeze + ΔP physical coupling"],
            ["SCADA Protocol Awareness", "Ignored by maintenance analytics", "Inspects Modbus function codes (Func 03 vs 05/06/16) & packet loss"],
            ["Data Leakage Control", "Often random row shuffling in prototypes", "Strict chronological split (Days 1–42 train / Days 43–60 unseen test)"],
            ["Combined Alert Triage", "Single undifferentiated alarm flood", "5-tier matrix explicitly separating Scenarios A, B, and C"],
            ["Industrial Grounding", "Abstract synthetic scores only", "Interactive Incident Replay Lab (OISD, Bollsta, OIL) + boundary table"],
        ],
        caption="Table 2.2: Comparative Analysis — Traditional Well Monitoring vs. Proposed Framework",
        col_widths=[1.6, 2.2, 2.5],
        font_size=9.0,
    )

    # =========================================================================
    # CHAPTER 3
    # =========================================================================
    add_h1(doc, "CHAPTER 3: SYSTEM ANALYSIS, PROPOSED DUAL-LAYER ARCHITECTURE & DESIGN DIAGRAMS", page_break=True)

    add_h2(doc, "3.1 Architectural Overview: Two Parallel Intelligence Layers")
    add_p(
        doc,
        "The core architectural principle of this project is parallel separation of concerns: Operational Failure Prediction "
        "(Layer 1) and Sensor/Cyber Anomaly Detection (Layer 2) operate concurrently on the same preprocessed 26-feature "
        "stream, and their outputs converge at a unified 5-tier decision layer. This design ensures that neither mechanical "
        "degradation nor sensor corruption masks the other."
    )

    add_h2(doc, "3.2 End-to-End System Architecture & Data Flow")
    add_embedded_figure(
        doc,
        "report_figures/fig_3_1_system_architecture_flow.png",
        "Figure 3.1: End-to-End Dual-Layer System Architecture (Telemetry, Physics Features, Parallel AI & Dashboard)",
        width_in=6.3,
    )

    add_h2(doc, "3.3 Detailed Module Breakdown")
    add_bullet(doc, "Module 1 — Physics-Informed Telemetry Generator (generate_scada_dataset.py): ", "Synthesizes 60 days of 1-minute ESP telemetry with coupled reservoir depletion, diurnal ambient cycles, 6 degradation-downtime-workover cycles, and 5 SCADA anomaly classes.")
    add_bullet(doc, "Module 2 — Petroleum Feature Engineering Engine: ", "Computes wellbore and surface differential pressures (ΔP), 15-minute rolling means and standard deviations, 15-minute rates of change (ROC), and baseline deviations.")
    add_bullet(doc, "Module 3 — AI Layer 1 (Supervised Predictive Maintenance): ", "Benchmarks Logistic Regression, Decision Tree, Random Forest, and HistGradientBoostingClassifier; exports Random Forest risk probability (0–100%), risk tier, and parameter contribution ranking.")
    add_bullet(doc, "Module 4 — AI Layer 2 (Hybrid Cyber & Sensor Integrity): ", "Combines an Isolation Forest fit solely on anomaly-free training rows with deterministic rules for frozen rolling variance (std < 0.05 psi), unauthorized Modbus writes (Func != 3), slow CHP drift, and extreme spikes.")
    add_bullet(doc, "Module 5 — Integrated 5-Tier Alert & Replay Engine (server.py + case_study_sim.py): ", "Serves live SCADA windows, real-time parameter-fault simulation (/api/simulate), and physics-based historical incident replays (/api/case_sim) to the web dashboard.")

    add_h2(doc, "3.4 Integrated Alert Matrix & Scenarios A, B, and C Decision Workflow")
    add_p(
        doc,
        "Figure 3.2 and Table 3.1 formalize how the two parallel AI scores—Failure Risk R (%) and Cyber Anomaly Score C (0–100)—are "
        "combined into five unambiguous operator states covering Scenario A (Equipment Degradation), Scenario B (Measurement Integrity "
        "Issue), and Scenario C (Simultaneous High Failure Risk and Sensor Anomaly)."
    )
    add_embedded_figure(
        doc,
        "report_figures/fig_3_2_decision_activity_flowchart.png",
        "Figure 3.2: Integrated Dual-Layer Alert & Operator Decision Flowchart (Scenarios A, B & C)",
        width_in=6.3,
    )

    add_styled_table(
        doc,
        ["Alert Tier", "Trigger Rule", "Operational Meaning", "Recommended Operator Response"],
        [
            ["Normal", "R <= 35% and C < 60", "Well parameters & sensors within baseline.", "Continue routine automated monitoring."],
            ["Maintenance Warning", "35% < R <= 65% and C < 60", "Early operating trend deviation detected.", "Schedule engineering assessment & monitor current/THP."],
            ["High Failure Risk (Scenario A)", "R > 65% and C < 60", "ML predicts elevated downtime/workover risk; sensors trusted.", "Prioritise mechanical inspection & workover planning."],
            ["Measurement Anomaly (Scenario B)", "C >= 60 and R <= 65%", "Sensor data frozen, drifting, spiked, or spoofed via Modbus.", "Verify gauge calibration, RTU link & physical pressure."],
            ["Critical Operational Warning (Scenario C)", "R > 65% and C >= 60", "High failure risk AND abnormal/tampered sensor data together.", "Verify sensor reliability FIRST; escalate under SOP."],
        ],
        caption="Table 3.1: Five-Tier Integrated Alert Structure and Operator Decision Matrix",
        col_widths=[1.4, 1.25, 1.8, 1.85],
        font_size=8.8,
    )

    add_h2(doc, "3.5 Use-Case Diagram & Operator Workflows")
    add_embedded_figure(
        doc,
        "report_figures/fig_3_3_use_case_diagram.png",
        "Figure 3.3: System Use-Case & Actor Interaction Diagram Across Engineering and OT Security Roles",
        width_in=6.2,
    )

    # =========================================================================
    # CHAPTER 4
    # =========================================================================
    add_h1(doc, "CHAPTER 4: TECHNOLOGY STACK, SOFTWARE ARCHITECTURE & IMPLEMENTATION", page_break=True)

    add_h2(doc, "4.1 Compute & Execution Environment")
    add_styled_table(
        doc,
        ["Environment Component", "Specification Used in Project"],
        [
            ["Operating System", "Microsoft Windows (64-bit) Local Workstation"],
            ["Python Runtime", "Python 3.14"],
            ["JavaScript Runtime (Verification)", "Node.js v24.18.0 (syntax validation via node --check)"],
            ["Web Server Port & Protocol", "Local HTTP REST Server on 0.0.0.0:8505 (http://localhost:8505)"],
            ["Version Control", "Git + GitHub (RishiKumar1917/cyber-secure-predictive-maintenance)"],
        ],
        caption="Table 4.1: Development and Runtime Environment Specifications",
        col_widths=[2.4, 3.9],
    )

    add_h2(doc, "4.2 Software Stack, Libraries & ML Toolchains")
    add_styled_table(
        doc,
        ["Tool / Library", "Version / Module", "Role in the Project"],
        [
            ["NumPy", "2.5.1", "Vectorized reservoir physics, noise synthesis, and numerical array scoring"],
            ["Pandas", "3.0.5", "Time-series manipulation, rolling windows, CSV/JSON telemetry I/O"],
            ["Scikit-Learn", "1.9.0", "StandardScaler, LogisticRegression, DecisionTreeClassifier, RandomForestClassifier, HistGradientBoostingClassifier, IsolationForest, OneClassSVM, evaluation metrics"],
            ["Python http.server", "ThreadingHTTPServer", "Lightweight zero-dependency REST backend serving HTML & live inference"],
            ["HTML5 / CSS3 / SVG", "Custom UI (dashboard.html)", "Dark-mode SCADA control room UI, clickable 6-zone SVG well schematic"],
            ["Chart.js", "v4.4.1 (CDN)", "Interactive multi-channel time-series charts with custom glowing playhead plugin"],
            ["Matplotlib & python-docx", "Offline Reporting Tools", "Generation of academic plots, flow diagrams, and this DOCX report"],
        ],
        caption="Table 4.2: Software Stack, Python Libraries, and Visualization Toolchain",
        col_widths=[1.6, 1.5, 3.2],
        font_size=9.0,
    )

    add_h2(doc, "4.3 Backend REST API Specification")
    add_p(
        doc,
        "Rather than relying on a generic template UI, a dedicated multi-threaded HTTP server (server.py) loads the 86,400-row "
        "scored dataset, evaluation metrics, and serialized scikit-learn models (trained_models_bundle.pkl) into memory at startup "
        "and exposes five JSON/HTML endpoints summarized in Table 4.3."
    )
    add_styled_table(
        doc,
        ["HTTP Endpoint", "Method", "Request / Query", "Response Payload & Purpose"],
        [
            ["/", "GET", "None", "Serves custom interactive single-page web dashboard (dashboard.html)."],
            ["/api/init", "GET", "None", "Returns model_evaluation_summary.json, scenario presets, and total row count (86,400)."],
            ["/api/window", "GET", "?start_day&end_day&focus_idx", "Returns downsampled 24-hour window arrays, live snapshot metrics, and active alert log."],
            ["/api/simulate", "POST", "{thp, chp, bhp, current, gas_rate, rpm, modbus, freeze, ...}", "Runs real-time Layer 1 + Layer 2 inference and returns risk %, cyber score, and attributions."],
            ["/api/cases", "GET", "None", "Returns metadata, as-happened defaults, and all-fixes presets for OISD, Bollsta, and OIL."],
            ["/api/case_sim", "POST", "{case_id, params}", "Executes physics replay engine (case_study_sim.py) and returns time-series, events & outcome."],
        ],
        caption="Table 4.3: Custom REST API Endpoints Exposed by server.py",
        col_widths=[1.2, 0.7, 1.9, 2.5],
        font_size=8.6,
    )

    add_h2(doc, "4.4 Engineering Design Considerations")
    add_bullet(doc, "Leakage-Free Temporal Validation: ", "Time-series SCADA samples exhibit strong autocorrelation. Random row splitting would leak adjacent future minutes into training. Our pipeline strictly partitions Days 1–42 for training and Days 43–60 for testing before fitting StandardScaler.")
    add_bullet(doc, "Sub-5 ms Interactive Inference: ", "Loading trained_models_bundle.pkl once at server boot eliminates cold-start overhead, allowing sliders in Tab 2 and fix toggles in Tab 3 to update diagrams and AI scores instantaneously.")
    add_bullet(doc, "Explainable Attribution Without Black-Box Opacity: ", "Random Forest Gini feature importances provide global predictor rankings, while per-snapshot parameter deviations from physical operating baselines identify the exact driver behind each alert.")

    # =========================================================================
    # CHAPTER 5
    # =========================================================================
    add_h1(doc, "CHAPTER 5: DATASET ENGINEERING, FEATURE EXTRACTION & MODEL DEVELOPMENT", page_break=True)

    add_h2(doc, "5.1 Rationale for Physics-Informed 2-Month Wellhead SCADA Synthesis")
    add_p(
        doc,
        "Publicly available datasets containing simultaneous oilfield mechanical breakdowns, complete petroleum wellhead "
        "parameters, and labeled SCADA cyberattacks do not exist due to critical-infrastructure confidentiality. Following "
        "the project design assumption (~2 months of historical well data paired with controlled simulated anomalies), "
        "generate_scada_dataset.py synthesizes 60 consecutive days (2026-07-01 00:00:00 to 2026-08-29 23:59:00) at 1-minute "
        "resolution—yielding 86,400 records and 36 total columns with zero missing/NULL values."
    )
    add_p(
        doc,
        "Crucially, parameters are not independent random numbers: Bottomhole Pressure (BHP) incorporates a gradual -15 psi "
        "reservoir depletion trend over 60 days; surface pressures include a 24-hour (1440-minute) diurnal thermal cycle; "
        "THP, water rate, gas rate, and motor current are physically coupled to ESP RPM (3200 RPM nominal) and BHP; and "
        "annular water level responds inversely to pump drawdown."
    )

    add_h2(doc, "5.2 Primary Wellhead, Downhole & Protocol Telemetry Schema")
    add_styled_table(
        doc,
        ["Column Name", "Normal Baseline", "Physical Coupling / Engineering Significance"],
        [
            ["tubing_head_pressure_psi (THP)", "~280.0 psi", "Coupled to RPM and BHP + diurnal cycle; drops during ESP wear, spikes if choked."],
            ["casing_head_pressure_psi (CHP)", "~150.0 psi", "Annulus pressure + 0.5x diurnal cycle; rises with annulus gas or gauge drift."],
            ["downhole_gauge_pressure_psi (BHP)", "~1250 -> 1235 psi", "Bottomhole gauge with -15 psi reservoir depletion over 60 days."],
            ["downhole_temp_f", "~185.0 °F", "Downhole motor/formation temperature; rises +11 °F during bearing overheat."],
            ["pump_rpm", "~3200 RPM", "ESP shaft speed; drops under severe wear, trips to 0 on downtime, surges if tampered."],
            ["pump_torque_current_amps", "~58.0 A", "Motor current coupled to RPM; rises +18.5 A under stage/bearing mechanical wear."],
            ["water_rate_bpd / gas_rate_mscfd", "~850 BPD / ~320 MSCFD", "Multiphase production rates proportional to pump RPM; decline prior to trip."],
            ["water_level_ft", "~450.0 ft", "Annular fluid level above intake; rises as pump lifting efficiency drops."],
            ["choke_opening_pct", "~80.0%", "Surface production choke position; drops to ~5–8% during valve sabotage."],
            ["modbus_function_code", "3 (Read)", "Modbus TCP function code (3 = normal telemetry read; 5, 6, 16 = write tampering)."],
            ["packet_loss_pct", "~0.18% (exp.)", "Network packet loss; surges to 28–75% during DoS telemetry freeze."],
        ],
        caption="Table 5.1: Primary Wellhead, Downhole, and SCADA Protocol Telemetry Schema",
        col_widths=[2.1, 1.3, 2.9],
        font_size=8.6,
    )

    add_h2(doc, "5.3 Derived Petroleum & Temporal Feature Set")
    add_styled_table(
        doc,
        ["Derived Feature Group", "Exact Columns Generated", "Engineering & Security Purpose"],
        [
            ["Differential Pressures (ΔP)", "diff_pressure_bhp_thp_psi, diff_pressure_thp_chp_psi", "Cross-checks pressure consistency across tubing, casing, and downhole gauges (Bollsta relevance)."],
            ["15-Min Rolling Mean", "thp_roll_mean_15m, gas_rate_roll_mean_15m, current_roll_mean_15m", "Smooths 1-minute sensor noise to reveal true degradation trajectories."],
            ["15-Min Rolling Std", "thp_roll_std_15m, chp_roll_std_15m", "Drops near 0.00 during frozen-sensor DoS attacks while healthy sensors show ~1.6–2.2 psi noise."],
            ["15-Min Rate of Change", "thp_roc_15m, chp_roc_15m, bhp_roc_15m, current_roc_15m", "Captures sudden acute injection spikes and rapid pre-trip load escalations."],
            ["Baseline Deviations", "thp_baseline_dev, chp_baseline_dev, bhp_baseline_dev", "Measures signed departure from established normal well baselines (280, 150, 1242.5 psi)."],
        ],
        caption="Table 5.2: Engineered Petroleum and Temporal Rolling Features",
        col_widths=[1.5, 2.3, 2.5],
        font_size=8.7,
    )

    add_h2(doc, "5.4 Dual-Layer Ground-Truth Labeling & 60-Day Dataset Overview")
    add_p(
        doc,
        "Six full maintenance cycles were injected on Days 7, 16, 29, 38, 48, and 56—each consisting of a 12–15 hour gradual "
        "Pre-failure degradation phase (THP and gas/water rates falling while motor current and downhole temperature climb), a "
        "4–5 hour unplanned Downtime shut-in, and a 6–8 hour Workover recovery phase. Independently, five canonical SCADA/sensor "
        "anomaly classes were injected across both the Training window (Days 1–42) and Unseen Test window (Days 43–60), including "
        "a deliberate 4-hour Scenario C overlap on Day 56 (240 minutes) where Pre-failure degradation and Physical Inconsistency "
        "tampering co-occur."
    )

    add_styled_table(
        doc,
        ["Operational Status (Layer 1)", "Row Count (Minutes)", "Share (%)", "Binary Target (is_failure_risk)"],
        [
            ["Normal", "77,700", "89.93%", "0 (Healthy)"],
            ["Pre-failure", "4,740", "5.49%", "1 (Early-Warning Positive)"],
            ["Workover", "2,400", "2.78%", "0 (Scheduled Intervention)"],
            ["Downtime", "1,560", "1.81%", "1 (Unplanned Outage Positive)"],
            ["Total Dataset", "86,400", "100.00%", "6,300 Positive / 80,100 Negative"],
        ],
        caption="Table 5.3: Layer 1 Operational / Predictive Maintenance Class Distribution",
        col_widths=[2.0, 1.4, 1.0, 1.9],
    )

    add_styled_table(
        doc,
        ["Anomaly Category (Layer 2)", "Row Count (Minutes)", "Injection Mechanism Across 60 Days"],
        [
            ["Normal", "83,190", "Routine Modbus Function 03 polling with natural sensor noise."],
            ["Sensor_Drift", "930", "Stealthy creeping +145 psi bias on CHP and -95 psi bias on BHP (Days 11, 34, 46)."],
            ["Physical_Inconsistency", "720", "High RPM (4380–4450) + choked valve (6–8%) + contradictory flow (Days 19, 27, 53, 56 Scenario C)."],
            ["Sensor_Freezing", "600", "Flatline zero-variance THP/BHP while CHP varies & packet loss reaches 28–68% (Days 14, 32, 44)."],
            ["False_Data_Injection", "570", "Unauthorized Modbus Func 16 write spoofing downhole BHP to ~420 psi (Days 6, 21, 51)."],
            ["Sensor_Spike", "390", "Sudden ±140–240 psi THP and ±250–420 psi BHP extreme transient spikes (Days 3, 24, 43)."],
        ],
        caption="Table 5.4: Layer 2 Cyber / Measurement Anomaly Class Distribution (3,210 Total Anomaly Minutes)",
        col_widths=[1.8, 1.3, 3.2],
        font_size=8.8,
    )

    add_embedded_figure(
        doc,
        "report_figures/fig_5_1_dataset_telemetry_overview.png",
        "Figure 5.1: 60-Day Multivariate Wellhead SCADA Telemetry & Chronological Train/Test Split (Day 42)",
        width_in=6.3,
    )

    add_h2(doc, "5.5 Chronological Splitting & Dual-Layer Training Pipeline")
    add_p(
        doc,
        "In ml_pipeline.py, the 86,400 records are sorted chronologically and split at the 70% boundary: Days 1–42 (60,479 rows) "
        "form the training set, and Days 43–60 (25,921 rows, starting 2026-08-11 23:59:00) form the unseen test set. Two separate "
        "StandardScaler instances are fit strictly on training rows. Layer 1 trains four balanced classifiers on 23 petroleum and "
        "rolling features: Logistic Regression, Decision Tree (max_depth=8), Random Forest (100 trees, max_depth=12), and "
        "HistGradientBoostingClassifier (120 iterations, max_depth=8, learning_rate=0.08). Layer 2 fits an Isolation Forest "
        "(150 estimators, contamination=0.038) and a baseline One-Class SVM (RBF kernel, nu=0.04) solely on non-anomaly training "
        "rows (is_anomaly == 0) over 16 protocol and physics-consistency features, then fuses the normalized Isolation Forest "
        "anomaly score with deterministic checks for zero-std sensor freezes, non-03 Modbus codes, creeping drift, spikes, and "
        "RPM/choke inconsistencies."
    )

    # =========================================================================
    # CHAPTER 6
    # =========================================================================
    add_h1(doc, "CHAPTER 6: EXPERIMENTAL RESULTS, PERFORMANCE VALIDATION & DASHBOARD WALKTHROUGH", page_break=True)

    add_h2(doc, "6.1 Layer 1 Predictive Maintenance Evaluation (Unseen Days 43–60)")
    add_p(
        doc,
        "Table 6.1 summarizes the exact out-of-sample test performance of all four supervised classifiers on the 25,921 unseen "
        "minutes of Days 43–60. Both tree ensembles exceed 0.98 F1-score and 0.997 ROC-AUC; Random Forest was selected as the "
        "primary dashboard scorer because it achieved zero false alarms (Precision = 1.0000, FP = 0) and the highest ROC-AUC (0.9986)."
    )

    pdm_rows = []
    for m_name, mv in eval_sum["pdm_metrics"].items():
        cm = mv["Confusion_Matrix"]
        disp_name = "HistGradientBoosting (XGBoost-Style)" if "HistGBM" in m_name else m_name
        pdm_rows.append([
            disp_name,
            f"{mv['Accuracy']*100:.2f}%",
            f"{mv['Precision']:.4f}",
            f"{mv['Recall']:.4f}",
            f"{mv['F1_Score']:.4f}",
            f"{mv['ROC_AUC']:.4f}",
            f"{cm[1][1]:,} / {cm[0][1]} / {cm[1][0]}",
        ])
    add_styled_table(
        doc,
        ["Classifier", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "TP / FP / FN"],
        pdm_rows,
        caption="Table 6.1: Layer 1 Predictive Maintenance Model Evaluation on Chronological Test Split (25,921 Rows)",
        col_widths=[1.85, 0.72, 0.72, 0.68, 0.72, 0.72, 0.89],
        font_size=8.6,
    )

    add_embedded_figure(
        doc,
        "report_figures/fig_6_1_pdm_benchmark_and_importance.png",
        "Figure 6.1: Layer 1 Model Comparison and Top-10 Random Forest Gini Feature Importances",
        width_in=6.3,
    )

    add_h2(doc, "6.2 Layer 2 Cyber & Sensor-Integrity Evaluation")
    add_p(
        doc,
        "Table 6.2 compares the Physics-Informed Hybrid Isolation Forest against the standalone One-Class SVM baseline on the "
        "same unseen Days 43–60 test split. While One-Class SVM flags 2,051 normal operational minutes as false alarms "
        "(Precision = 0.3846), the Hybrid Isolation Forest eliminates false positives (Precision = 1.0000, FP = 0) while achieving "
        "0.9465 recall and 0.9725 F1-score—confirming that normal mechanical wear (Scenario A) is not misclassified as a cyberattack."
    )

    cyb_rows = []
    for c_name, cv in eval_sum["cyber_metrics"].items():
        cm = cv["Confusion_Matrix"]
        cyb_rows.append([
            c_name,
            f"{cv['Accuracy']*100:.2f}%",
            f"{cv['Precision']:.4f}",
            f"{cv['Recall']:.4f}",
            f"{cv['F1_Score']:.4f}",
            f"{cv['ROC_AUC']:.4f}",
            f"{cm[1][1]:,} / {cm[0][1]:,} / {cm[1][0]}",
        ])
    add_styled_table(
        doc,
        ["Anomaly Detector", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "TP / FP / FN"],
        cyb_rows,
        caption="Table 6.2: Layer 2 Cyber / Measurement Anomaly Detector Comparison (Days 43–60 Test Set)",
        col_widths=[1.9, 0.7, 0.7, 0.65, 0.7, 0.7, 0.95],
        font_size=8.5,
    )

    rec_rows = []
    for cat, info in eval_sum["anomaly_type_recall"].items():
        rec_rows.append([
            cat.replace("_", " "),
            f"{info['Test_Minutes']} mins",
            f"{info['Detection_Rate_Pct']:.2f}%",
            f"{info['Mean_Anomaly_Score']:.1f} / 100",
        ])
    add_styled_table(
        doc,
        ["Simulated Anomaly Category", "Unseen Test Duration", "Detection Rate (%)", "Mean Anomaly Score"],
        rec_rows,
        caption="Table 6.3: Per-Anomaly-Category Detection Performance on Unseen Test Split",
        col_widths=[2.1, 1.4, 1.4, 1.4],
    )

    add_embedded_figure(
        doc,
        "report_figures/fig_6_2_confusion_and_cyber_recall.png",
        "Figure 6.2: Test-Set Confusion Matrices (Layers 1 & 2) and Per-Anomaly Recall Across 5 Threat Classes",
        width_in=6.3,
    )

    add_h2(doc, "6.3 Integrated Dual-Layer Alert Distribution Across 60 Days")
    ad = eval_sum["alert_distribution"]
    add_styled_table(
        doc,
        ["Integrated Alert Level", "Total Minutes (60 Days)", "Share (%)", "Interpretation"],
        [
            ["Normal", f"{ad['Normal']:,}", f"{ad['Normal']/864:.2f}%", "Routine healthy wellhead & verified SCADA operation."],
            ["High failure risk", f"{ad['High failure risk']:,}", f"{ad['High failure risk']/864:.2f}%", "Scenario A: equipment wear/downtime risk with trusted sensors."],
            ["Measurement anomaly", f"{ad['Measurement anomaly']:,}", f"{ad['Measurement anomaly']/864:.2f}%", "Scenario B: sensor spike, drift, freeze, FDI, or flow mismatch."],
            ["Critical operational warning", f"{ad['Critical operational warning']:,}", f"{ad['Critical operational warning']/864:.2f}%", "Scenario C: Day 56 overlap requiring sensor check before action."],
            ["Maintenance warning", f"{ad['Maintenance warning']:,}", f"{ad['Maintenance warning']/864:.2f}%", "Early transition minutes (35–65% risk) preceding trip."],
        ],
        caption="Table 6.4: 60-Day Integrated Dual-Layer Alert Distribution (86,400 Total Minutes)",
        col_widths=[1.8, 1.2, 0.85, 2.45],
        font_size=8.8,
    )

    add_h2(doc, "6.4 Interactive Web Console Demonstration & Screenshot Placeholders")
    add_p(
        doc,
        "The live custom web application (http://localhost:8505) translates both ML layers into plain-English operator views "
        "across four tabs. Figures 6.3 and 6.4 reserve space for full-resolution UI captures from the running dashboard."
    )

    add_image_placeholder(
        doc,
        fig_label="Figure 6.3",
        title="Live Well Monitor (Tab 1) Demonstrating Scenario A, Scenario B, and Scenario C Responses",
        what_belongs="A side-by-side or stacked screenshot of Tab 1 (1. Live Well Monitor) showing the animated 6-zone Well W-001 schematic, Layer 1 Predictive Maintenance card, Layer 2 Sensor & Cyber Check card, and the color-coded 24-hour trend chart.",
        steps_for_friends=(
            "1. Run 'python server.py' and open http://localhost:8505 in Chrome/Edge (1920x1080 fullscreen).\n"
            "2. On Tab 1 ('1. Live Well Monitor'), click 'Scenario A' and take a screenshot (shows Red High Risk + Green Sensors Trusted).\n"
            "3. Click 'Scenario C: Failure + Sensor Tampering' and take a second screenshot (shows Flashing Critical Warning).\n"
            "4. Combine both screenshots vertically or side-by-side (or insert Scenario C full screen) and paste here."
        ),
    )

    add_image_placeholder(
        doc,
        fig_label="Figure 6.4",
        title="Interactive Well Anatomy & One-Click Component Repair Simulator (Tab 2)",
        what_belongs="Screenshot of Tab 2 ('2. Interactive Simulator') showing sliders moved out of normal range, highlighted red/purple components on the clickable well schematic, and the right-hand 'Selected Well Component' diagnosis card with the green 'Fix This Part' button.",
        steps_for_friends=(
            "1. In http://localhost:8505, click '2. Interactive Simulator' in the top navigation bar.\n"
            "2. Click preset '🔴 Pump Wear' OR drag 'Pump Motor Current' up to ~78 A and check 'Freeze Sensor'.\n"
            "3. Click on '5. ESP Pump & Motor' on the middle diagram so its diagnosis and 'Fix This Part' button appear on the right.\n"
            "4. Capture the full 3-column simulator screen and paste it inside this box."
        ),
    )

    # =========================================================================
    # CHAPTER 7
    # =========================================================================
    add_h1(doc, "CHAPTER 7: REAL-LIFE OIL & GAS CASE STUDIES & INCIDENT REPLAY SIMULATION", page_break=True)

    add_h2(doc, "7.1 Analytical Framework for Historical Incident Mapping")
    add_p(
        doc,
        "To evaluate how the proposed framework relates to real industrial operations, three documented oil and gas incidents "
        "were examined using a rigorous two-part analytical discipline: (1) documented factual findings from official regulatory "
        "or corporate sources are strictly separated from project-specific engineering reconstructions, and (2) the Incident "
        "Replay Lab (case_study_sim.py + Tab 3) demonstrates how early monitoring and physical/procedural fixes alter simulated "
        "outcomes without claiming that a software prototype alone could have prevented historical tragedies."
    )

    add_h2(doc, "7.2 Case Study 1 (Primary Technical Case): Gas Blowout at Onshore Workover Rig, India (OISD, 2026)")
    add_bullet(doc, "Incident Context: ", "On 4 February 2026, during conventional wireline perforation at an onshore workover rig in India, uncontrolled gas flow (blowout) occurred immediately after perforating the target zone [8] (Case Ref: OISD/CS/2025-26/E&P/21). No injuries or fire were reported, though well-control consequences were severe.")
    add_bullet(doc, "Documented Sequence & Findings (OISD): ", "(i) The Geological Technical Order (GTO) indicated an oil-bearing zone, conflicting with offset-well evidence and prior gas influxes during drilling; (ii) CBL-VDL logs did not show good cement bonding across the entire depth; (iii) lighter completion fluid was used during perforation than final drilling mud, reducing hydrostatic pressure (Ph = ρ g h); (iv) the BOP stack lacked a shear ram, so the blind ram could not seal with the wireline still inside the well; and (v) the trip tank was kept isolated during perforation contrary to OISD-STD-174 [16].")
    add_bullet(doc, "Early-Detection & Replay Mapping: ", "Using illustrative parameters (2200 m depth, 3350 psi gas formation vs 3000 psi GTO assumption, 1.18 SG mud swapped to 1.02 SG completion fluid), our physics replay reproduces an escalating gas kick reaching 338.9 bbl and BLOWOUT at T+97 min when run 'As Happened' (trip tank reads 0.0 flat; blind ram fails at T+93). Enabling offset-well fluid re-weighting (SG 1.15, Ph = 3600 psi, +250 psi overbalance) yields SAFE (0.0 bbl influx). Enabling only trip-tank monitoring, AI Layer 2 flow-mismatch detection, or a BOP shear-seal ram controls the kick before the 40 bbl threshold (CONTROLLED at 18.0–28.6 bbl), whereas fixing cement quality alone still results in BLOWOUT because the wellbore remains underbalanced with late visual detection.")
    add_bullet(doc, "Limitations & Takeaway: ", "A dashboard cannot certify CBL-VDL cement integrity or replace a physical BOP shear ram. Its value lies in integrating conflicting geological records, fluid-density overbalance checks, and trip-tank telemetry prior to perforation.")

    add_h2(doc, "7.3 Case Study 2 (Measurement-Integrity Case): Equinor Deepsea Bollsta Well-Control Incident (2025)")
    add_bullet(doc, "Incident Context: ", "On 23 September 2025 (investigation published 18 May 2026 by Norway's Havtil [9]), during permanent plugging and abandonment (P&A) on Well Q-21 (Troll Field) from the Deepsea Bollsta drilling facility (114 personnel onboard), cutting the 13 3/8-inch casing at ~510 m released ~930 kg of gas (methane, ethane, propane) and water, causing one minor injury.")
    add_bullet(doc, "Documented Sequence & Findings (Havtil): ", "Direct cause was failure of the outer well barrier behind the 13 3/8-inch casing. Havtil identified faulty calibration of casing logging tools leading to misinterpretation, failure to adequately use differential-pressure (ΔP) data, inadequate maintenance of ΔP gauges, and weaknesses in barrier risk communication.")
    add_bullet(doc, "Early-Detection & Replay Mapping: ", "In our reconstruction (620 psi trapped annular gas, true bond index 0.35 masked as 0.80 by uncalibrated logging, ΔP gauge drifting low then freezing flat at 9.0 psi after T+70 min), cutting at T+150 min produces an uncontrolled 930.0 kg RELEASE. Enabling calibrated logging QA (catches poor bond at T+45), outer-barrier pressure testing (T+100), AI Layer 2 zero-variance freeze detection (T+85), or pairing maintained gauges with ΔP trending (T+94) postpones the cut, bleeds annular pressure to 0 psi, and yields SAFE (0.0 kg). Crucially, ΔP trending alone with a frozen gauge still ends in RELEASE—demonstrating why sensor maintenance and ML integrity monitoring are inseparable.")
    add_bullet(doc, "Limitations & Takeaway: ", "AI anomaly detection flags frozen or inconsistent ΔP traces and overdue calibration records, but cannot physically calibrate logging tools or certify well barriers.")

    add_h2(doc, "7.4 Case Study 3 (Surface Extension): Oil India Limited Tank Farm Fire, Assam (2026)")
    add_bullet(doc, "Incident Context: ", "On 6 November 2026 at ~9:05 AM, a major fire broke out at the Indirect Bath Heater (IDBH) area during maintenance at Oil India Limited's Tengakhat Intermediate Tank Farm, Assam [7]. The heater area had reportedly been isolated since 4 November 2026; seven contractor workers sustained burns (five fatalities reported by 10 November 2026), and Oil India constituted an internal inquiry committee.")
    add_bullet(doc, "Factual Boundary & Hypothetical Training Reconstruction: ", "The official press release did not establish the exact ignition root cause; therefore, this project explicitly avoids claiming any specific equipment fault or cyberattack caused the real fire. Instead, the Incident Replay Lab constructs one clearly labelled hypothetical training pathway (passing single isolation valve creeping coil pressure to 35.0 psi and 25.1% LEL by Hour 48.0 while a control-room transmitter remains frozen at 0.0 psi, igniting during hot work) to illustrate how Double-Block & Bleed LOTO, live residual-pressure monitoring, frozen-transmitter AI alerts, pre-work purging, and continuous gas testing each prevent ignition (SAFE, 0.0% LEL).")
    add_bullet(doc, "Takeaway: ", "Surface condition and transmitter-integrity monitoring extend our wellhead framework to surface equipment, strictly complementing physical LOTO isolation, gas testing, and permit-to-work barriers.")

    add_h2(doc, "7.5 Cross-Case Comparative Synthesis & Replay Outcomes")
    add_styled_table(
        doc,
        ["Comparison Dimension", "OISD Workover Rig (Main Case)", "Deepsea Bollsta P&A", "Oil India Tank Farm (Surface Ext.)"],
        [
            ["Date & Authority", "4 Feb 2026 | OISD (India) [8]", "23 Sep 2025 | Havtil (Norway) [9]", "6 Nov 2026 | OIL Press Release [7]"],
            ["Operation & Event", "Conventional perforation -> Gas blowout", "13 3/8-in casing cut -> ~930 kg gas/water release", "IDBH maintenance -> Major fire (cause under inquiry)"],
            ["Key Technical / Data Lapse", "GTO/offset conflict, light fluid, poor CBL, no shear ram, trip tank isolated", "Outer barrier failure, uncalibrated logging, unused ΔP, poor gauge upkeep", "Hypothetical replay: passing valve + frozen PT + hot work"],
            ["Project Layer 1 (PdM) Role", "Pressure/fluid-density overbalance & BOP/trip-tank readiness", "Barrier pressure-test tracking, ΔP trending & gauge QA status", "Bath temp, residual pressure, vibration & LOTO records"],
            ["Project Layer 2 (Cyber/Integrity) Role", "Flag flat trip-tank signal while return flow rises (1 bbl kick)", "Flag frozen ΔP gauge (zero std) & inconsistent logging data", "Flag pressure transmitter frozen at 0.0 psi during cooling"],
        ],
        caption="Table 7.1: Cross-Case Comparative Matrix Mapping Documented Incidents to Dual-Layer Modules",
        col_widths=[1.4, 1.7, 1.6, 1.6],
        font_size=8.4,
    )

    add_styled_table(
        doc,
        ["Case Study", "As-Happened Replay Outcome", "With All Fixes Outcome", "Single-Fix & Partial-Fix Replay Behavior"],
        [
            ["OISD Workover Rig (oisd)", f"{cs_sum['oisd']['as_happened']['status']} (338.9 bbl influx)", f"{cs_sum['oisd']['with_fixes']['status']} (0.0 bbl)", "fix_pore_estimate / fluid_sg 1.15 -> SAFE; trip_tank / ai_monitoring / shear_ram -> CONTROLLED (18.0–28.6 bbl); cement_good alone -> BLOWOUT."],
            ["Deepsea Bollsta (bollsta)", f"{cs_sum['bollsta']['as_happened']['status']} (930.0 kg gas)", f"{cs_sum['bollsta']['with_fixes']['status']} (0.0 kg)", "log_calibrated / outer_barrier_test / ai_monitoring / (dp_trended + gauge_maintained) -> SAFE; dp_trended or gauge_maintained alone -> RELEASE."],
            ["Oil India IDBH (oil_idbh)", f"{cs_sum['oil_idbh']['as_happened']['status']} (25.1% LEL, 650 °C)", f"{cs_sum['oil_idbh']['with_fixes']['status']} (0.0% LEL)", "Each single safeguard (double_block_bleed, residual_pressure_monitor, ai_monitoring, purge_before_work, continuous_gas_test) -> SAFE."],
        ],
        caption="Table 7.2: Verified Simulation Outcomes Across All 3 Reconstructed Case Studies (test_case_sims.py)",
        col_widths=[1.3, 1.35, 1.25, 2.4],
        font_size=8.4,
    )

    add_embedded_figure(
        doc,
        "report_figures/fig_7_1_case_studies_replay_comparison.png",
        "Figure 7.1: Reconstructed Time-Series Comparison Across All Three Case Studies (As Happened vs. With Fixes)",
        width_in=6.3,
    )

    add_image_placeholder(
        doc,
        fig_label="Figure 7.2",
        title="Incident Replay Lab (Tab 3) — OISD Workover Rig Blowout Live Replay & Comparison",
        what_belongs="Screenshot of Tab 3 ('3. Incident Replay (Case Studies)') showing the OISD Workover Rig schematic during blowout vs. after applying fixes, with the live event log and 'As it happened vs With your fixes' comparison table.",
        steps_for_friends=(
            "1. Open http://localhost:8505 and click '3. Incident Replay (Case Studies)'.\n"
            "2. Select 'OISD Workover Rig Blowout (2026)', click '⏭ Skip to end' (or Play to T+97 min) to show BLOWOUT.\n"
            "3. Optionally toggle 'Enable Dual-Layer AI monitoring' or 'Apply all fixes' to capture the comparison table turning green.\n"
            "4. Paste the full-width screenshot inside this box."
        ),
    )

    add_image_placeholder(
        doc,
        fig_label="Figure 7.3",
        title="Incident Replay Lab (Tab 3) — Deepsea Bollsta & Oil India IDBH Replays",
        what_belongs="Combined screenshot showing the Deepsea Bollsta (frozen ΔP gauge at 9.0 psi & 930 kg plume) and Oil India IDBH (hypothetical passing valve + frozen PT at 0.0 psi) schematic replays.",
        steps_for_friends=(
            "1. In Tab 3 ('3. Incident Replay'), click 'Equinor Deepsea Bollsta (2025)' and click '⏭ Skip to end' -> take screenshot.\n"
            "2. Click 'Oil India Tank Farm Fire (2026)' and click '⏭ Skip to end' -> take screenshot.\n"
            "3. Place both screenshots side-by-side in PowerPoint/Paint, save as one image, and paste here."
        ),
    )

    # =========================================================================
    # CHAPTER 8
    # =========================================================================
    add_h1(doc, "CHAPTER 8: CLAIMS, RESEARCH BOUNDARIES, LIMITATIONS & FUTURE ROADMAP", page_break=True)

    add_h2(doc, "8.1 Research Claims vs. Operational Boundaries")
    add_p(
        doc,
        "A core requirement of sound Research Methodology is stating precisely what an experimental prototype proves and what "
        "it must never overclaim. Table 8.1 formalizes the project's claims and operational boundaries."
    )
    add_styled_table(
        doc,
        ["What This Research Prototype CAN Claim", "What This Prototype MUST NOT Claim"],
        [
            ["Can identify abnormal multivariate patterns in historical and streaming well data.", "Cannot guarantee prevention of blowouts, fires, or mechanical failures."],
            ["Can estimate probability/risk of impending downtime on validated temporal models.", "Cannot predict every failure mode outside the observed 2-month ESP baseline."],
            ["Can flag suspicious, frozen, drifting, or physically inconsistent sensor readings.", "Cannot confirm every anomaly is a malicious cyberattack (could be wiring/calibration)."],
            ["Can highlight overdue maintenance, fluid-density mismatches, and isolation checks.", "Cannot replace physical equipment inspections, LOTO, or gas testing."],
            ["Can integrate well parameters, ΔP trends, and barrier records into one dashboard.", "Cannot independently verify cement bond quality or well-barrier integrity."],
            ["Can provide early-warning decision support and sensor-first triage (Scenario C).", "Cannot replace industrial SCADA/PLC controllers, BOP systems, or SIS."],
        ],
        caption="Table 8.1: Verified Research Claims vs. Operational Safety Boundaries",
        col_widths=[3.15, 3.15],
        font_size=8.9,
    )

    add_h2(doc, "8.2 Methodological & Prototype Limitations")
    add_bullet(doc, "1. Synthetic Two-Month Horizon: ", "While 86,400 one-minute records support rigorous prototype validation, synthetic physics-coupled data cannot fully capture rare multi-year reservoir scale, sand slugging, or hardware-specific VSD harmonics present in live field historians.")
    add_bullet(doc, "2. Slow-Drift Detection Sensitivity: ", "On unseen Test Days 43–60, Sensor_Drift achieved 81.33% detection rate (compared with 100.0% for Spike, FDI, and Physical Inconsistency) because the earliest minutes of a gradual +145 psi bias overlap with natural ±1.6–3.5 psi diurnal fluctuations.")
    add_bullet(doc, "3. Single-Well Scope in Core Dataset: ", "The 60-day telemetry file models a single ESP well (W-001), whereas field deployments monitor multi-well gathering manifolds where cross-well offset correlations can further strengthen anomaly detection.")
    add_bullet(doc, "4. Reconstructed Case-Study Constants: ", "Numerical parameters in Tab 3 replays (depth, pressures, LEL rates) are illustrative engineering assumptions rather than raw confidential company logs.")

    add_h2(doc, "8.3 Future Research & Deployment Enhancements")
    add_bullet(doc, "1. Real Field Historian & HIL PLC Validation: ", "Connect the REST pipeline to a physical Modbus TCP PLC/RTU testbed and multi-year public field datasets (such as Equinor Volve production data) to benchmark seasonal drift adaptation.")
    add_bullet(doc, "2. Sequence Deep Learning & Adaptive Change-Point Detection: ", "Pair Random Forest with CUSUM / Page-Hinkley change-point detectors or lightweight 1D-TCN / LSTM models to boost early-stage slow-drift recall above 95%.")
    add_bullet(doc, "3. Multi-Well Field Topology & Role-Based Audit Logging: ", "Extend the dashboard to multi-well pad monitoring with persistent SQLite operator acknowledgement logs and automated OPC-UA/Modbus read-only gateway enforcement.")

    # =========================================================================
    # CHAPTER 9
    # =========================================================================
    add_h1(doc, "CHAPTER 9: CONCLUSION", page_break=True)
    add_p(
        doc,
        "This 7th Semester Research Methodology Project demonstrated that predictive maintenance and OT/SCADA measurement "
        "integrity must be engineered as parallel, mutually reinforcing layers rather than isolated silos. Through a structured "
        "seven-stage research methodology, we synthesized an 86,400-minute physics-informed ESP wellhead dataset, engineered "
        "26 domain and rolling temporal features, and validated both intelligence layers on an unseen 18-day chronological test "
        "split without data leakage."
    )
    add_p(
        doc,
        "Empirically, Layer 1 Random Forest and HistGradientBoostingClassifier achieved F1-scores of 0.9838 and 0.9865 "
        "(ROC-AUC 0.9986 and 0.9973), while Layer 2's Physics-Informed Hybrid Isolation Forest achieved 1.0000 precision, "
        "0.9465 recall, and 0.9725 F1-score—eliminating false alarms during genuine mechanical degradation. Furthermore, the "
        "custom web command console (http://localhost:8505) and Incident Replay Lab bridge machine-learning metrics with real "
        "petroleum engineering practice across the OISD workover blowout, Deepsea Bollsta P&A release, and Oil India IDBH fire "
        "case studies. Positioned strictly as a transparent early-warning decision-support system, the framework empowers field "
        "engineers to verify measurement trustworthiness first while retaining every established physical safety barrier."
    )

    # =========================================================================
    # REFERENCES
    # =========================================================================
    add_h1(doc, "REFERENCES", page_break=True)
    refs = [
        '[1] A. M. Salem, M. S. Yakoot, and O. Mahmoud, "A novel machine learning model for autonomous analysis and diagnosis of well integrity failures in artificial-lift production systems," Advances in Geo-Energy Research, vol. 6, no. 2, pp. 123–142, 2022, doi: 10.46690/ager.2022.02.05.',
        '[2] S. Arena, G. Manca, S. Murru, P. F. Orrù, R. Perna, and D. Reforgiato Recupero, "Data Science Application for Failure Data Management and Failure Prediction in the Oil and Gas Industry: A Case Study," Applied Sciences, vol. 12, no. 21, p. 11103, Oct. 2022.',
        '[3] M. Wang, X. Su, H. Song, Y. Wang, and X. Yang, "Enhancing predictive maintenance strategies for oil and gas equipment through ensemble learning modeling," Journal of Petroleum Exploration and Production Technology, vol. 15, art. 46, Feb. 2025.',
        '[4] S. Mokhtari, A. Abbaspour, K. K. Yen, and A. Sargolzaei, "A Machine Learning Approach for Anomaly Detection in Industrial Control Systems Based on Measurement Data," Electronics, vol. 10, no. 4, p. 407, Feb. 2021, doi: 10.3390/electronics10040407.',
        '[5] M. Altaha and S. Hong, "Anomaly Detection for SCADA System Security Based on Unsupervised Learning and Function Codes Analysis in the DNP3 Protocol," Electronics, vol. 11, no. 14, p. 2184, Jul. 2022, doi: 10.3390/electronics11142184.',
        '[6] K. Stouffer, V. Pillitteri, M. Pease, S. Lightman, C. Tang, T. Zimmerman, A. Hahn, S. Saravia, A. Sherule, and M. Thompson, "Guide to Operational Technology (OT) Security," NIST Special Publication 800-82 Rev. 3, National Institute of Standards and Technology, Gaithersburg, MD, USA, Sep. 2023.',
        '[7] Oil India Limited (OIL), "Press Release: Tengakhat Intermediate Tank Farm Fire Incident," Official Corporate Disclosure, NSE India Archives, Nov. 6, 2026. [Online]. Available: https://nsearchives.nseindia.com/corporate/OIL_06112026170007_Press_Release06112026_signed.pdf',
        '[8] Oil Industry Safety Directorate (OISD), "Gas Blowout Incident at Workover Rig," Case Study OISD/CS/2025-26/E&P/21, Ministry of Petroleum & Natural Gas, Govt. of India, 2026. [Online]. Available: https://www.oisd.gov.in/public/assets/upload/CaseStudies/1770813058_812ceb2e62f725b67727.pdf',
        '[9] Norwegian Ocean Industry Authority (Havtil), "Equinor — Deepsea Bollsta — Investigation of Well-Control Incident (Q-21 Well, Troll Field)," Investigation Report, May 18, 2026. [Online]. Available: https://www.havtil.no/en/supervision/investigation-reports/2026/equinor---deepsea-bollsta---investigation-of-well-control-incident/',
        '[10] International Electrotechnical Commission (IEC), "ISA/IEC 62443-4-2: Security for industrial automation and control systems — Part 4-2: Technical security requirements for IACS components," IEC Standard, 2019.',
        '[11] Modbus Organization, "MODBUS Application Protocol Specification V1.1b3," Hopkinton, MA, USA, Apr. 2012.',
        '[12] L. Breiman, "Random Forests," Machine Learning, vol. 45, no. 1, pp. 5–32, Oct. 2001.',
        '[13] F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," in Proc. 8th IEEE International Conference on Data Mining (ICDM), Pisa, Italy, 2008, pp. 413–422.',
        '[14] B. Schölkopf, J. C. Platt, J. Shawe-Taylor, A. J. Smola, and R. C. Williamson, "Estimating the Support of a High-Dimensional Distribution," Neural Computation, vol. 13, no. 7, pp. 1443–1471, Jul. 2001.',
        '[15] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.',
        '[16] Oil Industry Safety Directorate (OISD), "OISD-STD-174: Well Control," Standard for Exploration & Production Operations, New Delhi, India.',
    ]
    for r_txt in refs:
        add_p(doc, r_txt, size=9.8, space_after=5)

    # =========================================================================
    # APPENDICES
    # =========================================================================
    add_h1(doc, "APPENDIX A: TECHNICAL KEYWORDS & DEFINITIONS", page_break=True)
    add_styled_table(
        doc,
        ["Keyword / Term", "Technical Definition in Project Context"],
        [
            ["ESP (Electric Submersible Pump)", "Downhole centrifugal artificial-lift pump driven by a submerged electric motor to lift reservoir fluids."],
            ["THP (Tubing Head Pressure)", "Surface pressure measured at the top of the production tubing string (baseline ~280 psi)."],
            ["CHP (Casing Head Pressure)", "Surface pressure measured in the annulus between production tubing and casing (baseline ~150 psi)."],
            ["BHP / DHG", "Bottomhole Pressure measured by a downhole gauge near the producing interval (~1250 psi)."],
            ["Differential Pressure (ΔP)", "Pressure difference between two measurement points (e.g., BHP - THP or P1 - P2) indicating flow/barrier state."],
            ["Hydrostatic Pressure (Ph)", "Pressure exerted by a vertical fluid column of density ρ and height h: Ph = ρ · g · h."],
            ["CBL-VDL", "Cement Bond Log – Variable Density Log used to evaluate cement sheath bonding behind casing."],
            ["BOP & Shear Ram", "Blowout Preventer safety stack; a shear ram cuts wireline/tubulars inside the wellbore to seal against kicks."],
            ["Trip Tank", "Small calibrated tank used to continuously track minor fluid-volume gains or losses during well operations."],
            ["IDBH", "Indirect Bath Heater; surface vessel warming crude oil/gas through a heated water/glycol bath."],
            ["LEL (%)", "Lower Explosive Limit; minimum vapour concentration in air capable of ignition (stop-work threshold >= 10% LEL)."],
            ["SCADA / RTU", "Supervisory Control and Data Acquisition / Remote Terminal Unit polling wellhead sensors."],
            ["Modbus Function Code", "Protocol command identifier: Func 03 reads registers; Func 05/06/16 perform coil or register writes."],
            ["False-Data Injection (FDI)", "Malicious or corrupted telemetry alteration causing reported values to diverge from true physical behavior."],
            ["Sensor Freezing", "Condition where a transmitter reports a constant flatline value (rolling std ~ 0) despite changing surroundings."],
            ["Chronological Split", "Time-ordered train/test split (Days 1–42 train, Days 43–60 test) preventing future-data leakage."],
            ["Isolation Forest", "Unsupervised tree ensemble isolating anomalous observations via shorter average random partition path lengths."],
            ["HistGradientBoostingClassifier", "Scikit-learn histogram-based gradient boosting ensemble (XGBoost-style) for fast tabular classification."],
        ],
        caption="Table A.1: Technical Glossary Across Petroleum Engineering, Machine Learning, and OT Security",
        col_widths=[2.0, 4.3],
        font_size=8.8,
    )

    add_h1(doc, "APPENDIX B: MATHEMATICAL FORMULATIONS", page_break=True)
    add_p(doc, "1. Wellbore Hydrostatic Pressure & Overbalance (OISD Case Study):", bold=True, color=C_NAVY)
    add_code_block(
        doc,
        "Ph (psi) = [ rho_sg * 1000 (kg/m^3) * 9.81 (m/s^2) * h (m) ] / 6894.76\n"
        "Overbalance (psi) = Ph_effective - P_formation\n"
        "Example at h = 2200 m, P_formation = 3350 psi:\n"
        "  - SG 1.02 (as happened) -> Ph = 3192 psi -> Overbalance = -158 psi (Underbalanced -> Kick)\n"
        "  - SG 1.15 (re-weighted) -> Ph = 3599 psi -> Overbalance = +249 psi (Safe Overbalance)"
    )
    add_p(doc, "2. Engineered Differential Pressure & Temporal Rolling Features (15-Minute Window W = 15):", bold=True, color=C_NAVY)
    add_code_block(
        doc,
        "DeltaP_wellbore(t) = BHP(t) - THP(t)\n"
        "DeltaP_surface(t)  = THP(t) - CHP(t)\n"
        "RollMean_15(t)     = (1 / 15) * sum_{k=0..14} x(t - k)\n"
        "RollStd_15(t)      = sqrt( (1 / 14) * sum_{k=0..14} (x(t - k) - RollMean_15(t))^2 )\n"
        "ROC_15(t)          = x(t) - x(t - 15)\n"
        "BaselineDev(t)     = x(t) - x_nominal"
    )
    add_p(doc, "3. Hybrid Layer 2 Cyber / Measurement Anomaly Score (0–100):", bold=True, color=C_NAVY)
    add_code_block(
        doc,
        "s_IF(x)       = clip( (-score_samples(x) - 0.46) / 0.28 * 100, 0, 100 )\n"
        "FreezeFlag    = (THP_RollStd_15 < 0.05) AND (RPM > 1000) AND (CHP_RollStd_15 > 1.0)\n"
        "ModbusTamper  = (modbus_function_code != 3)\n"
        "HybridScore   = max(s_IF(x), rule_floor) if any_physics_or_protocol_flag else 0.45 * s_IF(x)"
    )

    add_h1(doc, "APPENDIX C: CORE IMPLEMENTATION EXCERPTS", page_break=True)
    add_p(doc, "Excerpt 1 — Chronological Split & Dual-Layer Training (ml_pipeline.py):", bold=True, color=C_NAVY)
    add_code_block(
        doc,
        'split_idx = int(len(df) * 0.70)  # First 42 days = Train (60,479), Last 18 days = Test (25,921)\n'
        'train_df = df.iloc[:split_idx].copy()\n'
        'test_df = df.iloc[split_idx:].copy()\n'
        'pdm_scaler = StandardScaler()\n'
        'X_train_pdm = pdm_scaler.fit_transform(train_df[pdm_features])\n'
        'X_test_pdm = pdm_scaler.transform(test_df[pdm_features])\n'
        '# Layer 2 trained ONLY on anomaly-free rows (is_anomaly == 0)\n'
        'normal_train_mask = train_df["is_anomaly"] == 0\n'
        'X_train_cyber_normal = cyber_scaler.fit_transform(train_df.loc[normal_train_mask, cyber_features])'
    )
    add_p(doc, "Excerpt 2 — REST API Case-Study Replay Endpoint (server.py):", bold=True, color=C_NAVY)
    add_code_block(
        doc,
        'if parsed.path == "/api/case_sim":\n'
        '    case_id = body.get("case_id")\n'
        '    if case_id not in case_study_sim.AS_HAPPENED:\n'
        '        self._send_json({"error": f"Unknown case_id: {case_id}"}, status=400)\n'
        '        return\n'
        '    result = case_study_sim.simulate_case(case_id, body.get("params") or {})\n'
        '    self._send_json(result)'
    )

    add_h1(doc, "APPENDIX D: QUICK CHECKLIST FOR TEAMMATES BEFORE FINAL SUBMISSION", page_break=True)
    add_p(
        doc,
        "Before exporting this report to PDF for UPES submission, teammates should complete the following quick items:"
    )
    add_styled_table(
        doc,
        ["Item", "Where in Document", "Action Needed by Teammates"],
        [
            ["1. Team & Mentor Names", "Cover Page, Declaration, Approval, Acknowledgements", "Replace [Teammate 2/3/4 Name], [SAP ID], and [Project Mentor / Guide Name] with exact names."],
            ["2. UPES Logo", "Cover Page", "Insert the official UPES PNG logo inside the compact placeholder box."],
            ["3. Figure 1.2 (Concept)", "Chapter 1 (Section 1.5)", "Create the conceptual ESP well + SCADA threat diagram in Canva/Draw.io per instructions and paste."],
            ["4. Figure 6.3 (Tab 1 UI)", "Chapter 6 (Section 6.4)", "Start 'python server.py', capture Scenario A & Scenario C on http://localhost:8505, and paste."],
            ["5. Figure 6.4 (Tab 2 UI)", "Chapter 6 (Section 6.4)", "Capture Tab 2 ('2. Interactive Simulator') showing highlighted well parts & 'Fix This Part' button."],
            ["6. Figure 7.2 (OISD Replay)", "Chapter 7 (Section 7.5)", "Capture Tab 3 ('3. Incident Replay') showing OISD Blowout vs With Fixes comparison table."],
            ["7. Figure 7.3 (Bollsta & OIL)", "Chapter 7 (Section 7.5)", "Capture Deepsea Bollsta & Oil India IDBH replays side-by-side and paste."],
            ["8. Update Word Page Numbers", "Table of Contents / Lists", "All chapters start cleanly on new pages; verify page numbers in Word before 'Save As PDF'."],
        ],
        caption="Table D.1: Teammate Finalization Checklist (Placeholders & Screenshot Gaps)",
        col_widths=[1.4, 1.8, 3.1],
        font_size=8.8,
    )

    doc.save(str(OUT_DOCX))
    print(f"[SUCCESS] Generated {OUT_DOCX.resolve()} ({OUT_DOCX.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build_report()
