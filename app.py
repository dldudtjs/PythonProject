# [Main] Flask 실행 파일 (라우팅 정의)
# 파일 위치: app.py

from flask import Flask, render_template, jsonify, request, send_file
from modules import visualizer, static_data

app = Flask(__name__)

# 앱 시작 시 그래프 및 표 이미지 생성
visualizer.create_ranking_graph()
visualizer.create_team_radar_charts()
visualizer.create_waa_table_images()
visualizer.create_match_record_images()

# 1. 메인 페이지
@app.route('/')
def index():
    ranking_list = static_data.get_team_rank_data_from_json()
    return render_template('index.html', ranking_list=ranking_list)

# 2. 팀 비교 분석 페이지 (팀 대 팀)
@app.route('/analysis')
def analysis():
    ranking_list = static_data.get_team_rank_data_from_json()
    team_names = [team['name'] for team in ranking_list]
    return render_template('analysis.html', team_names=team_names)

# 3. 선수 대 선수 비교 페이지 (화면 표시)
@app.route('/player_compare')
def player_compare_page(): # 함수 이름 변경 (중복 방지)
    team_list = static_data.get_team_rank_data_from_json()
    team_names = [team['name'] for team in team_list]
    return render_template('player_compare.html', team_names=team_names)

# 4. 팀 상세 페이지
@app.route('/team/<team_name>')
def team_detail(team_name):
    team_data = static_data.get_specific_team_data(team_name)
    player_list = static_data.get_players_by_team(team_name)
    
    pyth_result = None 

    if team_data:
        lat = team_data.get('Latitude')
        lon = team_data.get('Longitude')
        stadium = team_data.get('Stadium', '홈구장')
        if lat and lon:
            visualizer.create_stadium_map(team_name, lat, lon, stadium)
            
        # 득점/실점 그래프
        visualizer.create_team_runs_chart(team_name, team_data)

        # 피타고리안 승률 그래프
        pyth_result = visualizer.create_pythagorean_chart(team_name, team_data)
        
        return render_template('team_detail.html', 
                               team=team_data, 
                               team_name=team_name, 
                               players=player_list,
                               pyth_data=pyth_result)
    else:
        return "팀 데이터를 찾을 수 없습니다.", 404

# 5. 선수 상세 페이지 (개인 프로필)
@app.route('/player/<int:player_id>')
def player_detail(player_id):
    player_data = static_data.get_player_by_id(player_id)
    
    if player_data:
        team_symbol = static_data.get_team_symbol(player_data['Team'])
        
        # 그래프 3종 생성
        visualizer.create_player_war_chart(player_data)
        visualizer.create_player_offensive_chart(player_data)
        visualizer.create_player_detail_chart(player_data)
        
        return render_template('player_detail.html', 
                               player=player_data, 
                               team_symbol=team_symbol)
    else:
        return "선수 정보를 찾을 수 없습니다.", 404

# --- API (자바스크립트 비동기 요청 처리용) ---

# [API] 특정 팀의 선수 목록 반환
@app.route('/api/players/<team_name>')
def get_players_json(team_name):
    players = static_data.get_players_by_team(team_name)
    player_simple_list = [{'Id': p['Id'], 'Name': p['Name'], 'Pos': p['Pos.']} for p in players]
    return jsonify(player_simple_list)

# [API] 특정 선수의 상세 정보 반환
@app.route('/api/player/<int:player_id>')
def get_player_detail_json(player_id):
    player = static_data.get_player_by_id(player_id)
    if player:
        team_symbol = static_data.get_team_symbol(player['Team'])
        player['TeamSymbol'] = team_symbol
        return jsonify(player)
    return jsonify({'error': 'Not found'}), 404

# [API] 선수 비교 그래프 이미지 반환
@app.route('/plot/compare/<int:p1_id>/<int:p2_id>')
def plot_comparison(p1_id, p2_id):
    p1 = static_data.get_player_by_id(p1_id)
    p2 = static_data.get_player_by_id(p2_id)
    
    if p1 and p2:
        filename = visualizer.create_player_comparison_chart(p1, p2)
        return send_file(f'static/image/comparison/{filename}', mimetype='image/png')
    else:
        return "Error", 404

if __name__ == '__main__':
    app.run(debug=True)