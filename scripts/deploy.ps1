Set-Location "$(Get-Location)\..";
docker build --tag python-docker .;
docker run -d -p 5000:5000  $( docker images --format "{{.Repository}}:{{.Tag}}" | Select-Object -First 1) 