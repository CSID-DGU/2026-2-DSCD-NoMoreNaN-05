# TRUEAD 데이터베이스 이전 및 임베딩 검색 준비

## 목적
광고 Claim과 의미가 관련된 Evidence를 검색하기 위해 PostgreSQL과 pgvector를 도입한다.
벡터 검색은 근거 후보를 찾는 단계이며 Claim의 참·거짓 판정은 별도로 수행한다.

## 완료한 과정
1. 로컬 Windows에 PostgreSQL 18.6 설치 및 pgAdmin 접속.
2. `TrueAD_Evidence_Claim` 데이터베이스 생성.
3. Python의 psycopg 드라이버와 `.env` 접속 설정으로 연결 확인.
4. SQLite 두 개의 데이터·키·관계·인덱스·뷰를 PostgreSQL로 이전.
5. 테이블별 건수와 전체 컬럼 값 비교 검증. 원본 SQLite 보존.
6. Windows C++ 빌드 도구와 SDK로 pgvector 0.8.7 설치.
7. 해당 DB에서 `CREATE EXTENSION vector`로 활성화.
8. 예제 숫자 벡터로 코사인 유사도 검색 기능 확인.

## 저장 구조
| PostgreSQL 스키마 | 데이터 | 주요 건수 |
|---|---|---|
| claim_verification | 제품·원료·질병·공식 Evidence | 제품 46,165 / 원료 1,223 / 질병 34,861 / Evidence 3,082 |
| kipris | 특허 보조 근거 후보 및 검색·원본 출처 | 특허·실용신안 12,572 / XML 페이지 26 |

claims와 claim_evidence_links는 이전 시 0건이었다.
특허는 효능 입증이나 식약처 인정과 구분되는 보조 근거 후보다.

## 각 도구의 역할
| 도구 | 역할 |
|---|---|
| VS Code + Python | 데이터 처리, 임베딩 모델 실행, DB 저장·검색 |
| PostgreSQL | 구조화 데이터와 벡터 저장 |
| pgvector | 벡터 자료형 및 거리·유사도 검색 |
| pgAdmin | DB 테이블 확인 및 SQL 실행 |
| 임베딩 모델 | 텍스트를 숫자 벡터로 변환 |

## 이번에 준비한 로컬 임베딩 설정
`configs/embedding.yaml`에 `intfloat/multilingual-e5-small` 사용 설정을 기록했다.
CPU 실행, 384차원, 벡터 정규화, 코사인 유사도 기준이다.
Claim에는 `query: `, 근거에는 `passage: ` 접두어를 사용하는 모델 규칙을 따른다.
장문은 모델 입력 한도를 고려해 청크 정책을 정한 뒤 처리한다.
모델 revision은 아직 미고정이며, 실제 벡터 저장 전에 커밋을 고정해야 한다.

현재는 설정 파일과 선택 설치용 requirements-embedding.txt만 추가했다.
모델 다운로드·패키지 설치·텍스트 임베딩 생성·벡터 테이블 생성·의미 검색 연결은 실행하지 않았다.
기존 프로그램이 이 설정을 자동으로 읽도록 연결된 상태도 아니다.
모델 호출료는 없지만 컴퓨터·서버 연산 자원을 사용한다.
한국어 건강정보 검색 성능은 작은 평가 데이터로 먼저 검증해야 한다.

## 예정된 동작
근거 텍스트 → 임베딩 생성 → 출처·모델 버전·차원·텍스트 해시와 함께 저장.
광고 Claim → 같은 모델로 임베딩 → 유사한 근거 검색 → 근거 검토·판정.
변경되지 않은 근거의 벡터는 재사용하고 추가·수정된 근거만 갱신한다.
유사도는 근거 관련성을 나타내며 사실 여부의 확률이 아니다.

## 서버 이전
로컬 개발·테스트 후 코드와 모델 설정을 서버로 옮긴다.
서버에 같은 모델 revision과 전처리를 적용하고 PostgreSQL·pgvector를 준비한다.
임베딩이 포함된 PostgreSQL 백업을 복원하면 기존 벡터를 다시 계산할 필요는 없다.
서버의 설치·복원 완료 상태는 별도 확인해야 한다.
기존 수집·검색 코드의 PostgreSQL 전환도 별도 작업이다.

모델 원본 안내: https://huggingface.co/intfloat/multilingual-e5-small
