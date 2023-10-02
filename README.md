# <span id='top'> 🐳 Dockerized 한끼얼마💰</span>

## 1. 🥙 한끼얼마 💰

![main](https://github.com/seungwonbased/ssg-recipe-project/blob/main/main_page.png)

> [📝 GitHub Repository & Report](https://github.com/seungwonbased/ssg-recipe-project)

## 2. 🐳 Dockerized 한끼얼마 아키텍처

![archi](https://github.com/seungwonbased/dockerized-recipe-book/blob/main/assets/architecture.png)

> [🐋 Docker Hub: seungwonbae](https://hub.docker.com/u/seungwonbae)

### 2.1. Images

#### 2.1.1. seungwonbae/recipe-book-was

```dockerfile
# Dockerfile
FROM ubuntu:20.04

WORKDIR /recipe-book

COPY . .

RUN apt-get update -y
RUN apt-get install -y python3
RUN apt install -y python3-pip
RUN pip install wheel
RUN pip install -r requirements.txt

ENV FLASK_APP=app
ENV FLASK_DEBUG=true
ENV APP_CONFIG_FILE=/recipe-book/config/docker.py

RUN chmod +x app.sh

CMD [ "./app.sh" ]
```

```bash
# app.sh
flask db init
flask db migrate
flask db upgrade

gunicorn --bind 0.0.0.0:5000 --timeout 90 "app:create_app()"
```

- Flask + Gunicorn (WSGI)로 구성된 웹 애플리케이션 서버
- Ubuntu 20.04 베이스
- 빌드 시 필요한 패키지와 의존 관계 설치
- 실행 시 app.sh 스크립트 실행
- app.sh 스크립트를 통해 데이터베이스를 설정하고, WAS를 실행
- 이전에 Lightsail에 배포했을 땐 Unix Socket을 통해 웹 서버와 통신했는데, 도커화 후에는 포트에 바인딩해 서비스
  - Unix Socket은 같은 로컬 머신 안에서 빠르고 효울적으로 통신이 가능하지만, 본 프로젝트에서는 웹 서버와 WAS를 다른 컨테이너에 격리했기 때문에 포트로 서비스해야 함

```python
# docker.py
from config.default import *
from dotenv import load_dotenv
import os


load_dotenv(os.path.join(BASE_DIR, '.env'))


SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
    user=os.getenv('DB_USER'),
    pw=os.getenv('DB_PASSWORD'),
    url=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    db=os.getenv('DB_NAME'))


SQLALCHEMY_TRACK_MODIFICATIONS = False
```

- 위와 같은 애플리케이션의 config/docker.py를 작성해 Docker 환경에서 설정을 자동화

#### 2.1.2. seungwonbae/recipe-book-postgres

```dockerfile
# Dockerfile
FROM postgres:15.4

ENV LANG C.UTF-8
ENV DB_USER=postgres
ENV DB_PASSWORD=password
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=recipe

COPY ./data /var/lib/postgresql/data
```

- PostgreSQL 데이터베이스 서버
- Dockerfile에서 기본 환경 변수를 설정
- 빌드 시 기본 데이터베이스 데이터를 COPY

#### 2.1.3. seungwonbae/recipe-book-ws

```dockerfile
# Dockerfile
FROM nginx

COPY nginx.conf /etc/nginx/nginx.conf
```

```.conf
# nginx.conf
events {
    worker_connections 1000;
}

http {
    upstream was {
        server recipe-book-was:5000;
    }

    server {
        listen 80;

        location / {
            proxy_set_header Connection "";
            proxy_pass http://was/;
        }
    }
}
```

- Nginx 웹 서버
- 빌드 시 Nginx 설정 파일을 COPY
- 설정 파일에서 proxy_pass를 통해 스트림되는 요청을 라운드 로빈으로 부하 분산

### 2.2. Docker Compose

```yaml
# docker-compose.yaml
version: "3.3"

services:
  recipe-book-postgres:
    image: seungwonbae/recipe-book-postgres
    container_name: postgres
    volumes:
      - postgres:/var/lib/postgresql/data
    expose:
      - "5432"
    environment:
      - POSTGRES_PASSWORD=password
    networks:
      - net
  recipe-book-was:
    depends_on:
      - recipe-book-postgres
    image: seungwonbae/recipe-book-was
    expose:
      - "5000"
    networks:
      - net
  recipe-book-ws:
    depends_on:
      - recipe-book-was
    image: seungwonbae/recipe-book-ws
    container_name: ws
    restart: always
    ports:
      - "80:80"
    networks:
      - net
volumes:
  postgres: {}
networks:
  net:
    driver: bridge
```

- docker-compose 파일에 세 개의 서비스 등록
  - DB: recipe-book-postgres
  - WAS: recipe-book-was
  - Web Server: recipe-book-ws
- DB에 볼륨을 설정해 재시작하더라도 데이터가 유지됨
- 웹 서버만 호스트와 포트를 매핑해 나머지는 백엔드에서 구동되도록 함
  - 웹 서버를 통해서만 서비스 접근 가능
- 웹 서버가 죽으면 다시 재시작하도록 설정
- Compose default 네트워크를 사용해도 되지만, net 네트워크를 생성해 네트워크 구성을 명확하게 함

## 3. ⚖️ Load Balancing Test

> [🔗 Youtube Link](https://youtu.be/zIxFwh1l9sU?si=3PlfnwQGynnu5xYx)

- 세 개의 WAS 컨테이너에 라운드 로빈으로 부하 분산이 되는 것을 확인

## 4. 🔧 Issue & Troubleshooting

> ✅: 해결 이슈 ❓: 미해결 이슈

### 4.1. WAS 초기 설정 자동화

- WAS 컨테이너를 띄울 때 CMD 명령을 통해 Flask 애플리케이션을 실행
- 이 때, DB 설정을 docker exec -it was /bin/bash 명령을 통해 직접 붙어서 수동으로 해줘야 함

> ✅ 해결: 초기 설정 쉘 스크립트를 작성하고, 컨테이너 실행 시 CMD 명령이 이를 수행하도록 함

### 4.2. 배포해보니 애플리케이션 기능이 말도 안되게 느려짐

- 애플리케이션이 동작은 하나, 기능, 즉 로그인이나 글쓰기 처리가 매우 느림
- 로그를 확인해보니 WAS에서 Timeout 에러가 계속 나고 있었음

> ✅ 해결: 로그를 확인해보니 Timeout 속도가 너무 짧았던 것이 문제여서 WAS를 띄울 때 --timeout=90으로 설정

### 4.3. 데이터베이스 초기 생성 자동화

- 처음에는 PostgreSQL의 기본 이미지로 컨테이너를 띄움
- 이 때, 초기 DB 생성을 docker exec -it postgres /bin/bash 명령을 통해 직접 붙어서 수동으로 해줘야 함

> ✅ 해결: 초기 설정을 마친 DB 데이터를 로컬 머신에 저장해두고 이미지 빌드 시 해당 데이터를 COPY하도록 함, 이후에는 Named Volume에 저장된 해당 데이터를 읽기 때문에 자동으로 설정됨

### 4.4. 웹 서버의 Static 리소스 서빙 불가

- 웹 서버에서 정적 리소스를 서빙하도록 하고 싶어 location /static 설정을 해봤지만 정적 리소스 불러오기 불가능

> ❓미해결: 애플리케이션의 Static 경로를 웹 서버에서 읽어들일 수 있도록 설정해봐야겠음

### 4.5. Docker Compose Scaling이 되지 않음

- 스케일링을 하지 않고 docker compose up을 했을 때는 애플리케이션이 정상적으로 실행됨
- --scale 옵션을 통해 WAS를 스케일링하면 WAS가 종료됨

> ✅ 해결: docker-compose 파일에서 recipe-book-was의 container_name을 명시적으로 준 것이 문제, 스케일링을 하려면 Docker가 컨테이너 이름을 관리하도록 해야 함
