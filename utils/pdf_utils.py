"""
PDF 생성 유틸리티
포트폴리오, 리포트, 모의고사 PDF 생성
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, Any
import os
from datetime import datetime


# 한글 폰트 등록 (시스템에 설치된 폰트 사용)
# Windows의 경우 맑은 고딕 사용
try:
    font_path = "C:/Windows/Fonts/malgun.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Malgun', font_path))
        KOREAN_FONT = 'Malgun'
    else:
        KOREAN_FONT = 'Helvetica'  # 폴백
except:
    KOREAN_FONT = 'Helvetica'


# OpenMP 에러 방지 및 Matplotlib 백엔드 설정
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import numpy as np
from reportlab.platypus import Image as RLImage

# 성취도 색상 정의
COLOR_PRIMARY = colors.HexColor('#9D4EDD') # 보라색 (Web UI 메인)
COLOR_SECONDARY = colors.HexColor('#3F3D56') # 어두운 군청색
COLOR_BG_LIGHT = colors.HexColor('#F8F4FF') # 연보라 배경 (Web UI 배경)
COLOR_SUCCESS = colors.HexColor('#4CAF50') 
COLOR_WARNING = colors.HexColor('#FF9800') 
COLOR_DANGER = colors.HexColor('#F44336') 
COLOR_TEXT_MAIN = colors.HexColor('#2C3E50')
COLOR_TEXT_SUB = colors.HexColor('#7F8C8D')

def _get_plt_font():
    """matplotlib을 위한 한글 폰트 설정 (맑은 고딕 우선)"""
    from matplotlib import font_manager, rc
    import platform
    
    font_name = None
    system = platform.system()
    
    if system == 'Windows':
        if os.path.exists("C:/Windows/Fonts/malgun.ttf"):
            font_name = font_manager.FontProperties(fname="C:/Windows/Fonts/malgun.ttf").get_name()
    elif system == 'Darwin': # Mac
        font_name = 'AppleGothic'
    elif system == 'Linux':
        font_name = 'NanumGothic'
        
    if font_name:
        rc('font', family=font_name)
    else:
        # 폰트 없을 경우 기본 설정 유지 (깨질 수 있음)
        pass 
        
    rc('axes', unicode_minus=False)

def create_trend_chart(trend_data):
    """성취도 추이 선 그래프 생성"""
    _get_plt_font()
    labels = [d['label'] for d in trend_data]
    scores = [d['score'] for d in trend_data]
    
    plt.figure(figsize=(6, 3.5), dpi=120) # 사이즈 약간 증가
    
    # 그리드 및 스타일
    plt.grid(axis='y', linestyle='--', alpha=0.3, color='#E0E0E0')
    plt.axhline(0, color='#E0E0E0', linewidth=1)
    
    # 데이터 플롯
    plt.plot(labels, scores, marker='o', color='#9D4EDD', linewidth=2, markersize=6, label='점수')
    plt.fill_between(labels, scores, color='#9D4EDD', alpha=0.1)
    
    # 축 설정
    plt.ylim(0, 105)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color('#CCCCCC')
    plt.gca().spines['bottom'].set_color('#CCCCCC')
    
    plt.tight_layout()
    
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', transparent=True)
    plt.close()
    img_data.seek(0)
    return RLImage(img_data, width=8*cm, height=4.6*cm)

def create_radar_chart(area_scores):
    """영역별 성취도 레이더 차트 생성"""
    _get_plt_font()
    if not area_scores:
        area_scores = {"데이터 없음": 0}
        
    labels = list(area_scores.keys())
    values = list(area_scores.values())
    
    # 레이더 차트 닫기
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), dpi=120)
    
    # 스타일링
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    # 배경 그리드
    plt.rgrids([20, 40, 60, 80, 100], color='#DDDDDD', angle=0, fontsize=8)
    ax.set_rlabel_position(0)
    
    # 데이터 그리기
    ax.plot(angles, values, color='#9D4EDD', linewidth=2, linestyle='solid')
    ax.fill(angles, values, color='#9D4EDD', alpha=0.2)
    
    # 레이블
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10, color='#333333')
    
    # 테두리 제거
    ax.spines['polar'].set_visible(False)
    
    plt.tight_layout()
    
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', transparent=True)
    plt.close()
    img_data.seek(0)
    return RLImage(img_data, width=7*cm, height=7*cm)

def create_portfolio_pdf(portfolio_data: Dict[str, Any], output_path: str):
    """
    고급스러운 디자인의 포트폴리오 PDF 생성 (Web UI 매칭)
    """
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=A4,
        rightMargin=1.2*cm,
        leftMargin=1.2*cm,
        topMargin=1.2*cm,
        bottomMargin=1.2*cm
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    # 커스텀 스타일 정의
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName=KOREAN_FONT,
        fontSize=26,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=5
    )
    
    header_subtitle_style = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName=KOREAN_FONT,
        fontSize=11,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=5
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName=KOREAN_FONT,
        fontSize=14,
        textColor=COLOR_SECONDARY,
        spaceBefore=15,
        spaceAfter=10,
        leading=16
    )
    
    stat_val_style = ParagraphStyle(
        'StatVal',
        fontName=KOREAN_FONT,
        fontSize=18,
        textColor=COLOR_PRIMARY,
        alignment=TA_CENTER,
        bold=True,
        leading=22
    )
    
    stat_label_style = ParagraphStyle(
        'StatLabel',
        fontName=KOREAN_FONT,
        fontSize=9,
        textColor=COLOR_TEXT_SUB,
        alignment=TA_CENTER
    )
    
    card_header_style = ParagraphStyle(
        'CardHeader',
        fontName=KOREAN_FONT,
        fontSize=12,
        textColor=COLOR_TEXT_MAIN,
        bold=True,
        leading=14
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=KOREAN_FONT,
        fontSize=10,
        leading=15,
        textColor=COLOR_TEXT_MAIN
    )
    
    small_text_style = ParagraphStyle(
        'SmallText',
        fontName=KOREAN_FONT,
        fontSize=9,
        textColor=COLOR_TEXT_SUB,
        leading=12
    )

    # ================= 1. 헤더 섹션 =================
    header_content = [
        [Paragraph(f"📂 나의 E-포트폴리오", header_title_style)],
        [Paragraph("학습 여정을 한눈에 확인하세요", header_subtitle_style)]
    ]
    
    header_table = Table(header_content, colWidths=[18.5*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 25),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
        ('ROUNDEDCORNERS', [12, 12, 12, 12]), # ReportLab 최신 버전 지원 확인 필요, 안되면 무시됨
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.8*cm))

    # ================= 2. 통계 요약 박스 (3단) =================
    stats_content = [[
        # Box 1
        Table([[Paragraph(str(portfolio_data.get('total_questions', 0)), stat_val_style)],
               [Paragraph("총 문제 수", stat_label_style)]], 
              colWidths=[5.8*cm], rowHeights=[1.2*cm, 0.8*cm]),
        # Box 2
        Table([[Paragraph(str(portfolio_data.get('average_score', 0)), stat_val_style)],
               [Paragraph("평균 점수", stat_label_style)]],
              colWidths=[5.8*cm], rowHeights=[1.2*cm, 0.8*cm]),
        # Box 3
        Table([[Paragraph(str(portfolio_data.get('total_score', 0)), stat_val_style)],
               [Paragraph("총점", stat_label_style)]],
              colWidths=[5.8*cm], rowHeights=[1.2*cm, 0.8*cm]),
    ]]
    
    stats_container = Table(stats_content, colWidths=[6.2*cm, 6.2*cm, 6.2*cm])
    stats_container.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # 내부 박스 스타일링 (각각의 Table에 대해)
    for i in range(3):
        inner_table = stats_content[0][i]
        inner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey), # 테두리
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        
    story.append(stats_container)
    story.append(Spacer(1, 0.8*cm))

    # ================= 3. 차트 섹션 (2단) =================
    # 헤더 추가
    chart_headers = Table([
        [Paragraph("📈 성취도 추이", section_title_style), 
         Paragraph("🎯 영역별 성취도", section_title_style)]
    ], colWidths=[9.25*cm, 9.25*cm])
    story.append(chart_headers)
    story.append(Spacer(1, 0.2*cm))

    chart1 = create_trend_chart(portfolio_data.get('trend_data', []))
    chart2 = create_radar_chart(portfolio_data.get('area_scores', {}))
    
    charts_row = Table([
        [chart1, chart2]
    ], colWidths=[9.25*cm, 9.25*cm])
    charts_row.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, 0), colors.white),
        ('BACKGROUND', (1, 0), (1, 0), colors.white),
        ('BOX', (0, 0), (0, 0), 0.5, colors.lightgrey),
        ('BOX', (1, 0), (1, 0), 0.5, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(charts_row)
    story.append(Spacer(1, 0.8*cm))

    # ================= 4. 강점/약점 섹션 (2단) =================
    sw_headers = Table([
        [Paragraph("💪 강점 영역", section_title_style), 
         Paragraph("🎯 약점 영역", section_title_style)]
    ], colWidths=[9.25*cm, 9.25*cm])
    story.append(sw_headers)
    story.append(Spacer(1, 0.2*cm))

    # 데이터 포맷팅
    strong_items = []
    if portfolio_data.get('strong_areas'):
        for item in portfolio_data['strong_areas']:
            # item이 dict인지 str인지 확인 (JSON 파싱 이슈 대응 후)
            concept = item.get('standard_code') if isinstance(item, dict) else str(item)
            score = item.get('average_score') if isinstance(item, dict) else 0
            strong_items.append(Paragraph(f"• <b>{concept}</b> <font color='#7F8C8D' size='9'>({score}점)</font>", normal_style))
    else:
        strong_items.append(Paragraph("데이터가 없습니다.", small_text_style))

    weak_items = []
    if portfolio_data.get('weak_areas'):
        for item in portfolio_data['weak_areas']:
            concept = item.get('standard_code') if isinstance(item, dict) else str(item)
            # recommendation 필드는 없을 수도 있음
            # rec = item.get('recommendation', '학습 필요') if isinstance(item, dict) else ''
            weak_items.append(Paragraph(f"• <b>{concept}</b>", normal_style))
            # weak_items.append(Paragraph(f"  └ {rec}", small_text_style))
    else:
        weak_items.append(Paragraph("약점이 없습니다! 👍", normal_style))

    # 리스트를 테이블 셀로 변환
    sw_content = Table([
        [strong_items, weak_items]
    ], colWidths=[9.25*cm, 9.25*cm])
    
    sw_content.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, 0), colors.white),
        ('BACKGROUND', (1, 0), (1, 0), colors.white),
        ('BOX', (0, 0), (0, 0), 0.5, colors.lightgrey),
        ('BOX', (1, 0), (1, 0), 0.5, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(sw_content)
    story.append(Spacer(1, 0.8*cm))

    # ================= 5. 학습 기록 테이블 =================
    story.append(Paragraph("📚 주요 학습 기록", section_title_style))
    story.append(Spacer(1, 0.2*cm))
    
    history_header = ["날짜", "과목", "주제", "점수"]
    history_data = [history_header]
    
    for item in portfolio_data.get('learning_history', []):
        score = item.get('score', 0)
        score_color = COLOR_SUCCESS if score >= 80 else (COLOR_WARNING if score >= 60 else COLOR_DANGER)
        
        row = [
            item.get('date', ''),
            item.get('subject', ''),
            Paragraph(item.get('topic', ''), normal_style), # 긴 텍스트 줄바꿈
            Paragraph(f"<font color='{score_color.hexval()}'><b>{score}</b></font>", normal_style)
        ]
        history_data.append(row)
    
    if len(history_data) == 1:
        history_data.append(["-", "-", "기록 없음", "-"])

    # 테이블 너비 조정
    h_table = Table(history_data, colWidths=[3*cm, 2.5*cm, 10*cm, 3*cm])
    
    h_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BG_LIGHT), # 헤더 배경
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_SECONDARY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey), # 전체 그리드
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # 데이터 행 스타일
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]), # 줄무늬
    ]))
    story.append(h_table)
    
    # PDF 생성
    doc.build(story)



def create_distribution_chart(student_scores):
    """학급성취도 분포 차트 생성 (바 차트)"""
    _get_plt_font()
    if not student_scores:
        student_scores = [{"username": "데이터 없음", "average_score": 0}]
        
    names = [s['username'] for s in student_scores]
    scores = [s['average_score'] for s in student_scores]
    
    plt.figure(figsize=(8, 4), dpi=100)
    bars = plt.bar(names, scores, color='#9D4EDD', alpha=0.7)
    
    # 평균선 추가
    avg_val = np.mean(scores)
    plt.axhline(avg_val, color='red', linestyle='--', linewidth=1, label=f'학급 평균: {avg_val:.1f}')
    
    plt.ylim(0, 105)
    plt.ylabel('평균 점수')
    plt.title('학생별 성취도 현황')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', transparent=True)
    plt.close()
    img_data.seek(0)
    return RLImage(img_data, width=15*cm, height=7*cm)

def create_class_report_pdf(report_data: Dict[str, Any], output_path: str):
    """
    고급스러운 디자인의 학급 성취도 리포트 PDF 생성
    """
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    # 커스텀 스타일 정의
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName=KOREAN_FONT,
        fontSize=24,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    header_subtitle_style = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName=KOREAN_FONT,
        fontSize=12,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Heading3'],
        fontName=KOREAN_FONT,
        fontSize=14,
        textColor=COLOR_SECONDARY,
        spaceBefore=10,
        spaceAfter=15
    )
    
    stat_val_style = ParagraphStyle(
        'StatVal',
        fontName=KOREAN_FONT,
        fontSize=20,
        textColor=COLOR_PRIMARY,
        alignment=TA_CENTER,
        bold=True
    )
    
    stat_label_style = ParagraphStyle(
        'StatLabel',
        fontName=KOREAN_FONT,
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=KOREAN_FONT,
        fontSize=10,
        leading=15
    )

    # 1. 헤더 섹션
    header_table = Table([
        [Paragraph(f"📊 {report_data['class_name']} 성취도 리포트", header_title_style)],
        [Paragraph(f"과목: {report_data['subject']} | 생성일: {datetime.now().strftime('%Y-%m-%d')}", header_subtitle_style)]
    ], colWidths=[18*cm])
    
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [15, 15, 15, 15]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))

    # 2. 학급 전체 통계 요약
    stats_data = [[
        [Paragraph(str(report_data.get('total_students', 0)), stat_val_style), 
         Paragraph("총 학생 수", stat_label_style)],
        [Paragraph(str(report_data.get('average_score', 0)), stat_val_style), 
         Paragraph("학급 평균", stat_label_style)]
    ]]
    
    stats_table = Table(stats_data, colWidths=[9*cm, 9*cm])
    stats_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_BG_LIGHT),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 1*cm))

    # 3. 학생별 성취도 분포 차트
    story.append(Paragraph("📈 학생별 성취 현황", card_title_style))
    dist_chart = create_distribution_chart(report_data.get('student_scores', []))
    story.append(dist_chart)
    story.append(Spacer(1, 1*cm))

    # 4. 주요 지도 포인트 (GPT 생성)
    story.append(Paragraph("💡 주요 지도 포인트", card_title_style))
    story.append(Paragraph(report_data.get('leading_points', '리딩 포인트가 없습니다.').replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 1*cm))

    # 5. 학생별 상세 성취도 테이블
    story.append(Paragraph("👥 학생별 성취도 상세", card_title_style))
    
    history_data = [["학생명", "주요 취약 영역", "평균 점수", "성취 수준"]]
    for s in report_data.get('student_scores', []):
        score = s.get('average_score', 0)
        score_color = COLOR_SUCCESS if score >= 80 else (COLOR_WARNING if score >= 60 else COLOR_DANGER)
        level = "성취" if score >= 80 else ("보통" if score >= 60 else "노력요함")
        
        history_data.append([
            s.get('username', ''),
            "분석 중...",
            f"{score}점",
            Paragraph(f"<font color='{score_color.hexval()}'>{level}</font>", normal_style)
        ])
    
    history_table = Table(history_data, colWidths=[4*cm, 7*cm, 4*cm, 3*cm])
    history_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BG_LIGHT),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_SECONDARY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), KOREAN_FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(history_table)

    # PDF 생성
    doc.build(story)



def create_mock_exam_pdf(exam_data: Dict[str, Any], output_path: str):
    """
    모의고사 PDF 생성
    
    Args:
        exam_data: 모의고사 데이터
        output_path: 출력 파일 경로
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=KOREAN_FONT,
        fontSize=20,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName=KOREAN_FONT,
        fontSize=12,
        leading=18,
        spaceAfter=10
    )
    
    # 제목
    story.append(Paragraph(exam_data['exam_name'], title_style))
    story.append(Paragraph(f"과목: {exam_data['subject']} | 대상: {exam_data['target_grade']}", question_style))
    story.append(Paragraph(f"총 문제 수: {exam_data['total_questions']}문제", question_style))
    story.append(Spacer(1, 30))
    
    # 문제
    for idx, question in enumerate(exam_data['questions'], 1):
        story.append(Paragraph(f"{idx}. {question['question_text']}", question_style))
        story.append(Spacer(1, 15))
        
        # 페이지 당 5문제씩
        if idx % 5 == 0 and idx < len(exam_data['questions']):
            story.append(PageBreak())
    
    # PDF 생성
    doc.build(story)


def create_answer_sheet_pdf(exam_data: Dict[str, Any], output_path: str):
    """
    모의고사 정답지 PDF 생성
    
    Args:
        exam_data: 모의고사 데이터
        output_path: 출력 파일 경로
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=KOREAN_FONT,
        fontSize=20,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=KOREAN_FONT,
        fontSize=11,
        leading=16
    )
    
    # 제목
    story.append(Paragraph(f"{exam_data['exam_name']} - 정답 및 해설", title_style))
    story.append(Spacer(1, 20))
    
    # 정답 및 해설
    for idx, question in enumerate(exam_data['questions'], 1):
        story.append(Paragraph(f"{idx}번 문제", normal_style))
        story.append(Paragraph(f"정답: {question['answer']}", normal_style))
        story.append(Paragraph(f"해설: {question['explanation']}", normal_style))
        story.append(Spacer(1, 15))
    
    # PDF 생성
    doc.build(story)
