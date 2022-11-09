pipeline {
    agent any 
    environment {
        registry = "743836443296.dkr.ecr.us-east-1.amazonaws.com/jenkins-rtls"
	  }
    stages {
        stage('Checkout') {
            steps {
               git branch: 'main', url: 'https://github.com/ronald2086/onboard.git'
               
            }
        }
	stage("verify tooling") {
      		steps {
       		 sh '''
        	  docker version
         	  docker info
         	  curl --version
         	   '''
              }
        }
        stage('Build') {
            steps{
                script {
                dockerImage = docker.build registry
                    }
                }
        }    
        stage('Pushing DOCKER Img to ECR') {
             steps{  
                script {
                     sh 'aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 743836443296.dkr.ecr.us-east-1.amazonaws.com'
                     sh 'docker push 743836443296.dkr.ecr.us-east-1.amazonaws.com/jenkins-rtls:latest'
                        }
                   }
          }
          stage('stop previous containers') {
                steps {
                 sh 'docker ps -f name=mypythonContainer -q | xargs --no-run-if-empty docker container stop'
                 sh 'docker container ls -a -fname=mypythonContainer -q | xargs -r docker container rm'
                }
            }
           stage('Docker Run') {
            steps{
             script {
              sh 'docker run -d -p 8050:8050 --rm --name mypythonContainer 743836443296.dkr.ecr.us-east-1.amazonaws.com/jenkins-rtls:latest'
               } 
            }
        }
    }
  }     
    

