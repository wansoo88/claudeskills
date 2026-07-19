# AWS 3-tier 아키텍처 패턴 (참조)

> 근거: AWS 공식 3-tier 레퍼런스(aws-samples/aws-three-tier-web-architecture-workshop). 웹/WAS/DB 분리 표준.

## 기본 3-tier 구성
| 티어 | 역할 | 대표 구성(AWS) |
|---|---|---|
| **Web (표현)** | 정적 자산·SPA 서빙, 진입점 | CloudFront + S3 (React SPA) / 또는 ALB + Nginx |
| **App (WAS/로직)** | API·비즈니스 로직 | ECS Fargate(Docker) / EKS / EC2 + ALB |
| **Data (DB)** | 영속 데이터 | RDS(PostgreSQL/MySQL) Multi-AZ / Aurora |

## 네트워크 원칙
- **퍼블릭 서브넷**: ALB, NAT Gateway만. 인터넷 노출 최소.
- **프라이빗 서브넷**: App, DB. 인터넷 직접 접근 불가.
- 보안그룹: ALB→App→DB 방향으로만 포트 허용(최소 권한).
- DB는 **절대 퍼블릭 금지**. 접근은 App 티어 경유.

## 규모별 조정
| 규모 | 조정 |
|---|---|
| 소규모(팀 내, ~수만) | 단일 컨테이너/작은 RDS, Multi-AZ 선택적. 비용 우선. |
| 중규모(수십만~수백만) | ECS + Auto Scaling, RDS Multi-AZ, 읽기 복제본 검토. |
| 대규모(수천만+) | EKS/ECS 오토스케일, Aurora, 캐시(ElastiCache), CDN 적극. |

## 데이터 특성별 추가
- **실시간/스트림**: Kinesis/SQS + 소비자(consumer). 배치면 EventBridge + 스케줄.
- **대용량 분석**: S3(데이터레이크) + Athena/Redshift 분리.
- **ML 모델**: 추론 엔드포인트(SageMaker) 또는 컨테이너 분리.

## 보안·운영 기본
- 비밀정보: **Secrets Manager / Parameter Store** (코드·이미지에 금지).
- 관측: **CloudWatch**(로그/지표/알람) — App 티어에서 구조적 로그 방출.
- 전송 암호화(HTTPS/TLS), 저장 암호화(RDS/S3 KMS).
- IAM 최소 권한, 태깅으로 비용 추적.

## draw.io 표현 팁
- 티어를 점선 컨테이너로 묶고 화살표로 트래픽 흐름 표시.
- 무료·텍스트 기반이라 git 버전관리·리뷰 용이. Confluence draw.io 앱으로 임베드.
