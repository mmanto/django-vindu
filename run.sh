#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
source ./utils/bask.sh

task_default() {
  bask_list_tasks
}

task_makemigrations() {
  docker-compose run --rm web ./manage.py makemigrations
}

task_docker_build() {
  cp vindu/local_settings.py.docker vindu/local_settings.py
  docker-compose build
}

task_docker_rebuild() {
  docker-compose down
  cp vindu/local_settings.py.docker vindu/local_settings.py
  docker-compose build
}

task_docker_rebuild_db() {
  docker-compose down
  docker-compose build --force-rm --no-cache db
}

task_docker_up() {
  cp vindu/local_settings.py.docker vindu/local_settings.py
  docker-compose up
}

task_docker_migrate() {
  docker-compose run --rm web ./manage.py migrate
}

task_docker_initdb() {
  bask_log_info "Running migrate"
  docker-compose run --rm web ./manage.py migrate
  #bask_log_info "Running loaddata"
}

task_docker_debug_app() {
  docker-compose stop web
  docker-compose run --rm --service-ports web python manage.py runserver 0.0.0.0:8000
}

task_dbshell() {
   PGPASSWORD="anting2018" psql -h localhost -p 7432 -U vindu_postgres vindu_postgres
}

task_shell() {
  docker-compose run --rm web ./manage.py shell
}
