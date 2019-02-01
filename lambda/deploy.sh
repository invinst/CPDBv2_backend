#!/usr/bin/env bash
set -e

deploy_lambda () {
  FUNCTION_DIR=$1
  echo "Deploying lambda function in package" $FUNCTION_DIR
  cd $FUNCTION_DIR
  . .env
  echo "Installing python packages"
  mkdir -p package
  pip3 install -r requirements.txt --target ./package > /dev/null
  cd package

  echo "Zipping"
  zip -r9 ../function.zip . > /dev/null || true
  cd ../
  zip -g ./function.zip ./lambda_function.py

  echo "Updating Lambda function"
  aws lambda update-function-code --function-name $FUNCTION_NAME$STAGING_SUFFIX --zip-file fileb://function.zip

  echo "Cleaning stuffs"
  rm ./function.zip
  rm -rf ./package
  cd ../
}


if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Update lambda function code."
    echo ""
    echo "Usage: `basename $0` {--production|--staging(default)} <command>"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ -z "$1" ]; then
    STAGING_SUFFIX=Staging
elif [ "$1" == "--production" ]; then
    STAGING_SUFFIX=''
    shift
else
    if [ "$1" == "--staging" ]; then
        shift
    fi
    STAGING_SUFFIX=Staging
fi
package=$1

cd lambda

if [ -z "$package" ]; then
  for dir in ./*/
  do
    if [[ -d $dir ]] && [[ $dir != './__pycache__/' ]]
    then
      deploy_lambda $dir
    fi
  done
else
  deploy_lambda $1
fi
