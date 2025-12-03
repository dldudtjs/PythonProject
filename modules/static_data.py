import json
import os

#메인페이미 팀 순위 변동
def get_2025_season_data():
    return {
        "labels": ["3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월"],
        "teams_data": {
            'LG':   [1, 1, 1, 2, 2, 1, 1, 1],
            '한화': [7, 3, 2, 1, 1, 2, 2, 2],
            'SSG':  [2, 7, 6, 5, 4, 3, 3, 3],
            '삼성': [2, 2, 5, 7, 7, 5, 4, 4],
            'NC':   [6, 9, 8, 8, 8, 7, 5, 5],
            'KT':   [4, 5, 4, 6, 5, 6, 6, 6],
            '롯데': [9, 4, 3, 3, 3, 4, 7, 7],
            'KIA':  [7, 6, 7, 4, 6, 8, 8, 8],
            '두산': [10, 8, 9, 9, 9, 9, 9, 9],
            '키움': [5, 10, 10, 10, 10, 10, 10, 10]
        }
    }

#메인페이지 팀랭크
def get_team_rank_data_from_json():
    """
    static/data/kbo_team_data.json 파일을 읽어서
    순위표에 필요한 정보(Rank, W, L, D, PCT)만 추출하여 반환합니다.
    """
    # 1. JSON 파일의 절대 경로 찾기
    # 현재 실행 중인 파일(app.py가 있는 루트) 기준 static/data 폴더 안을 찾습니다.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # modules 상위 폴더(루트)
    file_path = os.path.join(base_dir, 'static', 'data', 'kbo_team_data.json')

    ranking_list = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. 데이터 파싱 및 필터링
        for team_name, stats_list in data.items():
            # JSON 구조가 "팀명": [ {정보} ] 형태이므로 리스트의 첫 번째 요소 접근
            if stats_list:
                stat = stats_list[0]
                ranking_list.append({
                    'name': team_name,
                    'rank': stat.get('Rank'),
                    'w': stat.get('W'),
                    'l': stat.get('L'),
                    'd': stat.get('D'),
                    'pct': stat.get('PCT')
                })
        
        # 3. 순위(Rank) 기준으로 오름차순 정렬 (1위 -> 10위)
        ranking_list.sort(key=lambda x: x['rank'])

    except FileNotFoundError:
        print(f"오류: {file_path} 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
        return []

    return ranking_list

# 팀페이지
def get_specific_team_data(team_name):
    """
    팀 이름(예: 'LG', 'Samsung')을 받아서 해당 팀의 상세 정보를 반환합니다.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'static', 'data', 'kbo_team_data.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # team_name에 해당하는 데이터가 있는지 확인
        if team_name in data:
            # JSON 구조가 "LG": [{정보}] 형태이므로 리스트의 첫 번째 요소([0]) 반환
            return data[team_name][0]
        else:
            return None # 해당 팀 이름이 없을 경우
            
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        return None

# 팀페이지 - 팀 강점/약점 분석 (WAA 레이더 차트-오각형 그래프)
def get_all_team_data():
    """
    모든 팀의 상세 데이터를 반환합니다. (레이더 차트 정규화용)
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'static', 'data', 'kbo_team_data.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        return {}
    
# 팀페이지 - 팀별 대결 기록
def get_comparison_data():
    """
    kbo_team_comparison.json 파일을 읽어서 반환합니다.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'static', 'data', 'kbo_team_comparison.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"상대 전적 데이터 로드 실패: {e}")
        return {}
    
# 팀페이지 - 선수리스트
def get_players_by_team(team_name):
    """
    kbo_player_data.json에서 특정 팀의 선수를 가져와 
    WAR(승리 기여도) 내림차순으로 정렬하여 반환
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'static', 'data', 'kbo_player_data.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if team_name in data:
            players = data[team_name]
            
            # ★ 수정된 부분: WAR 기준으로 내림차순 정렬
            # 데이터가 없거나 문자열일 경우를 대비해 float 변환 및 기본값(-99) 처리
            sorted_players = sorted(
                players, 
                key=lambda x: float(x.get('WAR', -99)), 
                reverse=True
            )
            return sorted_players
        else:
            return []
    except Exception as e:
        print(f"선수 데이터 로드 오류: {e}")
        return []
    

# 선수 페이지
def get_player_by_id(player_id):
    """
    전체 팀 데이터를 뒤져서 player_id와 일치하는 선수 1명의 정보를 반환합니다.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'static', 'data', 'kbo_player_data.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 모든 팀(key)을 순회하며 선수 리스트(value) 탐색
        for team_name, players in data.items():
            for p in players:
                if p['Id'] == player_id:
                    return p # 선수를 찾으면 바로 반환
                    
        return None # 끝까지 못 찾으면 None 반환
            
    except Exception as e:
        print(f"선수 상세 정보 로드 실패: {e}")
        return None
    
# 선수 페이지 - 팀 심볼 불러오기
def get_team_symbol(team_name):
    """
    팀 이름(예: 'LG')을 입력받아 해당 팀의 심볼 이미지 경로를 반환합니다.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'static', 'data', 'kbo_team_data.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if team_name in data:
            # 팀 데이터의 첫 번째 요소에서 Symbol 키를 찾음
            return data[team_name][0].get('Symbol', '')
        return ''
            
    except Exception as e:
        print(f"팀 심볼 로드 실패: {e}")
        return ''