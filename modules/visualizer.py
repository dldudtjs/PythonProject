# [View] Matplotlib 활용 그래프 생성 및 이미지 변환


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
import os
import folium
from .static_data import get_2025_season_data, get_all_team_data, get_comparison_data

def create_ranking_graph():
    # ... (폰트 설정 코드는 기존과 동일 유지) ...
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
            
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
        plt.rcParams['axes.unicode_minus'] = False
    else:
        plt.rcParams['font.family'] = 'sans-serif'

    # 데이터 로드
    data = get_2025_season_data()
    months = data["labels"]
    teams = data["teams_data"]

    # 팀별 고유 색상 정의 (HTML 범례와 맞추기 위함)
    team_colors = {
        'KIA': '#EA0029', 'KT': '#000000', 'LG': '#C30452', 'NC': '#315288',
        'SSG': '#CE0E2D', '두산': '#1A1748', '롯데': '#041E42', '삼성': '#074CA1',
        '키움': '#570514', '한화': '#FC4E00'
    }

    plt.figure(figsize=(10, 6))
    
    # 그래프 그리기 (팀별 지정 색상 사용)
    for team_name, rankings in teams.items():
        color = team_colors.get(team_name, '#333333') # 색상이 없으면 기본 회색
        plt.plot(months, rankings, marker='o', label=team_name, linewidth=2, color=color)
        
    plt.ylim(10.5, 0.5)
    plt.yticks(range(1, 11), [f'{i}위' for i in range(1, 11)])
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    save_dir = os.path.join('static', 'image')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    save_path = os.path.join(save_dir, 'ranking_graph.png')
    plt.savefig(save_path)
    plt.close()

# 팀페이지 - 팀 강점/약점 분석 (WAA 레이더 차트-오각형 그래프)
def create_team_radar_charts():
    """
    모든 팀의 WAA 데이터를 0~100으로 정규화하여 레이더 차트를 생성합니다.
    (FIFA 스타일: 수치와 라벨을 그래프 바깥쪽에 고정하여 겹침 방지)
    """
    # 1. 폰트 설정
    font_path = None
    import matplotlib.font_manager as fm
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
            
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    else:
        plt.rcParams['font.family'] = 'sans-serif'

    # 2. 데이터 로드
    all_data = get_all_team_data()
    if not all_data:
        return

    # 분석할 5개 항목 정의
    categories = ['Batting_WAA', 'Baserunning_WAA', 'Defense_WAA', 'Starter_WAA', 'Reliever_WAA']
    labels = ['타격', '주루', '수비', '선발', '구원']
    
    # 각 항목별 최대/최소값 계산
    min_max = {}
    for cat in categories:
        values = [team_list[0][cat] for team_list in all_data.values()]
        min_max[cat] = {'min': min(values), 'max': max(values)}

    # 3. 팀별 차트 생성
    save_dir = os.path.join('static', 'image', 'radar')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for team_name, team_list in all_data.items():
        data = team_list[0]
        
        values = []     # 그래프 그리기용 (0~100)
        raw_values = [] # 텍스트 표시용 (실제 값)
        
        for cat in categories:
            val = data[cat]
            raw_values.append(val)
            
            min_val = min_max[cat]['min']
            max_val = min_max[cat]['max']
            
            if max_val == min_val:
                normalized_val = 50
            else:
                normalized_val = (val - min_val) / (max_val - min_val) * 100
            values.append(normalized_val)
        
        # 리스트 닫기
        values += values[:1]
        raw_values += raw_values[:1]
        
        # 각 축의 각도 계산
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        # 차트 그리기
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # ★ 수정 1: 기존의 자동 라벨(xticks) 제거
        plt.xticks([]) 
        
        # Y축 눈금 설정 (라벨 없음)
        ax.set_rlabel_position(0)
        plt.yticks([20, 40, 60, 80, 100], ["", "", "", "", ""], color="grey", size=7)
        plt.ylim(0, 100) # 그래프는 100까지만 그림
        
        # 데이터 영역 칠하기
        ax.plot(angles, values, linewidth=2, linestyle='solid', color='#002561')
        ax.fill(angles, values, '#002561', alpha=0.2)
        
        # ★ 수정 2: 라벨과 점수를 바깥쪽에 직접 배치 (FIFA 스타일)
        # 그래프 끝(100)보다 더 바깥쪽인 120, 135 위치에 텍스트를 고정시킵니다.
        for angle, label, raw in zip(angles[:-1], labels, raw_values[:-1]):            
            # 1. 실제 점수 (크고 진하게) - 위치: 120
            ax.text(angle, 120, f"{raw}", 
                    horizontalalignment='center', 
                    verticalalignment='center', 
                    size=13, weight='bold', color='#002561') # 팀 컬러
            
            # 2. 항목 이름 (작게 점수 아래에) - 위치: 138
            ax.text(angle, 138, label, 
                    horizontalalignment='center', 
                    verticalalignment='center', 
                    size=11, color='gray')

        plt.tight_layout(pad=3)

        # 이미지 저장
        file_name = f"radar_{team_name}.png"
        plt.savefig(os.path.join(save_dir, file_name), transparent=True)
        plt.close()
        
    print("팀 페이지 오각형 차트 생성 성공")

# 팀 - 팀 비교페이지 : 팀 분석 
def create_waa_table_images():
    """
    Pandas와 Matplotlib을 사용하여 WAA 분석 표를 이미지로 생성하고 저장합니다.
    (HTML 테이블 대신 Python 라이브러리 활용 능력을 보여주기 위함)
    """
    # 1. 폰트 설정 (기존 코드 재사용)
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
            
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    else:
        plt.rcParams['font.family'] = 'sans-serif'

    # 2. 데이터 로드
    all_data = get_all_team_data()
    if not all_data:
        return

    # 저장 경로 설정
    save_dir = os.path.join('static', 'image', 'table')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 분석할 항목 정의
    metrics = [
        {'key': 'Batting', 'label': '타격'},
        {'key': 'Baserunning', 'label': '주루'},
        {'key': 'Defense', 'label': '수비'},
        {'key': 'Starter', 'label': '선발'},
        {'key': 'Reliever', 'label': '구원'}
    ]

    for team_name, team_list in all_data.items():
        data = team_list[0]
        
        # 3. Pandas DataFrame 생성 (데이터 구조화)
        table_data = []
        for m in metrics:
            waa = data[f"{m['key']}_WAA"]
            rank = data[f"{m['key']}_Rank"]
            table_data.append([m['label'], waa, f"{rank}위"])
            
        df = pd.DataFrame(table_data, columns=['부문', '기록', '순위'])

        # 4. Matplotlib으로 표 그리기
        fig, ax = plt.subplots(figsize=(5, 4)) # 크기 조절
        ax.axis('off') # 축 숨기기
        ax.axis('tight')

        # 테이블 생성
        table = ax.table(cellText=df.values,
                         colLabels=df.columns,
                         loc='center',
                         cellLoc='center',
                         colColours=['#a50034']*3) # 헤더 색상 (자주색)

        # 5. 스타일링 (글자 크기, 셀 높이, 색상 조건)
        table.auto_set_font_size(False)
        table.set_fontsize(13)
        table.scale(1.2, 2) # (가로, 세로) 비율 조절

        # 셀 스타일 디테일 설정
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor('white') # 테두리 흰색 (깔끔하게)
            
            if row == 0: # 헤더 부분
                cell.set_text_props(color='white', weight='bold')
                cell.set_height(0.15)
            else: # 데이터 부분
                cell.set_height(0.12)
                # '기록' 컬럼(인덱스 1)에 대해 색상 조건 적용 (뱃지 효과 흉내)
                if col == 1: 
                    val = df.iloc[row-1, 1] # 값 가져오기
                    if val > 0.5:
                        cell.set_facecolor('#e8f0fe') # 배경을 연하게
                        cell.set_text_props(color='#d9534f', weight='bold') # 글자를 빨갛게
                    elif val < -0.5:
                        cell.set_facecolor('#e8f0fe')
                        cell.set_text_props(color='#5b7ece', weight='bold') # 글자를 파랗게
                    else:
                        cell.set_text_props(color='#555')

                # 교차 행 배경색 (가독성)
                if row % 2 == 0:
                     if col != 1: cell.set_facecolor('#f9f9f9')

        # 이미지 저장
        plt.tight_layout()
        file_name = f"table_{team_name}.png"
        plt.savefig(os.path.join(save_dir, file_name), bbox_inches='tight', dpi=100)
        plt.close()

    print("팀 분석 표(Matplotlib) 이미지 생성 성공")

# 팀 - 팀 비교페이지 : 팀별 대결 기록 
def create_match_record_images():
    """
    모든 팀 vs 상대팀의 1:1 전적 표를 이미지로 생성합니다.
    파일명 예시: record_LG_vs_한화.png
    """
    # 1. 데이터 로드
    comp_data = get_comparison_data()
    if not comp_data:
        return

    # 폰트 설정 (기존 코드 재사용 또는 확인)
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    
    # 저장 경로
    save_dir = os.path.join('static', 'image', 'record')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 2. 모든 데이터 순회하며 이미지 생성
    for team_name, records in comp_data.items():
        for record in records:
            opp_name = record['Opponent']
            
            # 자기 자신과의 기록('-')은 건너뜀
            if opp_name == team_name:
                continue

            # 3. 데이터 프레임 생성 (1행)
            # JSON 키: W, L, D, Winning_PCT
            try:
                # 승률이 문자열일 수 있으므로 float 변환 시도
                pct = float(record['Winning_PCT'])
                pct_str = f"{pct:.3f}"
            except:
                pct = 0.0
                pct_str = "-"

            row_data = [[
                f"vs {opp_name}", 
                record['W'], 
                record['D'], 
                record['L'], 
                pct_str
            ]]
            
            df = pd.DataFrame(row_data, columns=['대결', '승', '무', '패', '승률'])

            # 4. 표 그리기
            fig, ax = plt.subplots(figsize=(6, 1.2)) # 높이 아주 작게 (1행용)
            ax.axis('off')
            
            # 테이블 생성
            table = ax.table(cellText=df.values,
                             colLabels=df.columns,
                             loc='center',
                             cellLoc='center',
                             colColours=['#a50034']*5) # 헤더 자주색

            # 5. 스타일링
            table.auto_set_font_size(False)
            table.set_fontsize(14)
            table.scale(1, 1.8) # 셀 높이 조절

            for (row, col), cell in table.get_celld().items():
                cell.set_edgecolor('white') # 테두리 흰색
                
                if row == 0: # 헤더
                    cell.set_text_props(color='white', weight='bold')
                    cell.set_height(0.4)
                else: # 데이터 행
                    cell.set_height(0.5)
                    cell.set_facecolor('white') # 배경 흰색
                    
                    # 승률 컬럼(인덱스 4) 뱃지 효과
                    if col == 4:
                        if pct >= 0.5:
                            cell.set_text_props(color='white', weight='bold') 
                            cell.set_facecolor('#d9534f') # 빨강 배경
                        else:
                            cell.set_text_props(color='white', weight='bold')
                            cell.set_facecolor('#5b7ece') # 파랑 배경

            # 이미지 저장
            plt.tight_layout()
            file_name = f"record_{team_name}_vs_{opp_name}.png"
            plt.savefig(os.path.join(save_dir, file_name), bbox_inches='tight', dpi=100)
            plt.close()

    print("상대 전적 표(Record) 이미지 생성 성공")

# 팀 페이지 - 핵심 능력치 요약(도넛그래프)
def create_player_war_chart(player_data):
    """
    특정 선수의 oWAR, dWAR 비율을 파이 차트로 생성하여 저장합니다.
    파일명: war_chart_{PlayerID}.png
    """
    # 폰트 설정 (기존 코드와 동일)
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    else:
        plt.rcParams['font.family'] = 'sans-serif'
    
    # 1. 데이터 준비
    player_id = player_data['Id']
    war = player_data.get('WAR', 0)
    owar = player_data.get('oWAR', 0)
    dwar = player_data.get('dWAR', 0)

    # 2. 저장 경로 설정
    save_dir = os.path.join('static', 'image', 'player_chart')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # 3. 데이터 전처리 (파이 차트용)
    # 음수가 있을 경우 시각화를 위해 절대값 사용, 둘 다 0이면 빈 차트 생성
    abs_owar = abs(owar)
    abs_dwar = abs(dwar)
    
    if abs_owar + abs_dwar == 0:
        # 데이터가 없거나 0일 경우 회색 원
        sizes = [1]
        colors = ['#e0e0e0']
        labels = ['']
    else:
        sizes = [abs_owar, abs_dwar]
        colors = ['#d9534f', '#5b7ece'] # 빨강(공격), 파랑(수비)
        labels = ['공격', '수비']

    # 4. 차트 그리기 (도넛 차트)
    fig, ax = plt.subplots(figsize=(3, 3))
    
    wedges, texts, autotexts = ax.pie(sizes, 
                                      labels=labels, 
                                      colors=colors, 
                                      autopct='', # 퍼센트 텍스트 제거 (직접 수치 입력)
                                      startangle=90, 
                                      pctdistance=0.85,
                                      wedgeprops=dict(width=0.4, edgecolor='w'))

    # 가운데 구멍에 총 WAR 표시
    ax.text(0, 0, f"총 기여도\n(WAR)\n{war}", ha='center', va='center', fontsize=11, fontweight='bold', color='#333')

    # 범례 및 수치 텍스트 추가 (그래프 밖이나 위에 표시)
    # 여기서는 간단하게 제목이나 캡션 대신 HTML에서 범례를 처리하도록 함
    
    # 레이아웃 정리 및 저장
    plt.tight_layout()
    file_name = f"war_chart_{player_id}.png"
    plt.savefig(os.path.join(save_dir, file_name), transparent=True)
    plt.close()

# 팀 페이지 - 공격 효율성(가로막대그래프)
def create_player_offensive_chart(player_data):
    """
    선수의 공격 효율성(wRC+, OPS, AVG, OBP, SLG)을 가로 막대 그래프로 생성합니다.
    단위가 다른 데이터를 시각화하기 위해 각 지표별 기준치 대비 비율로 막대 길이를 설정합니다.
    """
    # 폰트 설정 (기존 코드 사용)
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    else:
        plt.rcParams['font.family'] = 'sans-serif'

    # 1. 데이터 준비
    player_id = player_data['Id']
    
    # 시각화할 지표와 라벨 정의 (순서: 위에서부터)
    metrics = ['wRC+', 'OPS', 'SLG', 'OBP', 'AVG']
    labels = ['wRC+', 'OPS', '장타율', '출루율', '타율']
    
    # 각 지표의 "만점(그래프 꽉 차는 길이)" 기준 설정 (시각적 밸런스 조절용)
    # 예: 타율 0.4면 그래프 80% 채움, wRC+ 200이면 그래프 100% 채움
    max_limits = {
        'wRC+': 200, 
        'OPS': 1.2, 
        'SLG': 0.8, 
        'OBP': 0.6, 
        'AVG': 0.5
    }
    
    values = []
    ratios = [] # 그래프 그리기용 비율 (0~1)
    
    for m in metrics:
        val = player_data.get(m, 0)
        values.append(val)
        
        # 비율 계산 (값이 기준보다 크면 1.0으로 고정)
        limit = max_limits[m]
        ratio = val / limit if limit > 0 else 0
        ratios.append(min(ratio, 1.0))

    # 2. 저장 경로
    save_dir = os.path.join('static', 'image', 'player_chart')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 3. 그래프 그리기 (가로 막대)
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # y축 위치 설정 (위에서부터 그려지게 역순 정렬)
    y_pos = range(len(metrics))
    
    # 막대 그리기
    bars = ax.barh(y_pos, ratios, height=0.8, color=['#5b7ece', '#d9534f', '#888', '#888', '#888'])
    
    # 4. 스타일링
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1.1) # 텍스트 공간 확보를 위해 1.1까지
    ax.axis('off') # 테두리 및 눈금 제거 (깔끔하게)
    
    # y축 라벨만 다시 켬 (axis='off'로 다 사라졌으므로 수동 텍스트 배치)
    for i, label in enumerate(labels):
        ax.text(-0.02, i, label, ha='right', va='center', fontsize=14, fontweight='bold', color='#333')

    # 5. 막대 옆에 실제 수치 표시
    for i, (ratio, val) in enumerate(zip(ratios, values)):
        # wRC+는 정수, 나머지는 소수점 3자리
        if metrics[i] == 'wRC+':
            text_val = f"{val}"
        else:
            text_val = f"{val:.3f}"
            
        ax.text(ratio + 0.02, i, text_val, va='center', fontsize=12, fontweight='bold', color='#002561')

    # 6. 저장
    plt.tight_layout()
    file_name = f"offensive_chart_{player_id}.png"
    plt.savefig(os.path.join(save_dir, file_name), bbox_inches='tight', transparent=True)
    plt.close()

# 선수 페이지 - 타격 세부 기록
def create_player_detail_chart(player_data):
    """
    선수의 타격 세부 기록(H, R, RBI, HR, 2B, 3B, BB, SO)을 선 그래프로 생성합니다.
    """
    # 폰트 설정 (기존 코드 사용)
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    else:
        plt.rcParams['font.family'] = 'sans-serif'

    # 1. 데이터 준비
    player_id = player_data['Id']
    
    # 시각화할 지표와 라벨
    metrics = ['H', 'R', 'RBI', 'BB', 'SO', '2B', 'HR', '3B'] # 수치 크기순 정렬 추천
    labels = ['안타', '득점', '타점', '볼넷', '삼진', '2루타', '홈런', '3루타']
    
    values = []
    for m in metrics:
        values.append(player_data.get(m, 0))

    # 2. 저장 경로
    save_dir = os.path.join('static', 'image', 'player_chart')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 3. 그래프 그리기 (선 그래프)
    fig, ax = plt.subplots(figsize=(10, 4)) # 가로로 긴 형태
    
    # 선 그래프와 마커 그리기
    ax.plot(labels, values, marker='o', linestyle='-', linewidth=2, color='#002561', markersize=8)
    
    # 영역 채우기 (선 아래쪽을 연하게 채움)
    ax.fill_between(labels, values, color='#002561', alpha=0.1)

    # 4. 스타일링
    ax.grid(True, linestyle='--', alpha=0.5, axis='y') # Y축 그리드만 표시
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 데이터 값 표시 (텍스트)
    for i, v in enumerate(values):
        ax.text(i, v + (max(values)*0.05), str(v), ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Y축 범위 여유 있게 설정 (텍스트 잘림 방지)
    plt.ylim(0, max(values) * 1.2)

    # 5. 저장
    plt.tight_layout()
    file_name = f"detail_chart_{player_id}.png"
    plt.savefig(os.path.join(save_dir, file_name), bbox_inches='tight', transparent=True)
    plt.close()

# 팀 페이지 - 홈구장 지도 생성
import folium # 상단에 추가

# ... (기존 코드들) ...

def create_stadium_map(team_name, lat, lon, stadium_name):
    """
    위도, 경도 정보를 받아 Folium 지도를 생성하고 HTML 파일로 저장합니다.
    저장 경로: static/maps/map_{team_name}.html
    """
    # 1. 저장 경로 확인
    save_dir = os.path.join('static', 'maps')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # 2. 지도 생성 (초기 위치 및 줌 레벨 설정)
    m = folium.Map(location=[lat, lon], zoom_start=16)

    # 3. 마커 추가 (클릭 시 구장 이름 표시)
    folium.Marker(
        location=[lat, lon],
        popup=stadium_name,
        tooltip=team_name,
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

    # 4. HTML 파일로 저장
    save_path = os.path.join(save_dir, f'map_{team_name}.html')
    m.save(save_path)
    # print(f"{team_name} 홈구장 지도 생성 완료")

# 팀 페이지 - 득/실점 그래프
# modules/visualizer.py 하단 추가

def create_team_runs_chart(team_name, team_data):
    """
    팀의 경기당 득점(R/G)과 실점(-R/G)을 비교하는 세로 막대 그래프를 생성합니다.
    (토스 스타일: 두 개의 막대 비교)
    """
    # 폰트 설정 (기존 코드 사용)
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    else:
        plt.rcParams['font.family'] = 'sans-serif'

    # 1. 데이터 준비
    # team_data는 리스트 안에 딕셔너리가 있는 형태이므로 첫 번째 요소 사용
    data = team_data if isinstance(team_data, dict) else team_data[0]
    
    runs_scored = data.get('R/G', 0)
    runs_allowed = data.get('-R/G', 0)
    
    values = [runs_scored, runs_allowed]
    labels = ['평균 득점', '평균 실점']
    colors = ['#5b7ece', '#ccc'] # 득점: 파랑(강조), 실점: 회색(비교)

    # 2. 저장 경로
    save_dir = os.path.join('static', 'image', 'team_chart') # 팀별 차트 폴더
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 3. 그래프 그리기 (세로 막대)
    fig, ax = plt.subplots(figsize=(5, 6)) # 세로로 긴 형태
    
    bars = ax.bar(labels, values, color=colors, width=0.5)
    
    # 4. 스타일링 (토스 스타일)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False) # 왼쪽 축도 숨김
    ax.get_yaxis().set_visible(False)    # Y축 눈금 숨김
    
    # X축 라벨 스타일
    ax.tick_params(axis='x', length=0, labelsize=12, labelcolor='#333', pad=10)

    # 막대 위에 값 표시 (크고 진하게)
    for bar, v in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.1, 
                f"{v}", 
                ha='center', va='bottom', 
                fontsize=16, fontweight='bold', 
                color=bar.get_facecolor())

    # 득실 마진 표시 (가운데)
    margin = runs_scored - runs_allowed
    margin_text = f"+{margin:.2f}" if margin > 0 else f"{margin:.2f}"
    margin_color = '#d9534f' if margin < 0 else '#5b7ece' # 마이너스면 빨강, 플러스면 파랑
    
    # 제목 대신 그래프 상단에 마진 표시
    plt.title(f"득실 마진: {margin_text}", fontsize=14, color=margin_color, fontweight='bold', pad=20)

    # 5. 저장
    plt.tight_layout()
    file_name = f"runs_chart_{team_name}.png"
    plt.savefig(os.path.join(save_dir, file_name), bbox_inches='tight', transparent=True)
    plt.close()

# 팀 페이지 - 기대 승률
def create_pythagorean_chart(team_name, team_data):
    """
    팀의 기대 승률(피타고리안 승률)과 실제 승률을 비교하는 그래프를 생성합니다.
    공식: R^1.83 / (R^1.83 + RA^1.83)
    """
    # 폰트 설정 (기존 코드 사용)
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    else:
        plt.rcParams['font.family'] = 'sans-serif'

    # 1. 데이터 준비
    data = team_data if isinstance(team_data, dict) else team_data[0]
    
    R = data.get('R', 0)      # 총 득점
    RA = data.get('-R', 0)    # 총 실점 (Runs Allowed)
    actual_pct = data.get('PCT', 0) # 실제 승률

    # 피타고리안 승률 계산 (지수 1.83 사용)
    if (R + RA) == 0:
        expected_pct = 0
    else:
        expected_pct = (R ** 1.83) / ((R ** 1.83) + (RA ** 1.83))

    # 2. 저장 경로
    save_dir = os.path.join('static', 'image', 'team_chart')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 3. 그래프 그리기 (가로 막대 비교)
    fig, ax = plt.subplots(figsize=(6, 3)) # 높이를 낮게 설정
    
    # 데이터
    labels = ['기대 승률', '실제 승률']
    values = [expected_pct, actual_pct]
    colors = ['#aaa', '#a50034'] # 기대(회색), 실제(팀컬러/붉은색)

    y_pos = range(len(labels))
    bars = ax.barh(y_pos, values, height=0.5, color=colors)

    # 4. 스타일링
    ax.set_xlim(0, 1.0) # 승률은 0~1 사이
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.get_xaxis().set_visible(False) # X축 눈금 숨김

    # 수치 텍스트 표시
    for bar, v in zip(bars, values):
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, 
                f"{v:.3f}", 
                va='center', fontsize=12, fontweight='bold', color='#333')

    # 운/불운 분석 텍스트 추가 (그래프 제목 대신 하단 코멘트용 데이터 반환 고려)
    diff = actual_pct - expected_pct
    
    # 5. 저장
    plt.tight_layout()
    file_name = f"pythagorean_{team_name}.png"
    plt.savefig(os.path.join(save_dir, file_name), bbox_inches='tight', transparent=True)
    plt.close()

    # 분석 결과 텍스트 반환 (HTML에서 쓰기 위해)
    if diff > 0.02:
        analysis = "운이 매우 좋음 (접전 승리 다수)"
        desc = "실력보다 더 좋은 성적을 거뒀습니다. 불펜이 강하거나 운이 따랐을 가능성이 높습니다."
    elif diff > 0:
        analysis = "약간의 행운"
        desc = "기대치보다 조금 더 많이 이겼습니다."
    elif diff > -0.02:
        analysis = "정직한 성적"
        desc = "득실점 능력만큼 딱 그만큼의 성적을 거뒀습니다."
    else:
        analysis = "불운 (성적 반등 가능성)"
        desc = "전력에 비해 승리를 챙기지 못했습니다. 다음 시즌엔 성적이 오를 가능성이 큽니다."

    return expected_pct, analysis, desc

# 선수-선수 페이지
# 이중 막대그래프
def create_player_comparison_chart(p1_data, p2_data):
    """
    두 선수의 주요 스탯(AVG, HR, RBI, SB, H)을 비교하는 이중 막대 그래프 생성
    """
    # 폰트 설정 (기존 코드 사용)
    font_path = None
    font_candidates = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_candidates:
        if 'Nanum' in font or 'Gothic' in font or 'Malgun' in font:
            font_path = font
            break
    if font_path:
        fe = fm.FontEntry(fname=font_path, name='KoreanFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = 'KoreanFont'
    else:
        plt.rcParams['font.family'] = 'sans-serif'

    # 데이터 준비
    metrics = ['AVG', 'HR', 'RBI', 'SB', 'H']
    labels = ['타율', '홈런', '타점', '도루', '안타']
    
    p1_vals = [p1_data.get(m, 0) for m in metrics]
    p2_vals = [p2_data.get(m, 0) for m in metrics]
    
    
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width/2, p1_vals, width, label=p1_data['Name'], color='#002561')
    rects2 = ax.bar(x + width/2, p2_vals, width, label=p2_data['Name'], color='#a50034')

    def autolabel(rects, is_float=False):
        for i, rect in enumerate(rects):
            height = rect.get_height()
            val = p1_vals[i] if rects == rects1 else p2_vals[i]
            if i == 0: # 타율
                txt = f"{val:.3f}"
            else:
                txt = f"{int(val)}"
            ax.annotate(txt,
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), 
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold')

    autolabel(rects1)
    autolabel(rects2)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight='bold')
    ax.legend()
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.get_yaxis().set_visible(False)

    plt.tight_layout()
    
    save_dir = os.path.join('static', 'image', 'comparison')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    file_name = f"compare_{p1_data['Id']}_vs_{p2_data['Id']}.png"
    plt.savefig(os.path.join(save_dir, file_name), transparent=True)
    plt.close()
    
    return file_name