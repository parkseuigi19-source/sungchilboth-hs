"""
차트 및 그래프 생성 유틸리티
성취도 시각화를 위한 차트 생성
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용
from matplotlib import font_manager, rc
import numpy as np
from typing import Dict, List, Any
import os


# 한글 폰트 설정
try:
    font_path = "C:/Windows/Fonts/malgun.ttf"
    if os.path.exists(font_path):
        font_name = font_manager.FontProperties(fname=font_path).get_name()
        rc('font', family=font_name)
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass


def create_achievement_bar_chart(
    data: Dict[str, float],
    output_path: str,
    title: str = "성취도 분석"
):
    """
    성취도 막대 그래프 생성
    
    Args:
        data: {성취기준: 점수} 딕셔너리
        output_path: 출력 파일 경로
        title: 그래프 제목
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    standards = list(data.keys())
    scores = list(data.values())
    
    colors_list = ['#3498DB' if score >= 80 else '#F39C12' if score >= 60 else '#E74C3C' 
                   for score in scores]
    
    bars = ax.bar(standards, scores, color=colors_list, alpha=0.8)
    
    # 값 표시
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel('성취기준', fontsize=12)
    ax.set_ylabel('점수', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_heatmap(
    data: List[Dict[str, Any]],
    output_path: str,
    title: str = "강약점 히트맵"
):
    """
    강약점 히트맵 생성
    
    Args:
        data: 히트맵 데이터 리스트
        output_path: 출력 파일 경로
        title: 그래프 제목
    """
    fig, ax = plt.subplots(figsize=(12, 3))
    
    standards = [d['standard_code'] for d in data]
    scores = [d['score'] for d in data]
    
    # 히트맵 데이터를 2D 배열로 변환
    heatmap_data = np.array([scores])
    
    im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    
    # 축 설정
    ax.set_xticks(np.arange(len(standards)))
    ax.set_xticklabels(standards)
    ax.set_yticks([])
    
    # 값 표시
    for i in range(len(standards)):
        text = ax.text(i, 0, f'{scores[i]:.1f}',
                      ha="center", va="center", color="black", fontsize=10)
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # 컬러바
    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.1)
    cbar.set_label('점수', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_line_chart(
    data: List[Dict[str, Any]],
    output_path: str,
    title: str = "학습 진행도",
    x_label: str = "기간",
    y_label: str = "점수"
):
    """
    선 그래프 생성 (학습 진행도 등)
    
    Args:
        data: 데이터 리스트 (x, y 값 포함)
        output_path: 출력 파일 경로
        title: 그래프 제목
        x_label: X축 레이블
        y_label: Y축 레이블
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_values = [d.get('x', d.get('month', i)) for i, d in enumerate(data)]
    y_values = [d.get('y', d.get('average_score', 0)) for d in data]
    
    ax.plot(x_values, y_values, marker='o', linewidth=2, markersize=8, 
            color='#3498DB', label='평균 점수')
    
    # 값 표시
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        ax.text(i, y + 2, f'{y:.1f}', ha='center', fontsize=9)
    
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_pie_chart(
    data: Dict[str, int],
    output_path: str,
    title: str = "분포"
):
    """
    파이 차트 생성
    
    Args:
        data: {레이블: 값} 딕셔너리
        output_path: 출력 파일 경로
        title: 그래프 제목
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    labels = list(data.keys())
    sizes = list(data.values())
    colors_list = ['#3498DB', '#E74C3C', '#F39C12', '#2ECC71', '#9B59B6']
    
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        colors=colors_list[:len(labels)],
        autopct='%1.1f%%',
        startangle=90
    )
    
    # 텍스트 스타일
    for text in texts:
        text.set_fontsize(11)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_class_distribution_chart(
    student_scores: List[float],
    output_path: str,
    title: str = "학급 점수 분포"
):
    """
    학급 점수 분포 히스토그램 생성
    
    Args:
        student_scores: 학생 점수 리스트
        output_path: 출력 파일 경로
        title: 그래프 제목
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bins = [0, 40, 60, 80, 100]
    colors_list = ['#E74C3C', '#F39C12', '#3498DB', '#2ECC71']
    
    n, bins, patches = ax.hist(student_scores, bins=bins, color='#3498DB', 
                                edgecolor='black', alpha=0.7)
    
    # 각 구간별 색상 지정
    for i, patch in enumerate(patches):
        patch.set_facecolor(colors_list[i])
    
    # 값 표시
    for i in range(len(n)):
        if n[i] > 0:
            ax.text((bins[i] + bins[i+1])/2, n[i], str(int(n[i])),
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('점수 구간', fontsize=12)
    ax.set_ylabel('학생 수', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # X축 레이블
    ax.set_xticks([(bins[i] + bins[i+1])/2 for i in range(len(bins)-1)])
    ax.set_xticklabels(['0-40', '40-60', '60-80', '80-100'])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
