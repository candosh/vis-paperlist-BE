# IEEE VIS: IEEE Visualization Conference
# 2009, 2019 ~ 2023 데이터 수집 완료 : 2024.03.04 - 최서현

import requests
import json
import os
from collections import defaultdict
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키와 기본 URL 설정
api_key = os.getenv("IEEE_API_KEY")
base_url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

# 결과 저장 디렉토리 설정 및 생성
save_dir = 'Result'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 결과 카운터 초기화
received_counts = defaultdict(int)
saved_counts = defaultdict(int)

def save_data(year, papers):
    global received_counts, saved_counts

    # 받아온 문서의 총 수 업데이트
    received_counts[year] += len(papers)

    formatted_papers = []
    for paper in papers:
        authors = [author['full_name'] for author in paper.get('authors', {}).get('authors', [])]
        formatted_paper = {
            "title": paper.get("title", ""),
            "conferenceTitle": paper.get("publication_title", ""),
            "date": paper.get("publication_date", ""),
            "authors": authors,
            "DOI": paper.get("doi", ""),
            "citation": paper.get("citing_paper_count", 0),
            "abstract": paper.get("abstract", ""),
        }
        formatted_papers.append(formatted_paper)

    saved_counts[year] += len(formatted_papers)

    # 연도별 파일에 저장
    filename = f'IEEE_VIS_{year}.json'
    file_path = os.path.join(save_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_papers, f, ensure_ascii=False, indent=4)
    
    print(f"Data saved to {file_path}")

# 연도별 publication_title 값
# 2023 ~ 2022 : IEEE Visualization and Visual Analytics
# 2021 ~ 2020 : 연도 IEEE Visualization Conference (VIS)
# 2009 : 2009 Second International Conference in Visualisation
# 2008 : 2008 International Conference Visualisation

def fetch_and_save_data(year):
    accumulated_papers = []
    search_params = {
        "publication_title": "IEEE Visualization and Visual Analytics",
        "start_year": year,
        "end_year": year,
        "apikey": api_key,
        "start_record": 1,
        "max_records": 200
    }
    
    while True:
        response = requests.get(base_url, params=search_params)
        if response.status_code == 200:
            data = response.json()
            papers = data.get('articles', [])
            accumulated_papers.extend(papers)
            
            # 현재 페이지의 문서 수가 max_records 미만이면, 더 이상 가져올 데이터X
            if len(papers) < search_params["max_records"]:
                break 
            
            search_params["start_record"] += len(papers)  
        else:
            print(f"Error in {year}: {response.status_code}")
            print(response.text)
            break
    
    # 한 연도의 모든 데이터를 한 번에 파일에 저장
    if accumulated_papers:
        save_data(year, accumulated_papers)
    else:
        print(f"No data found for year {year}")

# 연도별로 API 호출 및 데이터 저장 후, 카운터 출력
for year in range(2022, 2024):
    fetch_and_save_data(year)

# 최종 카운터 출력 : 갯수 확인 시 사용
for year in range(2022, 2024):
    print(f"Year {year}: Received {received_counts[year]}, Saved {saved_counts[year]}")