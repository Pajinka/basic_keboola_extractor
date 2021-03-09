echo "Preparing KBC test image"
# set env vars
$KBC_DEVELOPERPORTAL_USERNAME  = ${jmeno_kbc}
$KBC_DEVELOPERPORTAL_PASSWORD  = ${heslo_kbc}
$KBC_DEVELOPERPORTAL_VENDOR = 'datasentics'
$KBC_DEVELOPERPORTAL_APP = 'datasentics.ex-ex-demo'
$BASE_KBC_CONFIG = '455568423'
$KBC_STORAGE_TOKEN = ${token} 'Input your storage token'


#build app
$APP_IMAGE='keboola-comp-test'
docker build ..\ --tag=$APP_IMAGE
docker images
docker -v
#docker run $APP_IMAGE flake8 --config=./deployment/flake8.cfg
echo "Running unit-tests..."
docker run $APP_IMAGE python -m unittest discover

docker pull quay.io/keboola/developer-portal-cli-v2:latest
$REPOSITORY= docker run --rm -e KBC_DEVELOPERPORTAL_USERNAME=$KBC_DEVELOPERPORTAL_USERNAME -e KBC_DEVELOPERPORTAL_PASSWORD=$KBC_DEVELOPERPORTAL_PASSWORD quay.io/keboola/developer-portal-cli-v2:latest ecr:get-repository $KBC_DEVELOPERPORTAL_VENDOR $KBC_DEVELOPERPORTAL_APP

docker tag $APP_IMAGE`:latest $REPOSITORY`:test

echo 'running login'
$(docker run --rm -e KBC_DEVELOPERPORTAL_USERNAME=$KBC_DEVELOPERPORTAL_USERNAME -e KBC_DEVELOPERPORTAL_PASSWORD=$KBC_DEVELOPERPORTAL_PASSWORD -e KBC_DEVELOPERPORTAL_URL quay.io/keboola/developer-portal-cli-v2:latest ecr:get-login $KBC_DEVELOPERPORTAL_VENDOR $KBC_DEVELOPERPORTAL_APP)

echo 'pushing test image'
docker push $REPOSITORY`:test

echo 'running test config in KBC'
docker run --rm -e KBC_STORAGE_TOKEN=$KBC_STORAGE_TOKEN quay.io/keboola/syrup-cli:latest run-job $KBC_DEVELOPERPORTAL_APP $BASE_KBC_CONFIG test
