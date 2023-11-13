cd "$(pwd)/.." &
docker build --tag python-docker . &
docker run -d -p 5000:5000 $(docker images | head -2 | tail -1 | cut -d " " -f 1)